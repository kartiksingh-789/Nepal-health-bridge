import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nepal_health_bridge.settings')
django.setup()

from directory.models import Department, Hospital

print("\n--- TARGET HOSPITALS ---")
hospitals = Hospital.objects.filter(name__icontains="Kathmandu") | Hospital.objects.filter(name__icontains="Tribhuvan") | Hospital.objects.filter(name__icontains="Teaching")
for h in hospitals:
    print(f"HOSP_ID: {h.id} -> '{h.name}'")

print("\n--- TARGET DEPARTMENTS ---")
departments = Department.objects.filter(hospital__in=hospitals)
for d in departments:
    print(f"DEPT_ID: {d.id} -> '{d.name}' (HOSP: '{d.hospital.name}', HOSP_ID: {d.hospital.id})")
