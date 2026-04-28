from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('ekle/', views.harcama_ekle, name='harcama_ekle'),
    path('yukle/', views.csv_yukle, name='csv_yukle'),
    path('analiz/', views.ai_analiz, name='ai_analiz'),
    path('analiz/chat/', views.ai_chat, name='ai_chat'),
    path('harcamalar/', views.harcama_listesi, name='harcama_listesi'),
    path('harcamalar/<int:pk>/sil/', views.harcama_sil, name='harcama_sil'),
    path('harcamalar/<int:pk>/duzenle/', views.harcama_duzenle, name='harcama_duzenle'),
]