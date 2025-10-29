from django.db import models

# Create your models here.
class company(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    address = models.CharField(max_length=255)
    password = models.CharField(max_length=100)
    date_joined = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.name
class shipment(models.Model):
    company = models.ForeignKey(company, on_delete=models.CASCADE)
    sender_name = models.CharField(max_length=255)
    sender_address = models.CharField(max_length=255)
    receiver_name = models.CharField(max_length=255)    
    receiver_address = models.CharField(max_length=255)
    receiver_email = models.EmailField(default="abdulla@example.com")
    weight = models.DecimalField(max_digits=6, decimal_places=2)
    distance_km = models.DecimalField(max_digits=6, decimal_places=2)
    tracking_number = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=50, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Shipment {self.tracking_number} - {self.status}"
class shipment_status(models.Model):
    shipment = models.ForeignKey(shipment, on_delete=models.CASCADE)
    status = models.CharField(max_length=50)
    location = models.CharField(max_length=255, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.shipment.tracking_number} - {self.status} at {self.updated_at}"