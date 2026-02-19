"""
URL configuration for shippingapprest project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path , include
from shipments import views_front
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('shipments.urls')),
    path('', views_front.home, name='home'),
    path('track/', views_front.track_page, name='track_page'),
    path('company/register/', views_front.company_register_page, name='company_register_page'),
    path('company/login/', views_front.company_login_page, name='company_login_page'),
    path('company/dashboard/', views_front.company_dashboard, name='company_dashboard'),
    path('company/logout/', views_front.company_logout_page, name='company_logout_page'),]
