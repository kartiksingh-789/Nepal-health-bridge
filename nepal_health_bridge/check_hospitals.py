import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nepal_health_bridge.settings')
django.setup()

from directory.models import Hospital

print("\n--- SPECIFIC HOSPITALS ---")
for h_id in [2, 6, 8, 9, 10]:
    try:
        h = Hospital.objects.get(id=h_id)
        print(f"HOSP_ID: {h.id} -> '{h.name}'")
    except Hospital.DoesNotExist:
        print(f"HOSP_ID: {h_id} NOT FOUND")
