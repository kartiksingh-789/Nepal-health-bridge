import os, django, sys

sys.path.append(r"c:\Users\KIIT0001\Desktop\mini proj\Nepal-health-bridge-master\nepal_health_bridge")
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nepal_health_bridge.settings')
django.setup()

from directory.models import Hospital

image_map = {
    "Gandaki Medical College": "https://images.unsplash.com/photo-1586773860418-d37222d8fce3?auto=format&fit=crop&w=800&q=80",
    "Karnali Provincial Hospital": "https://images.unsplash.com/photo-1530497610245-94d3c16cda28?auto=format&fit=crop&w=800&q=80",
    "Kathmandu Central Hospital": "https://images.unsplash.com/photo-1638202993928-7267aad84c31?auto=format&fit=crop&w=800&q=80",
    "Koshi Hospital": "https://images.unsplash.com/photo-1587351021759-3e566b6af7e4?auto=format&fit=crop&w=800&q=80",
    "Manipal Teaching Hospital": "https://images.unsplash.com/photo-1519494026892-80bbd2d6fd0d?auto=format&fit=crop&w=800&q=80",
    "National Medical College": "https://images.unsplash.com/photo-1502740479091-6387fe5cead3?auto=format&fit=crop&w=800&q=80",
    "Nepal Mediciti": "https://images.unsplash.com/photo-1542884748-2b87b36c6b90?auto=format&fit=crop&w=800&q=80",
    "Nobel Medical College": "https://images.unsplash.com/photo-1512678080530-7760d81faba6?auto=format&fit=crop&w=800&q=80",
    "Patan Life Care": "https://images.unsplash.com/photo-1551884170-09fb70a3a2ed?auto=format&fit=crop&w=800&q=80",
    "Tribhuvan University Teaching Hospital": "https://images.unsplash.com/photo-1622253694242-2b2890fbdbf8?auto=format&fit=crop&w=800&q=80"
}

# Generic fallbacks
fallbacks = [
    "https://images.unsplash.com/photo-1516549655169-df83a0774514?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1551076805-e1869033e561?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1504813184591-01572f98c85f?auto=format&fit=crop&w=800&q=80"
]

hospitals = Hospital.objects.all()
for i, h in enumerate(hospitals):
    matched = False
    for map_key, img_url in image_map.items():
        if map_key in h.name:
            h.image_url = img_url
            h.save()
            matched = True
            break
    if not matched:
        h.image_url = fallbacks[i % len(fallbacks)]
        h.save()

print("All hospitals have been successfully updated with realistic and varied high-quality images.")
