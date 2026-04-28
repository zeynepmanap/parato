from django.db import models

# Create your models here.

from django.db import models
from django.contrib.auth.models import User

class Kategori(models.TextChoices):
    MARKET = 'market', 'Market'
    ULASIM = 'ulasim', 'Ulaşım'
    SAGLIK = 'saglik', 'Sağlık'
    EGLENCE = 'eglence', 'Eğlence'
    FATURA = 'fatura', 'Fatura'
    YEMEK = 'yemek', 'Yemek'
    DIGER = 'diger', 'Diğer'

class Harcama(models.Model):
    kullanici = models.ForeignKey(User, on_delete=models.CASCADE)
    baslik = models.CharField(max_length=200)
    tutar = models.DecimalField(max_digits=10, decimal_places=2)
    kategori = models.CharField(max_length=20, choices=Kategori.choices, default=Kategori.DIGER)
    tarih = models.DateField()
    aciklama = models.TextField(blank=True)
    olusturulma = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-tarih']

    def __str__(self):
        return f"{self.baslik} - {self.tutar}₺"