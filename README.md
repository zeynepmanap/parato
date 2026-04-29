# 💰 Parato — AI Destekli Kişisel Finans Takip Uygulaması

Parato, kullanıcıların harcamalarını takip etmesini, analiz etmesini ve yerel LLM (Llama3) destekli AI koç ile kişiselleştirilmiş tasarruf önerileri almasını sağlayan bir web uygulamasıdır.

## 🖼️ Ekran Görüntüleri

![Dashboard](screenshots/Ekran%20Resmi%202026-04-28%2023.26.08.png)

## 🚀 Özellikler

- 📊 Kategori bazlı harcama takibi ve interaktif grafikler
- 🤖 Llama3 ile AI destekli harcama analizi ve tasarruf önerileri
- 💬 Finans koçuyla gerçek zamanlı sohbet
- 📂 CSV / banka ekstresi içe aktarma
- 📅 Geçmiş aylara göre filtreleme
- 🔐 Kullanıcı kayıt ve giriş sistemi

## 🛠️ Teknoloji Stack

- **Backend:** Python, Django 6.0
- **AI/LLM:** Ollama + Llama3 (yerel, internet gerektirmez)
- **Veri İşleme:** Pandas
- **Frontend:** HTML, CSS, Chart.js
- **Veritabanı:** SQLite

## ⚙️ Kurulum

### Gereksinimler
- Python 3.12+
- [Ollama](https://ollama.com) kurulu ve `llama3` modeli indirilmiş olmalı

### Adımlar

```bash
# Repoyu klonla
git clone https://github.com/zeynepmanap/parato.git
cd parato

# Virtual environment oluştur
python3 -m venv venv
source venv/bin/activate

# Bağımlılıkları yükle
pip install django pandas ollama python-dotenv reportlab

# Veritabanını oluştur
python manage.py migrate

# Süper kullanıcı oluştur
python manage.py createsuperuser

# Sunucuyu başlat
python manage.py runserver
```

Tarayıcıda `http://127.0.0.1:8000` adresini aç.

### Ollama Kurulumu
```bash
# Ollama'yı başlat
ollama serve

# Llama3 modelini indir
ollama pull llama3
```

## 📁 Proje Yapısı
parato/
├── accounts/          # Kullanıcı giriş/kayıt
├── tracker/           # Ana uygulama
│   ├── models.py      # Harcama modeli
│   ├── views.py       # Tüm view'lar + AI entegrasyonu
│   ├── urls.py        # URL yapısı
│   └── templates/     # HTML şablonları
├── config/            # Django ayarları
└── manage.py

## Geliştirici

-Zeynep Manap
