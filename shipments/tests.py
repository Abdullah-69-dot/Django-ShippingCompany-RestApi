from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from .models import Company, Shipment, ShipmentStatus
from unittest.mock import patch

class CompanyTests(APITestCase):
    def setUp(self):
        self.register_url = reverse('company-register')
        self.login_url = reverse('company-login')
        self.company_data = {
            'name': 'Test Company',
            'email': 'test@example.com',
            'phone': '1234567890',
            'address': 'Test Address',
            'password': 'password123'
        }

    def test_company_registration(self):
        response = self.client.post(self.register_url, self.company_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Company.objects.count(), 1)
        self.assertEqual(Company.objects.get().email, 'test@example.com')

    def test_company_registration_invalid_data(self):
        data = self.company_data.copy()
        data['email'] = ''  # Invalid email
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_company_login(self):
        # Register first
        self.client.post(self.register_url, self.company_data, format='json')
        
        # Login
        data = {
            'email': self.company_data['email'],
            'password': self.company_data['password']
        }
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data['tokens'])

class ShipmentTests(APITestCase):
    def setUp(self):
        self.create_url = reverse('create-shipment')
        self.list_url = reverse('company-shipments')
        
        # Create company
        self.company = Company.objects.create(
            name='Test Company',
            email='test@example.com',
            phone='1234567890',
            address='Test Address',
            password='password123'  # Note: In real app, use make_password or serializer save
        )
        self.company.save() # Triggers hash if using model save
        
        # Authenticate (simulate session based auth used in views)
        session = self.client.session
        session['company_id'] = self.company.id
        session.save()
        
        self.shipment_data = {
            'sender_name': 'Sender',
            'sender_address': 'Sender Addr',
            'sender_lat': 30.0,
            'sender_lng': 31.0,
            'receiver_name': 'Receiver',
            'receiver_address': 'Receiver Addr',
            'receiver_email': 'receiver@example.com',
            'receiver_lat': 30.1,
            'receiver_lng': 31.1,
            'weight': 10.0,
            'distance_km': 100.0
        }

    @patch('shipments.views.send_mail')
    def test_create_shipment(self, mock_send_mail):
        response = self.client.post(self.create_url, self.shipment_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Shipment.objects.count(), 1)
        self.assertEqual(ShipmentStatus.objects.count(), 1) # Initial status
        
        # Check pricing calculation
        # Base 50 + (10 * 10) + (100 * 2) = 50 + 100 + 200 = 350
        self.assertEqual(float(response.data['price']), 350.0)

    def test_list_shipments(self):
        # Create a shipment first
        with patch('shipments.views.send_mail'):
            self.client.post(self.create_url, self.shipment_data, format='json')
            
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_update_shipment_status(self):
        # Create shipment
        with patch('shipments.views.send_mail'):
            resp = self.client.post(self.create_url, self.shipment_data, format='json')
            shipment_id = resp.data['shipment']['id']
            
        update_url = reverse('update-shipment-status', args=[shipment_id])
        data = {
            'status': 'in_transit',
            'location': 'New Location',
            'latitude': 30.2,
            'longitude': 31.2
        }
        
        response = self.client.post(update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['shipment']['status'], 'in_transit')
        
        # Verify status history
        self.assertEqual(ShipmentStatus.objects.filter(shipment_id=shipment_id).count(), 2)

    def test_track_shipment(self):
        # Create shipment
        with patch('shipments.views.send_mail'):
            resp = self.client.post(self.create_url, self.shipment_data, format='json')
            tracking_number = resp.data['tracking_number']
            
        track_url = reverse('track-shipment', args=[tracking_number])
        response = self.client.get(track_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['tracking_number'], tracking_number)
