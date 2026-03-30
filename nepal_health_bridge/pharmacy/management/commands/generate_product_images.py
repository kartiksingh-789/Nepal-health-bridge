"""
Management command to generate professional product images for all pharmacy products.
Run: python manage.py generate_product_images
"""
import os, math, random
from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from pharmacy.models import Product


# ── Colour palettes per category ──────────────────────────────────
CATEGORY_THEMES = {
    'pain-relief':          {'bg1': (227, 66,  52),  'bg2': (192, 57,  43),  'accent': (255,255,255), 'icon': '💊'},
    'cold-flu':             {'bg1': (52, 152, 219),  'bg2': (41, 128, 185),  'accent': (255,255,255), 'icon': '🤧'},
    'digestive-health':     {'bg1': (46, 204, 113),  'bg2': (39, 174,  96),  'accent': (255,255,255), 'icon': '🩺'},
    'diabetes-care':        {'bg1': (155, 89, 182),  'bg2': (142, 68, 173),  'accent': (255,255,255), 'icon': '💉'},
    'heart-bp':             {'bg1': (231, 76,  60),  'bg2': (192, 57,  43),  'accent': (255,255,255), 'icon': '❤️'},
    'vitamins-supplements': {'bg1': (241, 196, 15),  'bg2': (243, 156, 18),  'accent': (255,255,255), 'icon': '💪'},
    'skin-care':            {'bg1': (243, 156, 18),  'bg2': (230, 126, 34),  'accent': (255,255,255), 'icon': '✨'},
    'eye-ear-care':         {'bg1': (52, 73, 94),    'bg2': (44, 62, 80),    'accent': (255,255,255), 'icon': '👁️'},
    'baby-mother-care':     {'bg1': (255, 167, 196), 'bg2': (255, 118, 163), 'accent': (255,255,255), 'icon': '👶'},
    'first-aid':            {'bg1': (231, 76,  60),  'bg2': (192, 57,  43),  'accent': (255,255,255), 'icon': '🩹'},
    'antibiotics':          {'bg1': (26, 188, 156),  'bg2': (22, 160, 133),  'accent': (255,255,255), 'icon': '💊'},
    'ayurvedic-herbal':     {'bg1': (39, 174,  96),  'bg2': (34, 139, 34),   'accent': (255,255,255), 'icon': '🌿'},
}

DEFAULT_THEME = {'bg1': (100, 100, 100), 'bg2': (80, 80, 80), 'accent': (255,255,255), 'icon': '💊'}

# ── Form icons (emoji can't be reliably rendered, so we use text) ──
FORM_SHAPES = {
    'Tablet':  'pill',
    'Capsule': 'capsule',
    'Syrup':   'bottle',
    'Cream':   'tube',
    'Gel':     'tube',
    'Drops':   'eyedrop',
    'Spray':   'spray',
    'Powder':  'sachet',
    'Softgel': 'capsule',
    'Lotion':  'bottle',
    'Liquid':  'bottle',
    'Chewable':'pill',
    'Paste':   'tube',
    'Bandage': 'cross',
    'Strips':  'cross',
    'Solution':'bottle',
    'Device':  'device',
    'Syringe': 'syringe',
    'Strip':   'strip',
}


def draw_rounded_rect(draw, xy, radius, fill):
    """Draw a rounded rectangle."""
    x0, y0, x1, y1 = xy
    draw.rectangle([x0 + radius, y0, x1 - radius, y1], fill=fill)
    draw.rectangle([x0, y0 + radius, x1, y1 - radius], fill=fill)
    draw.pieslice([x0, y0, x0 + 2*radius, y0 + 2*radius], 180, 270, fill=fill)
    draw.pieslice([x1 - 2*radius, y0, x1, y0 + 2*radius], 270, 360, fill=fill)
    draw.pieslice([x0, y1 - 2*radius, x0 + 2*radius, y1], 90, 180, fill=fill)
    draw.pieslice([x1 - 2*radius, y1 - 2*radius, x1, y1], 0, 90, fill=fill)


def draw_pill_shape(draw, cx, cy, size, color):
    """Draw a medicine pill/tablet shape."""
    w, h = int(size * 0.8), int(size * 0.35)
    draw.ellipse([cx - w, cy - h, cx + w, cy + h], fill=color)
    # highlight
    hw, hh = int(w * 0.6), int(h * 0.5)
    highlight = tuple(min(c + 60, 255) for c in color)
    draw.ellipse([cx - hw, cy - hh - 5, cx + hw, cy + hh - 5], fill=highlight)
    # divider line
    draw.line([(cx, cy - h), (cx, cy + h)], fill=(255, 255, 255, 180), width=2)


def draw_capsule_shape(draw, cx, cy, size, color):
    """Draw a capsule shape."""
    w, h = int(size * 0.35), int(size * 0.75)
    # bottom half
    draw.rounded_rectangle([cx - w, cy - h, cx + w, cy + h], radius=w, fill=color)
    # top half different shade
    color2 = tuple(min(c + 40, 255) for c in color)
    draw.rounded_rectangle([cx - w, cy - h, cx + w, cy], radius=w, fill=color2)


def draw_bottle_shape(draw, cx, cy, size, color):
    """Draw a medicine bottle."""
    bw, bh = int(size * 0.5), int(size * 0.8)
    # body
    draw.rounded_rectangle([cx - bw, cy - bh//2, cx + bw, cy + bh//2], radius=12, fill=color)
    # cap
    cw = int(bw * 0.6)
    draw.rounded_rectangle([cx - cw, cy - bh//2 - 20, cx + cw, cy - bh//2 + 5], radius=6, fill=tuple(max(c - 40, 0) for c in color))
    # label
    lw, lh = int(bw * 0.7), int(bh * 0.3)
    draw.rounded_rectangle([cx - lw, cy - lh//2, cx + lw, cy + lh//2], radius=6, fill=(255, 255, 255))


def draw_tube_shape(draw, cx, cy, size, color):
    """Draw a tube (cream/gel)."""
    tw, th = int(size * 0.35), int(size * 0.85)
    # body
    draw.rounded_rectangle([cx - tw, cy - th//3, cx + tw, cy + th//2], radius=15, fill=color)
    # nozzle
    nw = int(tw * 0.4)
    draw.rounded_rectangle([cx - nw, cy - th//2 - 10, cx + nw, cy - th//3 + 10], radius=5, fill=tuple(max(c - 50, 0) for c in color))
    # cap
    draw.ellipse([cx - nw - 2, cy - th//2 - 20, cx + nw + 2, cy - th//2], fill=tuple(max(c - 70, 0) for c in color))


def draw_cross_shape(draw, cx, cy, size, color):
    """Draw a medical cross."""
    s = int(size * 0.3)
    draw.rectangle([cx - s, cy - s*3, cx + s, cy + s*3], fill=color)
    draw.rectangle([cx - s*3, cy - s, cx + s*3, cy + s], fill=color)


def draw_generic_icon(draw, cx, cy, size, color, shape_type):
    """Draw icon based on form type."""
    if shape_type == 'pill':
        draw_pill_shape(draw, cx, cy, size, color)
    elif shape_type == 'capsule':
        draw_capsule_shape(draw, cx, cy, size, color)
    elif shape_type in ('bottle', 'eyedrop', 'spray'):
        draw_bottle_shape(draw, cx, cy, size, color)
    elif shape_type in ('tube',):
        draw_tube_shape(draw, cx, cy, size, color)
    elif shape_type in ('cross',):
        draw_cross_shape(draw, cx, cy, size, color)
    else:
        draw_pill_shape(draw, cx, cy, size, color)


def create_product_image(product, output_path):
    """Generate a professional product card image."""
    W, H = 600, 600
    cat_slug = product.category.slug if product.category else ''
    theme = CATEGORY_THEMES.get(cat_slug, DEFAULT_THEME)
    bg1, bg2 = theme['bg1'], theme['bg2']

    img = Image.new('RGB', (W, H), (255, 255, 255))
    draw = ImageDraw.Draw(img)

    # ── Gradient background (top 60%) ─────────
    for y in range(int(H * 0.62)):
        ratio = y / (H * 0.62)
        r = int(bg1[0] + (bg2[0] - bg1[0]) * ratio)
        g = int(bg1[1] + (bg2[1] - bg1[1]) * ratio)
        b = int(bg1[2] + (bg2[2] - bg1[2]) * ratio)
        draw.line([(0, y), (W, y)], fill=(r, g, b))

    # ── Decorative circles (subtle) ──────────
    for _ in range(5):
        cx = random.randint(0, W)
        cy = random.randint(0, int(H * 0.55))
        radius = random.randint(30, 100)
        overlay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        overlay_draw.ellipse(
            [cx - radius, cy - radius, cx + radius, cy + radius],
            fill=(255, 255, 255, 20)
        )
        img.paste(Image.alpha_composite(Image.new('RGBA', (W, H), (0, 0, 0, 0)), overlay).convert('RGB'),
                  mask=overlay.split()[3])

    # ── Medicine icon in center of coloured area ──
    shape = FORM_SHAPES.get(product.form, 'pill')
    icon_color = (255, 255, 255)
    draw_generic_icon(draw, W // 2, int(H * 0.28), 120, icon_color, shape)

    # ── White bottom card area ────────────────
    card_y = int(H * 0.58)
    draw_rounded_rect(draw, (0, card_y, W, H), 30, (255, 255, 255))

    # ── Text rendering ────────────────────────
    try:
        font_name_bold = ImageFont.truetype('arialbd.ttf', 24)
        font_brand     = ImageFont.truetype('arial.ttf', 18)
        font_detail    = ImageFont.truetype('arial.ttf', 16)
        font_price     = ImageFont.truetype('arialbd.ttf', 28)
        font_badge     = ImageFont.truetype('arialbd.ttf', 14)
        font_form_sm   = ImageFont.truetype('arial.ttf', 14)
    except:
        font_name_bold = ImageFont.load_default()
        font_brand = font_detail = font_price = font_badge = font_form_sm = font_name_bold

    text_x = 30
    y_cursor = card_y + 20

    # Product Name (wrap if long)
    name = product.name
    if len(name) > 28:
        # split into two lines
        mid = name[:28].rfind(' ')
        if mid == -1:
            mid = 28
        line1, line2 = name[:mid], name[mid:].strip()
        draw.text((text_x, y_cursor), line1, fill=(33, 33, 33), font=font_name_bold)
        y_cursor += 30
        draw.text((text_x, y_cursor), line2, fill=(33, 33, 33), font=font_name_bold)
        y_cursor += 32
    else:
        draw.text((text_x, y_cursor), name, fill=(33, 33, 33), font=font_name_bold)
        y_cursor += 32

    # Brand
    draw.text((text_x, y_cursor), product.brand, fill=(120, 120, 120), font=font_brand)
    y_cursor += 26

    # Form + Strength + Pack
    detail = f'{product.form}  •  {product.strength}  •  {product.pack_size}'
    draw.text((text_x, y_cursor), detail, fill=(150, 150, 150), font=font_detail)
    y_cursor += 30

    # Price row
    price_str = f'NPR {product.price}'
    draw.text((text_x, y_cursor), price_str, fill=bg1, font=font_price)

    if product.original_price > product.price:
        # strikethrough original price
        orig_str = f'NPR {product.original_price}'
        px = text_x + draw.textlength(price_str, font=font_price) + 15
        draw.text((px, y_cursor + 6), orig_str, fill=(180, 180, 180), font=font_detail)
        ow = draw.textlength(orig_str, font=font_detail)
        draw.line([(px, y_cursor + 16), (px + ow, y_cursor + 16)], fill=(180, 180, 180), width=1)

        # discount badge
        disc = product.discount_percent
        if disc > 0:
            badge_text = f'{disc}% OFF'
            bx = W - 30 - int(draw.textlength(badge_text, font=font_badge)) - 16
            draw_rounded_rect(draw, (bx, y_cursor + 2, W - 30, y_cursor + 26), 10, bg1)
            draw.text((bx + 8, y_cursor + 4), badge_text, fill=(255, 255, 255), font=font_badge)

    # ── Prescription badge (top‑right) ────────
    if product.requires_rx:
        rx_text = 'Rx Required'
        rw = int(draw.textlength(rx_text, font=font_badge)) + 20
        rx_x = W - rw - 15
        draw_rounded_rect(draw, (rx_x, 15, W - 15, 38), 10, (231, 76, 60))
        draw.text((rx_x + 10, 17), rx_text, fill=(255, 255, 255), font=font_badge)

    # ── Category badge (top‑left) ─────────────
    if product.category:
        cat_text = product.category.name
        cw = int(draw.textlength(cat_text, font=font_form_sm)) + 20
        draw_rounded_rect(draw, (15, 15, 15 + cw, 38), 10, (0, 0, 0, 80))
        # semi-transparent black background
        cat_bg = Image.new('RGBA', (cw, 23), (0, 0, 0, 100))
        img.paste(Image.alpha_composite(
            Image.new('RGBA', (cw, 23), (0, 0, 0, 0)), cat_bg
        ).convert('RGB'), (15, 15))
        draw = ImageDraw.Draw(img)  # refresh draw
        draw_rounded_rect(draw, (15, 15, 15 + cw, 38), 10, (0, 0, 0))
        draw.text((25, 17), cat_text, fill=(255, 255, 255), font=font_form_sm)

    # ── Save ──────────────────────────────────
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img.save(output_path, quality=92)


class Command(BaseCommand):
    help = 'Generate product images for all pharmacy products'

    def handle(self, *args, **options):
        media_root = Path(settings.MEDIA_ROOT)
        products_dir = media_root / 'products'
        products_dir.mkdir(parents=True, exist_ok=True)

        products = Product.objects.select_related('category').all()
        total = products.count()
        self.stdout.write(f'🎨 Generating images for {total} products …\n')

        for i, product in enumerate(products, 1):
            filename = f'{product.slug}.png'
            filepath = products_dir / filename
            create_product_image(product, str(filepath))

            # Update the DB to point to this image
            product.image = f'products/{filename}'
            product.save(update_fields=['image'])

            self.stdout.write(f'  [{i}/{total}] ✅ {product.name}')

        self.stdout.write(self.style.SUCCESS(f'\n🎉 Done! Generated {total} product images in {products_dir}'))
