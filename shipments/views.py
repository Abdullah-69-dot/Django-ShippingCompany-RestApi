from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.core.mail import send_mail
from django.conf import settings
from .models import Shipment, Company, ShipmentStatus
from .serializers import (
    ShipmentSerializer, CompanySerializer, CompanyLoginSerializer,
    ShipmentCreateSerializer, ShipmentTrackSerializer, ShipmentStatusSerializer
)
import random
import string

# Generate random tracking number
def generate_tracking_number():
    return 'TRK' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))

# ============= Company Registration & Login =============

@api_view(['POST'])
def company_register(request):
    """Register a new company"""
    serializer = CompanySerializer(data=request.data)
    if serializer.is_valid():
        company = serializer.save()
        # Store company ID in session
        request.session['company_id'] = company.id
        return Response({
            'message': 'Company registered successfully',
            'company': CompanySerializer(company).data
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def company_login(request):
    """Company login"""
    serializer = CompanyLoginSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        
        try:
            company = Company.objects.get(email=email)
            if company.check_password(password):
                # Store company ID in session
                request.session['company_id'] = company.id
                return Response({
                    'message': 'Login successful',
                    'company': CompanySerializer(company).data
                }, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        except Company.DoesNotExist:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def company_logout(request):
    """Company logout"""
    request.session.flush()
    return Response({'message': 'Logged out successfully'}, status=status.HTTP_200_OK)

# ============= Shipment Management =============

@api_view(['POST'])
def create_shipment(request):
    """Company creates a new shipment"""
    # Check if company is logged in
    company_id = request.session.get('company_id')
    if not company_id:
        return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
    
    try:
        company = Company.objects.get(id=company_id)
    except Company.DoesNotExist:
        return Response({'error': 'Company not found'}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = ShipmentCreateSerializer(data=request.data)
    
    if serializer.is_valid():
        # Generate tracking number
        tracking_number = generate_tracking_number()
        
        # Create shipment
        shipment = serializer.save(
            company=company,
            tracking_number=tracking_number,
            status='pending'
        )
        
        # Create initial status entry
        ShipmentStatus.objects.create(
            shipment=shipment,
            status='pending',
            location=shipment.sender_address,
            latitude=shipment.sender_lat,
            longitude=shipment.sender_lng,
            notes='Shipment created'
        )
        
        # Send email to receiver
        receiver_email = serializer.validated_data.get('receiver_email')
        if receiver_email:
            subject = 'Your Shipment Tracking Number'
            message = f"""
Dear {serializer.validated_data.get('receiver_name')},

Your shipment has been created successfully by {company.name}.

Tracking Number: {tracking_number}

You can track your shipment at any time using this number.

Shipment Details:
- From: {serializer.validated_data.get('sender_name')}
- Weight: {serializer.validated_data.get('weight')} kg

Thank you for using our service!

Best regards,
{company.name}
            """
            try:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [receiver_email],
                    fail_silently=False,
                )
            except Exception as e:
                print(f"Email sending failed: {e}")
        
        return Response({
            'message': 'Shipment created successfully',
            'tracking_number': tracking_number,
            'shipment': ShipmentSerializer(shipment).data
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def company_shipments(request):
    """Get all shipments for logged-in company"""
    company_id = request.session.get('company_id')
    if not company_id:
        return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
    
    shipments = Shipment.objects.filter(company_id=company_id).order_by('-created_at')
    serializer = ShipmentSerializer(shipments, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['POST'])
def update_shipment_status(request, shipment_id):
    """Company updates shipment status with location"""
    company_id = request.session.get('company_id')
    if not company_id:
        return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
    
    try:
        shipment = Shipment.objects.get(id=shipment_id, company_id=company_id)
    except Shipment.DoesNotExist:
        return Response({'error': 'Shipment not found'}, status=status.HTTP_404_NOT_FOUND)
    
    new_status = request.data.get('status')
    location = request.data.get('location')
    latitude = request.data.get('latitude')
    longitude = request.data.get('longitude')
    notes = request.data.get('notes', '')
    
    if not new_status:
        return Response({'error': 'Status is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Update shipment status
    shipment.status = new_status
    shipment.save()
    
    # Create status history entry
    ShipmentStatus.objects.create(
        shipment=shipment,
        status=new_status,
        location=location,
        latitude=latitude,
        longitude=longitude,
        notes=notes
    )
    
    return Response({
        'message': 'Status updated successfully',
        'shipment': ShipmentSerializer(shipment).data
    }, status=status.HTTP_200_OK)

# ============= Public Tracking =============

@api_view(['GET'])
def track_shipment(request, tracking_number):
    """Public endpoint - Track shipment by tracking number"""
    try:
        shipment = Shipment.objects.get(tracking_number=tracking_number)
        serializer = ShipmentTrackSerializer(shipment)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Shipment.DoesNotExist:
        return Response({'error': 'Shipment not found'}, status=status.HTTP_404_NOT_FOUND)