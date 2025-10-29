from django.urls import path
from .views import (
    company_register, company_login, company_logout,
    create_shipment, company_shipments, update_shipment_status,
    track_shipment
)

urlpatterns = [
    # Company Authentication
    path('company/register/', company_register, name='company-register'),
    path('company/login/', company_login, name='company-login'),
    path('company/logout/', company_logout, name='company-logout'),
    
    # Company Shipment Management
    path('shipments/create/', create_shipment, name='create-shipment'),
    path('shipments/', company_shipments, name='company-shipments'),
    path('shipments/<int:shipment_id>/update-status/', update_shipment_status, name='update-shipment-status'),
    
    # Public Tracking
    path('track/<str:tracking_number>/', track_shipment, name='track-shipment'),
]