from django.db import models
from django.contrib.auth.hashers import make_password, check_password

class Company(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    address = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    date_joined = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        # Hash password before saving
        if not self.pk or 'pbkdf2_sha256' not in self.password:
            self.password = make_password(self.password)
        super().save(*args, **kwargs)
    
    def check_password(self, raw_password):
        return check_password(raw_password, self.password)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Companies"


class Shipment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('picked_up', 'Picked Up'),
        ('in_transit', 'In Transit'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='shipments')
    sender_name = models.CharField(max_length=255)
    sender_address = models.CharField(max_length=255)
    sender_lat = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    sender_lng = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    
    receiver_name = models.CharField(max_length=255)    
    receiver_address = models.CharField(max_length=255)
    receiver_email = models.EmailField()
    receiver_lat = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    receiver_lng = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    
    weight = models.DecimalField(max_digits=6, decimal_places=2)
    distance_km = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    tracking_number = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Shipment {self.tracking_number} - {self.status}"


class ShipmentStatus(models.Model):
    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE, related_name='status_history')
    status = models.CharField(max_length=50)
    location = models.CharField(max_length=255, blank=True, null=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.shipment.tracking_number} - {self.status} at {self.updated_at}"
    
    class Meta:
        verbose_name_plural = "Shipment Statuses"
        ordering = ['-updated_at']