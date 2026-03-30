import os, django, sys
import io

sys.path.append(r"c:\Users\KIIT0001\Desktop\mini proj\Nepal-health-bridge-master\nepal_health_bridge")
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nepal_health_bridge.settings')
django.setup()

from directory.models import HospitalAdmin
from django.contrib.auth.models import User

with io.open('out_admins_utf8.txt', 'w', encoding='utf-8') as fh:
    fh.write("--- Hospital Admins ---\n")
    for a in HospitalAdmin.objects.all():
        fh.write(f"Username: {a.username} | Hospital: {a.hospital.name if a.hospital else 'None'}\n")

    fh.write("\n--- Django Superusers ---\n")
    for u in User.objects.all():
        fh.write(f"Username: {u.username} | is_superuser: {u.is_superuser}\n")

