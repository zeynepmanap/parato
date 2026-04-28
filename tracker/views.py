from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import json
import re
from .models import Harcama
from datetime import date


def markdown_temizle(metin):
    metin = re.sub(r'\*\*(.*?)\*\*', r'\1', metin)
    metin = re.sub(r'\*(.*?)\*', r'\1', metin)
    metin = re.sub(r'^#+\s+', '', metin, flags=re.MULTILINE)
    metin = re.sub(r'^\*\s+', '', metin, flags=re.MULTILINE)
    metin = re.sub(r'^\-\s+', '', metin, flags=re.MULTILINE)
    return metin.strip()


@login_required
def dashboard(request):
    bugun = date.today()
    ay = int(request.GET.get('ay', bugun.month))
    yil = int(request.GET.get('yil', bugun.year))

    harcamalar = Harcama.objects.filter(
        kullanici=request.user,
        tarih__month=ay,
        tarih__year=yil
    )
    toplam = sum(h.tutar for h in harcamalar)

    kategoriler = {}
    for h in harcamalar:
        kategoriler[h.kategori] = kategoriler.get(h.kategori, 0) + h.tutar

    en_cok = max(kategoriler, key=kategoriler.get) if kategoriler else '-'

    ay_isimleri = {
        1: 'Ocak', 2: 'Şubat', 3: 'Mart', 4: 'Nisan',
        5: 'Mayıs', 6: 'Haziran', 7: 'Temmuz', 8: 'Ağustos',
        9: 'Eylül', 10: 'Ekim', 11: 'Kasım', 12: 'Aralık'
    }

    kat_isimleri = {
        'market': 'Market', 'ulasim': 'Ulaşım', 'saglik': 'Sağlık',
        'eglence': 'Eğlence', 'fatura': 'Fatura', 'yemek': 'Yemek', 'diger': 'Diğer'
    }

    grafik_etiketler = json.dumps([kat_isimleri.get(k, k) for k in kategoriler.keys()])
    grafik_degerler = json.dumps([float(v) for v in kategoriler.values()])

    aylar = []
    for i in range(12):
        m = bugun.month - i
        y = bugun.year
        if m <= 0:
            m += 12
            y -= 1
        aylar.append({'ay': m, 'yil': y})

    context = {
        'toplam': toplam,
        'islem_sayisi': harcamalar.count(),
        'en_cok': en_cok,
        'harcamalar': harcamalar[:5],
        'secili_ay': ay,
        'secili_yil': yil,
        'aylar': aylar,
        'ay_isimleri': ay_isimleri,
        'secili_ay_ismi': ay_isimleri[ay],
        'grafik_etiketler': grafik_etiketler,
        'grafik_degerler': grafik_degerler,
    }
    return render(request, 'tracker/dashboard.html', context)


@login_required
def harcama_ekle(request):
    if request.method == 'POST':
        Harcama.objects.create(
            kullanici=request.user,
            baslik=request.POST['baslik'],
            tutar=request.POST['tutar'],
            kategori=request.POST['kategori'],
            tarih=request.POST['tarih'],
            aciklama=request.POST.get('aciklama', '')
        )
        messages.success(request, 'Harcama başarıyla kaydedildi!')
        return redirect('dashboard')
    return render(request, 'tracker/harcama_ekle.html')


@login_required
def csv_yukle(request):
    if request.method == 'POST' and request.FILES.get('csv_dosya'):
        import csv
        import io

        dosya = request.FILES['csv_dosya']
        decoded = dosya.read().decode('utf-8')
        reader = csv.DictReader(io.StringIO(decoded))

        eklenen = 0
        hatalar = []

        for i, row in enumerate(reader, start=2):
            try:
                Harcama.objects.create(
                    kullanici=request.user,
                    baslik=row['baslik'].strip(),
                    tutar=float(row['tutar'].replace(',', '.')),
                    kategori=row.get('kategori', 'diger').strip().lower(),
                    tarih=row['tarih'].strip(),
                    aciklama=row.get('aciklama', '').strip()
                )
                eklenen += 1
            except Exception as e:
                hatalar.append(f"Satır {i}: {e}")

        if hatalar:
            messages.warning(request, f"{eklenen} kayıt eklendi. {len(hatalar)} hata: {hatalar[0]}")
        else:
            messages.success(request, f"{eklenen} harcama başarıyla içe aktarıldı!")

        return redirect('dashboard')

    return render(request, 'tracker/csv_yukle.html')


@login_required
def harcama_listesi(request):
    harcamalar = Harcama.objects.filter(kullanici=request.user).order_by('-tarih')
    context = {'harcamalar': harcamalar}
    return render(request, 'tracker/harcama_listesi.html', context)


@login_required
def harcama_sil(request, pk):
    harcama = Harcama.objects.get(pk=pk, kullanici=request.user)
    harcama.delete()
    messages.success(request, 'Harcama silindi.')
    return redirect('harcama_listesi')


@login_required
def harcama_duzenle(request, pk):
    harcama = Harcama.objects.get(pk=pk, kullanici=request.user)
    if request.method == 'POST':
        harcama.baslik = request.POST['baslik']
        harcama.tutar = request.POST['tutar']
        harcama.kategori = request.POST['kategori']
        harcama.tarih = request.POST['tarih']
        harcama.aciklama = request.POST.get('aciklama', '')
        harcama.save()
        messages.success(request, 'Harcama güncellendi.')
        return redirect('harcama_listesi')
    return render(request, 'tracker/harcama_duzenle.html', {'harcama': harcama})


def _harcama_ozeti(kullanici):
    harcamalar = Harcama.objects.filter(
        kullanici=kullanici,
        tarih__month=date.today().month,
        tarih__year=date.today().year
    )
    if not harcamalar:
        return None
    return "\n".join([
        f"- {h.baslik}: {h.tutar}₺ ({h.get_kategori_display()}, {h.tarih})"
        for h in harcamalar
    ])


@login_required
def ai_analiz(request):
    analiz = None
    analiz_satirlar = []

    if request.method == 'POST':
        import ollama

        harcama_listesi_str = _harcama_ozeti(request.user)

        if not harcama_listesi_str:
            analiz = "Bu ay henüz harcama kaydı yok. Önce harcama eklemen gerekiyor."
            analiz_satirlar = [analiz]
        else:
            prompt = f"""Sen Parato'nun baş finans analistisin. 10 yıllık deneyimli bir portföy yöneticisi gibi konuş.

Harcama verileri:
{harcama_listesi_str}

Aşağıdaki başlıkları kullan, her bölümü detaylı ve eksiksiz yaz:

GENEL DURUM
Finansal tablonun genel değerlendirmesi. Sağlıklı mı, riskli mi?

---
KATEGORİ ANALİZİ
Her kategori bütçenin yüzde kaçı? Türkiye koşullarında makul mü?

---
KATEGORİ BAZLI HARCAMA DAĞILIMI
Tüm kategorileri listele, her birinin toplam içindeki payını yüzde olarak göster.

---
FAZLA HARCANAN ALANLAR
Hangi kategorilerde limit aşıldı? Somut rakamlarla göster.

---
TASARRUF ÖNERİLERİ
5 öneri. Her biri için: ne değişmeli, aylık tahmini tasarruf miktarı, nasıl uygulanır adım adım.

---
GELECEK AY BÜTÇE TAHMİNİ
Bu verilere göre gelecek ay için kategori bazlı bütçe öner. Rakamsal olsun.

---
RİSK VE ÖZET SKOR
6 ay sonraki risk değerlendirmesi, finansal sağlık skoru 10 üzerinden, en kritik tek değişiklik.

Sadece Türkçe yaz. Kesinlikle markdown, tablo veya ** işareti kullanma. Düz metin yaz."""

            try:
                response = ollama.chat(
                    model='llama3',
                    messages=[{'role': 'user', 'content': prompt}],
                    options={'temperature': 0.3}
                )
                analiz = markdown_temizle(response['message']['content'])
            except Exception as e:
                analiz = f"Analiz sırasında hata oluştu: {str(e)}"

            analiz_satirlar = analiz.split('\n')

    return render(request, 'tracker/ai_analiz.html', {
        'analiz': analiz,
        'analiz_satirlar': analiz_satirlar
    })


@login_required
def ai_chat(request):
    if request.method == 'POST':
        import ollama

        data = json.loads(request.body)
        mesajlar = data.get('mesajlar', [])
        harcama_listesi_str = _harcama_ozeti(request.user)

        sistem = f"""Sen Parato'nun AI finans koçusun. Kullanıcının bu ayki harcama verileri:

{harcama_listesi_str or 'Henüz harcama verisi yok.'}

Bu verilere dayanarak kullanıcının sorularını yanıtla. Sadece Türkçe konuş. Kısa ve net ol. Kesinlikle markdown, ** işareti, * işareti veya - liste işareti kullanma. Düz paragraf halinde yaz."""

        ollama_mesajlar = [{'role': 'system', 'content': sistem}] + mesajlar

        try:
            response = ollama.chat(
                model='llama3',
                messages=ollama_mesajlar,
                options={'temperature': 0.5}
            )
            cevap = markdown_temizle(response['message']['content'])
        except Exception as e:
            cevap = f"Hata: {str(e)}"

        return JsonResponse({'cevap': cevap})

    return JsonResponse({'hata': 'Geçersiz istek'}, status=400)