import os, django, sys

sys.path.append(r"c:\Users\KIIT0001\Desktop\mini proj\Nepal-health-bridge-master\nepal_health_bridge")
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nepal_health_bridge.settings')
django.setup()

from directory.models import HospitalAdmin
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password

print("Reseting passwords to 'admin123'...")

# Reset Django Admin
user = User.objects.filter(username="soumesh").first()
if user:
    user.set_password("admin123")
    user.save()
    print("Django superuser 'soumesh' password reset.")

# Reset a Hospital Admin
h_admin = HospitalAdmin.objects.filter(username="soumeshpan_2005").first()
if h_admin:
    h_admin.password = make_password("admin123")
    h_admin.save()
    print("Hospital Admin 'soumeshpan_2005' password reset.")

