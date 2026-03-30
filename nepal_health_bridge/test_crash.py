import os
import django
import sys
import traceback

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nepal_health_bridge.settings')
django.setup()

from django.test import Client
from directory.models import HospitalAdmin, Patient, Doctor

c = Client()
print("Starting diagnostic test...")

# 1. Test Admin
admin = HospitalAdmin.objects.first()
if admin:
    session = c.session
    session["admin_id"] = admin.id
    session.save()
    try:
        response = c.get('/hospital/admin/appointments/')
        print(f"Admin Appointments OK: {response.status_code}")
    except Exception as e:
        print("\n=== ADMIN CRASH ===")
        traceback.print_exc()

# 2. Test Doctor
doc = Doctor.objects.first()
if doc:
    session = c.session
    session["doctor_id"] = doc.id
    session.save()
    try:
        response = c.get('/doctor/schedule/')
        print(f"Doctor Schedule OK: {response.status_code}")
    except Exception as e:
        print("\n=== DOCTOR CRASH ===")
        traceback.print_exc()

# 3. Test Patient
patient = Patient.objects.first()
if patient:
    session = c.session
    session["patient_id"] = patient.id
    session.save()
    try:
        response = c.get('/patient/profile/')
        print(f"Patient Profile OK: {response.status_code}")
    except Exception as e:
        print("\n=== PATIENT CRASH ===")
        traceback.print_exc()
