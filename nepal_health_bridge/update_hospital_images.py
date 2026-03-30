import os
import sys
import django

sys.path.append(r"c:\Users\KIIT0001\Desktop\mini proj\Nepal-health-bridge-master\nepal_health_bridge")
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nepal_health_bridge.settings')
django.setup()

from directory.models import Hospital

# A set of beautiful UNsplash hospital / medical building / hallway pictures
images = [
    "https://images.unsplash.com/photo-1586773860418-d37222d8fce3?auto=format&fit=crop&w=800&q=80",  # Modern exterior
    "https://images.unsplash.com/photo-1519494026892-80bbd2d6fd0d?auto=format&fit=crop&w=800&q=80",  # Clean hallway
    "https://images.unsplash.com/photo-1504813184591-01572f98c85f?auto=format&fit=crop&w=800&q=80",  # Reception/Lobby
    "https://images.unsplash.com/photo-1516549655169-df83a0774514?auto=format&fit=crop&w=800&q=80",  # Equipment
    "https://images.unsplash.com/photo-1551076805-e1869033e561?auto=format&fit=crop&w=800&q=80",  # waiting area
    "https://images.unsplash.com/photo-1579684385127-1ef15d508118?auto=format&fit=crop&w=800&q=80",  # Beds
    "https://images.unsplash.com/photo-1512678080530-7760d81faba6?auto=format&fit=crop&w=800&q=80",  # Clinic
    "https://images.unsplash.com/photo-1513224502586-d1e602410265?auto=format&fit=crop&w=800&q=80",  # Checkup room
    "https://images.unsplash.com/photo-1631217868264-e5b90bb7e133?auto=format&fit=crop&w=800&q=80",  # MRI Machine
    "https://images.unsplash.com/photo-1538108149393-fbbd814ec73e?auto=format&fit=crop&w=800&q=80",  # Operating theater
]

hospitals = Hospital.objects.all().order_by('name')

print("Applying new images...")
for i, hospital in enumerate(hospitals):
    hospital.image_url = images[i % len(images)]
    hospital.save()
    
print("All hospitals updated successfully!")
