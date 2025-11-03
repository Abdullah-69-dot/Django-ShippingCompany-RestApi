from rest_framework import serializers
from .models import Shipment, Company, ShipmentStatus

class CompanySerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    
    class Meta:
        model = Company
        fields = ['id', 'name', 'email', 'phone', 'address', 'password', 'date_joined']
        read_only_fields = ['id', 'date_joined']
        extra_kwargs = {
            'password': {'write_only': True}
        }

class CompanyLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(style={'input_type': 'password'})

class ShipmentStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShipmentStatus
        fields = '__all__'
        read_only_fields = ['updated_at']

class ShipmentSerializer(serializers.ModelSerializer):
    status_history = ShipmentStatusSerializer(many=True, read_only=True)
    company_name = serializers.CharField(source='company.name', read_only=True)
    
    class Meta:
        model = Shipment
        fields = '__all__'
        read_only_fields = ['id', 'tracking_number', 'created_at', 'updated_at']

class ShipmentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shipment
        fields = [
            'sender_name', 'sender_address', 'sender_lat', 'sender_lng',
            'receiver_name', 'receiver_address', 'receiver_email', 
            'receiver_lat', 'receiver_lng',
            'weight', 'distance_km', 'price'
        ]

class ShipmentTrackSerializer(serializers.ModelSerializer):
    status_history = ShipmentStatusSerializer(many=True, read_only=True)
    company_name = serializers.CharField(source='company.name', read_only=True)
    company_phone = serializers.CharField(source='company.phone', read_only=True)
    
    class Meta:
        model = Shipment
        fields = [
            'id', 'tracking_number', 'status', 
            'sender_name', 'sender_address', 'sender_lat', 'sender_lng',
            'receiver_name', 'receiver_address', 'receiver_lat', 'receiver_lng',
            'weight', 'distance_km', 'created_at', 'updated_at',
            'company_name', 'company_phone', 'status_history'
        ]