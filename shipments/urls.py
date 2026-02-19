from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    company_register, company_login, company_logout,
    create_shipment, company_shipments, update_shipment_status,
    track_shipment , 
)

urlpatterns = [
    path('company/register/', company_register, name='company-register'),
    path('company/login/', company_login, name='company-login'),
    path('company/logout/', company_logout, name='company-logout'),
    
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    
    path('shipments/create/', create_shipment, name='create-shipment'),
    path('shipments/', company_shipments, name='company-shipments'),
    path('shipments/<int:shipment_id>/update-status/', update_shipment_status, name='update-shipment-status'),
    
    path('track/<str:tracking_number>/', track_shipment, name='track-shipment'),
]