"""
Management command to seed the pharmacy with realistic data.
Run:  python manage.py seed_pharmacy
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from pharmacy.models import Category, Product, Coupon


class Command(BaseCommand):
    help = 'Seeds pharmacy Categories, Products, and Coupons'

    def handle(self, *args, **options):
        self.stdout.write('🌱 Seeding pharmacy data …')

        # ─── CATEGORIES ──────────────────────────
        categories_data = [
            {'name': 'Pain Relief',          'slug': 'pain-relief',          'icon': 'fa-solid fa-head-side-virus'},
            {'name': 'Cold & Flu',           'slug': 'cold-flu',             'icon': 'fa-solid fa-virus'},
            {'name': 'Digestive Health',     'slug': 'digestive-health',     'icon': 'fa-solid fa-stomach'},  # custom
            {'name': 'Diabetes Care',        'slug': 'diabetes-care',        'icon': 'fa-solid fa-syringe'},
            {'name': 'Heart & BP',           'slug': 'heart-bp',             'icon': 'fa-solid fa-heart-pulse'},
            {'name': 'Vitamins & Supplements','slug': 'vitamins-supplements','icon': 'fa-solid fa-capsules'},
            {'name': 'Skin Care',            'slug': 'skin-care',            'icon': 'fa-solid fa-hand-sparkles'},
            {'name': 'Eye & Ear Care',       'slug': 'eye-ear-care',         'icon': 'fa-solid fa-eye'},
            {'name': 'Baby & Mother Care',   'slug': 'baby-mother-care',     'icon': 'fa-solid fa-baby'},
            {'name': 'First Aid',            'slug': 'first-aid',            'icon': 'fa-solid fa-kit-medical'},
            {'name': 'Antibiotics',          'slug': 'antibiotics',          'icon': 'fa-solid fa-pills'},
            {'name': 'Ayurvedic & Herbal',   'slug': 'ayurvedic-herbal',     'icon': 'fa-solid fa-leaf'},
        ]

        cat_objs = {}
        for c in categories_data:
            obj, created = Category.objects.get_or_create(
                slug=c['slug'],
                defaults={'name': c['name'], 'icon': c['icon'], 'is_active': True},
            )
            cat_objs[c['slug']] = obj
            status = '✅ Created' if created else '⏭️  Exists'
            self.stdout.write(f'  {status}: Category "{obj.name}"')

        # ─── PRODUCTS ────────────────────────────
        products_data = [
            # ── Pain Relief ──
            {'category': 'pain-relief', 'name': 'Paracetamol 500mg',          'slug': 'paracetamol-500mg',         'brand': 'Lomus Pharma',        'composition': 'Paracetamol 500mg',        'form': 'Tablet',  'strength': '500mg',   'pack_size': '10 Tablets',   'manufacturer': 'Lomus Pharmaceuticals',       'price': 25,    'original_price': 30,    'stock': 500,  'requires_rx': False},
            {'category': 'pain-relief', 'name': 'Ibuprofen 400mg',            'slug': 'ibuprofen-400mg',           'brand': 'Nepal Pharma',        'composition': 'Ibuprofen 400mg',          'form': 'Tablet',  'strength': '400mg',   'pack_size': '10 Tablets',   'manufacturer': 'Nepal Pharma Laboratory',     'price': 45,    'original_price': 55,    'stock': 350,  'requires_rx': False},
            {'category': 'pain-relief', 'name': 'Diclofenac Gel 30g',         'slug': 'diclofenac-gel-30g',        'brand': 'Asian Pharma',        'composition': 'Diclofenac Diethylamine',  'form': 'Gel',     'strength': '1% w/w',  'pack_size': '30g Tube',     'manufacturer': 'Asian Pharmaceuticals',       'price': 120,   'original_price': 150,   'stock': 200,  'requires_rx': False},
            {'category': 'pain-relief', 'name': 'Nimesulide 100mg',           'slug': 'nimesulide-100mg',          'brand': 'Deurali-Janta',       'composition': 'Nimesulide 100mg',         'form': 'Tablet',  'strength': '100mg',   'pack_size': '10 Tablets',   'manufacturer': 'Deurali-Janta Pharma',        'price': 35,    'original_price': 40,    'stock': 420,  'requires_rx': False},

            # ── Cold & Flu ──
            {'category': 'cold-flu',    'name': 'Cetrizine 10mg',             'slug': 'cetrizine-10mg',            'brand': 'Nepal Pharma',        'composition': 'Cetirizine HCl 10mg',      'form': 'Tablet',  'strength': '10mg',    'pack_size': '10 Tablets',   'manufacturer': 'Nepal Pharma Laboratory',     'price': 30,    'original_price': 40,    'stock': 600,  'requires_rx': False},
            {'category': 'cold-flu',    'name': 'Sinex Nasal Spray',          'slug': 'sinex-nasal-spray',         'brand': 'Vicks',               'composition': 'Oxymetazoline HCl',        'form': 'Spray',   'strength': '0.05%',   'pack_size': '15ml Bottle',  'manufacturer': 'P&G Health',                  'price': 185,   'original_price': 220,   'stock': 150,  'requires_rx': False},
            {'category': 'cold-flu',    'name': 'Amoxicillin 500mg',          'slug': 'amoxicillin-500mg',         'brand': 'Lomus Pharma',        'composition': 'Amoxicillin Trihydrate',   'form': 'Capsule', 'strength': '500mg',   'pack_size': '15 Capsules',  'manufacturer': 'Lomus Pharmaceuticals',       'price': 90,    'original_price': 110,   'stock': 300,  'requires_rx': True},
            {'category': 'cold-flu',    'name': 'Cough Syrup 100ml',          'slug': 'cough-syrup-100ml',         'brand': 'Time Pharma',         'composition': 'Dextromethorphan + CPM',   'form': 'Syrup',   'strength': '100ml',   'pack_size': '100ml Bottle', 'manufacturer': 'Time Pharmaceuticals',        'price': 75,    'original_price': 95,    'stock': 250,  'requires_rx': False},

            # ── Digestive Health ──
            {'category': 'digestive-health', 'name': 'Omeprazole 20mg',       'slug': 'omeprazole-20mg',           'brand': 'Curex Pharma',        'composition': 'Omeprazole 20mg',          'form': 'Capsule', 'strength': '20mg',    'pack_size': '10 Capsules',  'manufacturer': 'Curex Pharmaceuticals',       'price': 55,    'original_price': 70,    'stock': 400,  'requires_rx': False},
            {'category': 'digestive-health', 'name': 'Domperidone 10mg',      'slug': 'domperidone-10mg',          'brand': 'Asian Pharma',        'composition': 'Domperidone 10mg',         'form': 'Tablet',  'strength': '10mg',    'pack_size': '10 Tablets',   'manufacturer': 'Asian Pharmaceuticals',       'price': 40,    'original_price': 50,    'stock': 350,  'requires_rx': False},
            {'category': 'digestive-health', 'name': 'ORS Sachets (Pack of 5)', 'slug': 'ors-sachets-5',           'brand': 'Jeevan Jal',          'composition': 'Electrolytes + Glucose',   'form': 'Powder',  'strength': '21.8g',   'pack_size': '5 Sachets',    'manufacturer': 'Nepal CRS Company',           'price': 50,    'original_price': 50,    'stock': 800,  'requires_rx': False},
            {'category': 'digestive-health', 'name': 'Pantoprazole 40mg',     'slug': 'pantoprazole-40mg',         'brand': 'Deurali-Janta',       'composition': 'Pantoprazole Sodium 40mg', 'form': 'Tablet',  'strength': '40mg',    'pack_size': '10 Tablets',   'manufacturer': 'Deurali-Janta Pharma',        'price': 85,    'original_price': 100,   'stock': 300,  'requires_rx': True},

            # ── Diabetes Care ──
            {'category': 'diabetes-care', 'name': 'Metformin 500mg',          'slug': 'metformin-500mg',           'brand': 'Lomus Pharma',        'composition': 'Metformin HCl 500mg',      'form': 'Tablet',  'strength': '500mg',   'pack_size': '10 Tablets',   'manufacturer': 'Lomus Pharmaceuticals',       'price': 30,    'original_price': 35,    'stock': 450,  'requires_rx': True},
            {'category': 'diabetes-care', 'name': 'Glimepiride 2mg',          'slug': 'glimepiride-2mg',           'brand': 'Nepal Pharma',        'composition': 'Glimepiride 2mg',          'form': 'Tablet',  'strength': '2mg',     'pack_size': '10 Tablets',   'manufacturer': 'Nepal Pharma Laboratory',     'price': 65,    'original_price': 80,    'stock': 300,  'requires_rx': True},
            {'category': 'diabetes-care', 'name': 'Insulin Syringe 1ml',      'slug': 'insulin-syringe-1ml',       'brand': 'BD',                  'composition': 'N/A',                      'form': 'Syringe', 'strength': '1ml',     'pack_size': '10 Syringes',  'manufacturer': 'Becton Dickinson',            'price': 250,   'original_price': 300,   'stock': 150,  'requires_rx': False},
            {'category': 'diabetes-care', 'name': 'Glucometer Test Strips',   'slug': 'glucometer-test-strips',    'brand': 'Accu-Chek',           'composition': 'N/A',                      'form': 'Strip',   'strength': 'N/A',     'pack_size': '50 Strips',    'manufacturer': 'Roche Diabetes',              'price': 1100,  'original_price': 1350,  'stock': 100,  'requires_rx': False},

            # ── Heart & BP ──
            {'category': 'heart-bp',    'name': 'Amlodipine 5mg',             'slug': 'amlodipine-5mg',            'brand': 'Lomus Pharma',        'composition': 'Amlodipine Besylate 5mg',  'form': 'Tablet',  'strength': '5mg',     'pack_size': '10 Tablets',   'manufacturer': 'Lomus Pharmaceuticals',       'price': 45,    'original_price': 55,    'stock': 400,  'requires_rx': True},
            {'category': 'heart-bp',    'name': 'Atorvastatin 10mg',          'slug': 'atorvastatin-10mg',         'brand': 'Deurali-Janta',       'composition': 'Atorvastatin Calcium 10mg','form': 'Tablet',  'strength': '10mg',    'pack_size': '10 Tablets',   'manufacturer': 'Deurali-Janta Pharma',        'price': 70,    'original_price': 90,    'stock': 350,  'requires_rx': True},
            {'category': 'heart-bp',    'name': 'Losartan 50mg',              'slug': 'losartan-50mg',             'brand': 'Nepal Pharma',        'composition': 'Losartan Potassium 50mg',  'form': 'Tablet',  'strength': '50mg',    'pack_size': '10 Tablets',   'manufacturer': 'Nepal Pharma Laboratory',     'price': 60,    'original_price': 75,    'stock': 300,  'requires_rx': True},
            {'category': 'heart-bp',    'name': 'Aspirin 75mg',               'slug': 'aspirin-75mg',              'brand': 'Curex Pharma',        'composition': 'Aspirin 75mg',             'form': 'Tablet',  'strength': '75mg',    'pack_size': '14 Tablets',   'manufacturer': 'Curex Pharmaceuticals',       'price': 20,    'original_price': 25,    'stock': 600,  'requires_rx': False},

            # ── Vitamins & Supplements ──
            {'category': 'vitamins-supplements', 'name': 'Vitamin C 500mg Chewable', 'slug': 'vitamin-c-500mg',    'brand': 'Nepal Pharma',        'composition': 'Ascorbic Acid 500mg',      'form': 'Chewable','strength': '500mg',   'pack_size': '30 Tablets',   'manufacturer': 'Nepal Pharma Laboratory',     'price': 180,   'original_price': 220,   'stock': 400,  'requires_rx': False},
            {'category': 'vitamins-supplements', 'name': 'Calcium + Vitamin D3',     'slug': 'calcium-vitamin-d3', 'brand': 'Deurali-Janta',       'composition': 'Calcium 500mg + D3 250IU', 'form': 'Tablet',  'strength': '500mg',   'pack_size': '30 Tablets',   'manufacturer': 'Deurali-Janta Pharma',        'price': 250,   'original_price': 300,   'stock': 300,  'requires_rx': False},
            {'category': 'vitamins-supplements', 'name': 'Iron + Folic Acid',        'slug': 'iron-folic-acid',    'brand': 'Lomus Pharma',        'composition': 'Ferrous Sulphate + FA',    'form': 'Tablet',  'strength': '200mg',   'pack_size': '30 Tablets',   'manufacturer': 'Lomus Pharmaceuticals',       'price': 120,   'original_price': 150,   'stock': 500,  'requires_rx': False},
            {'category': 'vitamins-supplements', 'name': 'Multivitamin Daily',       'slug': 'multivitamin-daily', 'brand': 'Asian Pharma',        'composition': 'Multivitamins + Minerals', 'form': 'Tablet',  'strength': 'N/A',     'pack_size': '30 Tablets',   'manufacturer': 'Asian Pharmaceuticals',       'price': 350,   'original_price': 420,   'stock': 250,  'requires_rx': False},
            {'category': 'vitamins-supplements', 'name': 'Omega-3 Fish Oil',         'slug': 'omega-3-fish-oil',   'brand': 'Time Pharma',         'composition': 'EPA 180mg + DHA 120mg',    'form': 'Softgel', 'strength': '1000mg',  'pack_size': '30 Softgels',  'manufacturer': 'Time Pharmaceuticals',        'price': 420,   'original_price': 500,   'stock': 200,  'requires_rx': False},

            # ── Skin Care ──
            {'category': 'skin-care',   'name': 'Clotrimazole Cream 15g',      'slug': 'clotrimazole-cream',       'brand': 'Nepal Pharma',        'composition': 'Clotrimazole 1%',          'form': 'Cream',   'strength': '1% w/w',  'pack_size': '15g Tube',     'manufacturer': 'Nepal Pharma Laboratory',     'price': 65,    'original_price': 80,    'stock': 300,  'requires_rx': False},
            {'category': 'skin-care',   'name': 'Betamethasone Cream 20g',     'slug': 'betamethasone-cream',      'brand': 'Asian Pharma',        'composition': 'Betamethasone 0.1%',       'form': 'Cream',   'strength': '0.1%',    'pack_size': '20g Tube',     'manufacturer': 'Asian Pharmaceuticals',       'price': 85,    'original_price': 100,   'stock': 250,  'requires_rx': True},
            {'category': 'skin-care',   'name': 'Sunscreen SPF 50 Lotion',     'slug': 'sunscreen-spf50',          'brand': 'Himalaya',            'composition': 'UV Filters + Aloe Vera',   'form': 'Lotion',  'strength': 'SPF 50',  'pack_size': '100ml Bottle', 'manufacturer': 'Himalaya Wellness',           'price': 450,   'original_price': 550,   'stock': 180,  'requires_rx': False},

            # ── Eye & Ear Care ──
            {'category': 'eye-ear-care','name': 'Ciprofloxacin Eye Drops',     'slug': 'ciprofloxacin-eye-drops',  'brand': 'Lomus Pharma',        'composition': 'Ciprofloxacin 0.3%',       'form': 'Drops',   'strength': '0.3%',    'pack_size': '10ml Bottle',  'manufacturer': 'Lomus Pharmaceuticals',       'price': 75,    'original_price': 90,    'stock': 200,  'requires_rx': True},
            {'category': 'eye-ear-care','name': 'Artificial Tears 10ml',       'slug': 'artificial-tears-10ml',    'brand': 'Time Pharma',         'composition': 'CMC Sodium 0.5%',          'form': 'Drops',   'strength': '0.5%',    'pack_size': '10ml Bottle',  'manufacturer': 'Time Pharmaceuticals',        'price': 110,   'original_price': 140,   'stock': 300,  'requires_rx': False},

            # ── Baby & Mother Care ──
            {'category': 'baby-mother-care', 'name': 'Gripe Water 150ml',      'slug': 'gripe-water-150ml',       'brand': 'Woodwards',           'composition': 'Dill Oil + Sodium Bicarb', 'form': 'Liquid',  'strength': '150ml',   'pack_size': '150ml Bottle', 'manufacturer': 'Dabur Nepal',                 'price': 130,   'original_price': 160,   'stock': 200,  'requires_rx': False},
            {'category': 'baby-mother-care', 'name': 'Baby Diaper Rash Cream', 'slug': 'diaper-rash-cream',       'brand': 'Himalaya',            'composition': 'Zinc Oxide + Aloe Vera',   'form': 'Cream',   'strength': '50g',     'pack_size': '50g Tube',     'manufacturer': 'Himalaya Wellness',           'price': 200,   'original_price': 240,   'stock': 180,  'requires_rx': False},
            {'category': 'baby-mother-care', 'name': 'Prenatal Multivitamin',  'slug': 'prenatal-multivitamin',   'brand': 'Asian Pharma',        'composition': 'Iron + Folic Acid + DHA',  'form': 'Tablet',  'strength': 'N/A',     'pack_size': '30 Tablets',   'manufacturer': 'Asian Pharmaceuticals',       'price': 280,   'original_price': 340,   'stock': 250,  'requires_rx': False},

            # ── First Aid ──
            {'category': 'first-aid',   'name': 'Cotton Bandage Roll 10cm',    'slug': 'cotton-bandage-10cm',     'brand': 'SurgeCare',           'composition': 'N/A',                      'form': 'Bandage', 'strength': '10cm',    'pack_size': '1 Roll',       'manufacturer': 'SurgeCare Nepal',             'price': 35,    'original_price': 45,    'stock': 500,  'requires_rx': False},
            {'category': 'first-aid',   'name': 'Povidone Iodine Solution',    'slug': 'povidone-iodine',         'brand': 'Betadine',            'composition': 'Povidone Iodine 5%',       'form': 'Solution','strength': '5% w/v',  'pack_size': '100ml Bottle', 'manufacturer': 'Win Medicare',                'price': 95,    'original_price': 120,   'stock': 300,  'requires_rx': False},
            {'category': 'first-aid',   'name': 'Adhesive Bandage Strips',     'slug': 'adhesive-bandage-strips', 'brand': 'Band-Aid',            'composition': 'N/A',                      'form': 'Strips',  'strength': 'N/A',     'pack_size': '20 Strips',    'manufacturer': 'Johnson & Johnson',           'price': 75,    'original_price': 90,    'stock': 400,  'requires_rx': False},
            {'category': 'first-aid',   'name': 'Digital Thermometer',         'slug': 'digital-thermometer',     'brand': 'Microlife',           'composition': 'N/A',                      'form': 'Device',  'strength': 'N/A',     'pack_size': '1 Unit',       'manufacturer': 'Microlife Corp',              'price': 350,   'original_price': 450,   'stock': 120,  'requires_rx': False},

            # ── Antibiotics ──
            {'category': 'antibiotics', 'name': 'Azithromycin 500mg',          'slug': 'azithromycin-500mg',      'brand': 'Deurali-Janta',       'composition': 'Azithromycin 500mg',       'form': 'Tablet',  'strength': '500mg',   'pack_size': '3 Tablets',    'manufacturer': 'Deurali-Janta Pharma',        'price': 120,   'original_price': 150,   'stock': 300,  'requires_rx': True},
            {'category': 'antibiotics', 'name': 'Ciprofloxacin 500mg',        'slug': 'ciprofloxacin-500mg',     'brand': 'Lomus Pharma',        'composition': 'Ciprofloxacin HCl 500mg',  'form': 'Tablet',  'strength': '500mg',   'pack_size': '10 Tablets',   'manufacturer': 'Lomus Pharmaceuticals',       'price': 85,    'original_price': 100,   'stock': 250,  'requires_rx': True},
            {'category': 'antibiotics', 'name': 'Metronidazole 400mg',        'slug': 'metronidazole-400mg',     'brand': 'Nepal Pharma',        'composition': 'Metronidazole 400mg',      'form': 'Tablet',  'strength': '400mg',   'pack_size': '15 Tablets',   'manufacturer': 'Nepal Pharma Laboratory',     'price': 50,    'original_price': 60,    'stock': 350,  'requires_rx': True},
            {'category': 'antibiotics', 'name': 'Cephalexin 500mg',           'slug': 'cephalexin-500mg',        'brand': 'Curex Pharma',        'composition': 'Cephalexin 500mg',         'form': 'Capsule', 'strength': '500mg',   'pack_size': '10 Capsules',  'manufacturer': 'Curex Pharmaceuticals',       'price': 110,   'original_price': 135,   'stock': 280,  'requires_rx': True},

            # ── Ayurvedic & Herbal ──
            {'category': 'ayurvedic-herbal', 'name': 'Ashwagandha Tablets',    'slug': 'ashwagandha-tablets',     'brand': 'Dabur',               'composition': 'Ashwagandha Extract',      'form': 'Tablet',  'strength': '500mg',   'pack_size': '60 Tablets',   'manufacturer': 'Dabur Nepal',                 'price': 320,   'original_price': 400,   'stock': 200,  'requires_rx': False},
            {'category': 'ayurvedic-herbal', 'name': 'Tulsi Drops 20ml',       'slug': 'tulsi-drops-20ml',        'brand': 'Organic Nepal',       'composition': 'Holy Basil Extract',       'form': 'Drops',   'strength': '20ml',    'pack_size': '20ml Bottle',  'manufacturer': 'Organic Nepal Pvt Ltd',       'price': 180,   'original_price': 220,   'stock': 250,  'requires_rx': False},
            {'category': 'ayurvedic-herbal', 'name': 'Chyawanprash 500g',      'slug': 'chyawanprash-500g',       'brand': 'Dabur',               'composition': 'Amla + 40+ Herbs',         'form': 'Paste',   'strength': '500g',    'pack_size': '500g Jar',     'manufacturer': 'Dabur Nepal',                 'price': 380,   'original_price': 450,   'stock': 150,  'requires_rx': False},
            {'category': 'ayurvedic-herbal', 'name': 'Triphala Churna 100g',   'slug': 'triphala-churna-100g',    'brand': 'Himalaya',            'composition': 'Amla + Bibhitaki + Haritaki', 'form': 'Powder', 'strength': '100g', 'pack_size': '100g Jar',     'manufacturer': 'Himalaya Wellness',           'price': 150,   'original_price': 190,   'stock': 200,  'requires_rx': False},
        ]

        created_count = 0
        for p in products_data:
            cat_slug = p.pop('category')
            cat = cat_objs.get(cat_slug)
            obj, created = Product.objects.get_or_create(
                slug=p['slug'],
                defaults={**p, 'category': cat, 'is_active': True},
            )
            if created:
                created_count += 1
            status = '✅ Created' if created else '⏭️  Exists'
            self.stdout.write(f'  {status}: Product "{obj.name}"')

        # ─── COUPONS ─────────────────────────────
        now = timezone.now()
        coupons_data = [
            {'code': 'SWASTHYA10',  'discount_type': 'percent', 'discount_value': 10,  'min_order': 200,  'max_uses': 500,  'valid_from': now, 'valid_to': now + timedelta(days=90)},
            {'code': 'FLAT50',      'discount_type': 'flat',    'discount_value': 50,  'min_order': 300,  'max_uses': 300,  'valid_from': now, 'valid_to': now + timedelta(days=60)},
            {'code': 'NEWUSER20',   'discount_type': 'percent', 'discount_value': 20,  'min_order': 100,  'max_uses': 1000, 'valid_from': now, 'valid_to': now + timedelta(days=180)},
            {'code': 'HEALTHBRIDGE','discount_type': 'percent', 'discount_value': 15,  'min_order': 500,  'max_uses': 200,  'valid_from': now, 'valid_to': now + timedelta(days=120)},
            {'code': 'FREESHIP',    'discount_type': 'flat',    'discount_value': 100, 'min_order': 400,  'max_uses': 250,  'valid_from': now, 'valid_to': now + timedelta(days=45)},
        ]

        for c in coupons_data:
            obj, created = Coupon.objects.get_or_create(
                code=c['code'],
                defaults={**c, 'is_active': True},
            )
            status = '✅ Created' if created else '⏭️  Exists'
            self.stdout.write(f'  {status}: Coupon "{obj.code}"')

        self.stdout.write(self.style.SUCCESS(
            f'\n🎉 Pharmacy seeding complete! '
            f'{created_count} new products added across {len(cat_objs)} categories + {len(coupons_data)} coupons.'
        ))
