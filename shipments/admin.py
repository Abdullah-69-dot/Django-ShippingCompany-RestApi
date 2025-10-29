from django.contrib import admin

# Register your modelsfrom django.contrib import admin
from .models import Company, Shipment, ShipmentStatus

admin.site.register(Company)
admin.site.register(Shipment)
admin.site.register(ShipmentStatus)