# Shipment Management System

A comprehensive web-based shipment tracking and management system built with Django REST Framework. Features real-time tracking, interactive maps with reverse geocoding, automatic price calculation, and JWT authentication.

## Features

### For Companies
- Create and manage shipments with detailed tracking
- Interactive maps with location picker and reverse geocoding
- Automatic distance calculation between sender and receiver
- Real-time shipment status updates
- Automatic price calculation: 50 + (weight × 10) + (distance × 2)
- Email notifications to customers with tracking details

### For Customers
- Track shipments using tracking number
- View complete shipment history and timeline
- Interactive map showing shipment route
- Receive tracking information via email

## Tech Stack

**Backend:**
- Django 4.2.7
- Django REST Framework 3.14.0
- Simple JWT 5.3.0
- PostgreSQL/SQLite

**Frontend:**
- Bootstrap 5.3 RTL
- Leaflet.js 1.9.4
- Axios 1.4.0
- Vanilla JavaScript

**External Services:**
- OpenStreetMap for maps
- Nominatim API for geocoding
- Gmail SMTP for email notifications

## Installation

```bash
# Clone repository
git clone https://github.com/yourusername/shipment-management-system.git
cd shipment-management-system

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup database
python manage.py makemigrations
python manage.py migrate

# Configure email settings in .env
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=your-email@gmail.com

# Run server
python manage.py runserver
```

Visit http://127.0.0.1:8000/

## API Endpoints

### Authentication
- `POST /api/company/register/` - Register new company
- `POST /api/company/login/` - Company login
- `POST /api/token/refresh/` - Refresh JWT token

### Shipments (Requires Auth)
- `POST /api/shipments/create/` - Create new shipment
- `GET /api/shipments/` - List company shipments
- `POST /api/shipments/<id>/update-status/` - Update shipment status

### Public
- `GET /api/track/<tracking_number>/` - Track shipment

## Usage

### For Companies
1. Register/Login at `/company/register/` or `/company/login/`
2. Access dashboard at `/company/dashboard/`
3. Click "Add New Shipment"
4. Use map picker to select sender/receiver locations
5. Enter weight (price calculated automatically)
6. Save shipment (customer receives email with tracking number)

### For Customers
1. Visit `/track/`
2. Enter tracking number from email
3. View shipment details, map, and status history

## Project Structure

```
shipment-management-system/
├── manage.py
├── requirements.txt
├── project/
│   ├── settings.py
│   └── urls.py
├── shipment/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   └── templates/
└── .env
```

## Database Models

**Company:** id, name, email, phone, address, password, date_joined

**Shipment:** id, company, sender/receiver details, coordinates, weight, distance, price, tracking_number, status, timestamps

**ShipmentStatus:** id, shipment, status, location, coordinates, notes, updated_at

## Configuration

### Email Setup (Gmail)
1. Go to https://myaccount.google.com/security
2. Enable 2-Step Verification
3. Generate App Password
4. Add to `.env` file

### JWT Settings
Token lifetime: 1 day (access), 7 days (refresh)


## License

MIT License - Copyright (c) 2025

## Contributing

Pull requests are welcome. For major changes, please open an issue first.
