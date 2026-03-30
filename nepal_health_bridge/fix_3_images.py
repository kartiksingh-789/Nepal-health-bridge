import os, django, sys

sys.path.append(r"c:\Users\KIIT0001\Desktop\mini proj\Nepal-health-bridge-master\nepal_health_bridge")
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nepal_health_bridge.settings')
django.setup()

from directory.models import Hospital

image_map = {
    "Koshi Hospital": "https://images.unsplash.com/photo-1586773860418-d37222d8fce3?auto=format&fit=crop&w=800&q=80",  # Modern exterior
    "National Medical College": "https://images.unsplash.com/photo-1551076805-e1869033e561?auto=format&fit=crop&w=800&q=80", # Waiting area
    "Tribhuvan University Teaching Hospital": "https://images.unsplash.com/photo-1516549655169-df83a0774514?auto=format&fit=crop&w=800&q=80" # Equipment / interior
}

hospitals = Hospital.objects.all()
for h in hospitals:
    for map_key, img_url in image_map.items():
        if map_key in h.name:
            h.image_url = img_url
            h.save()
            print(f"Updated {h.name} image.")

print("Fixed the 3 missing hospitals with known working images!")
