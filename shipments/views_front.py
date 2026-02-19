from django.shortcuts import render, redirect
from django.contrib import messages

# Home Page
def home(request):
    return render(request, 'shipments/home.html')

# Track Shipment Page
def track_page(request):
    return render(request, 'shipments/track_shipment.html')

# Company Registration Page
def company_register_page(request):
    if request.session.get('company_id'):
        return redirect('company_dashboard')
    return render(request, 'shipments/company_register.html')

# Company Login Page
def company_login_page(request):
    if request.session.get('company_id'):
        return redirect('company_dashboard')
    return render(request, 'shipments/company_login.html')

# Company Dashboard
def company_dashboard(request):
    if not request.session.get('company_id'):
        messages.error(request, 'يجب تسجيل الدخول أولاً')
        return redirect('company_login_page')
    return render(request, 'shipments/company_dashboard.html')

# Company Logout
def company_logout_page(request):
    request.session.flush()
    messages.success(request, 'تم تسجيل الخروج بنجاح')
    return redirect('home')