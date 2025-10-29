from django.urls import path
from . import views   # ✅ استيراد views من نفس التطبيق

urlpatterns = [
    path('', views.home, name='home'),  # مؤقتًا هنحط صفحة تجريبية
]
