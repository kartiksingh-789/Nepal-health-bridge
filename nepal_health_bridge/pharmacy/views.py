from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.db.models import Q
from django.conf import settings
import random
import json
import uuid
import hmac
import hashlib
import base64
import requests as http_requests

from .models import (
    User, OTP, Product, Category, Cart, CartItem,
    Wishlist, Order, OrderItem, Address, Coupon,
    Review, Prescription, Notification
)


# ── Helper ───────────────────────────────────────────────────────────
def get_session_user(request):
    mobile = request.session.get('user_mobile')
    if not mobile:
        return None
    try:
        return User.objects.get(mobile=mobile)
    except User.DoesNotExist:
        return None


REALISTIC_SLUGS = [
    # Pain Relief (4)
    'paracetamol-500mg', 'ibuprofen-400mg', 'diclofenac-gel-30g', 'nimesulide-100mg',
    # Cold & Flu (4)
    'cetrizine-10mg', 'sinex-nasal-spray', 'amoxicillin-500mg', 'cough-syrup-100ml',
    # Digestive Health (4)
    'omeprazole-20mg', 'domperidone-10mg', 'ors-sachets-5', 'pantoprazole-40mg',
    # Diabetes Care (4)
    'metformin-500mg', 'glimepiride-2mg', 'insulin-syringe-1ml', 'glucometer-test-strips',
    # Heart & BP (4)
    'amlodipine-5mg', 'atorvastatin-10mg', 'losartan-50mg', 'aspirin-75mg',
    # Vitamins & Supplements (5)
    'vitamin-c-500mg', 'calcium-vitamin-d3', 'iron-folic-acid', 'multivitamin-daily', 'omega-3-fish-oil',
    # Skin Care (3)
    'clotrimazole-cream', 'betamethasone-cream', 'sunscreen-spf50',
    # Eye & Ear Care (2)
    'ciprofloxacin-eye-drops', 'artificial-tears-10ml',
    # Baby & Mother Care (3)
    'gripe-water-150ml', 'diaper-rash-cream', 'prenatal-multivitamin',
    # First Aid (1)
    'cotton-bandage-10cm',
]


# ──────────────────────────────────────────────
# HOME
# ──────────────────────────────────────────────

def index(request):
    from django.db.models import Case, When, IntegerField
    categories = Category.objects.filter(is_active=True)
    featured_products = Product.objects.filter(is_active=True, stock__gt=0).annotate(
        priority=Case(
            When(slug__in=REALISTIC_SLUGS, then=1),
            default=0,
            output_field=IntegerField(),
        )
    ).order_by('-priority', '-created_at')[:8]

    return render(request, 'index.html', {
        'categories':        categories,
        'featured_products': featured_products,
    })


# ──────────────────────────────────────────────
# PRODUCTS
# ──────────────────────────────────────────────

def products(request):
    from django.core.paginator import Paginator
    from django.db.models import Case, When, IntegerField

    products_qs = Product.objects.filter(is_active=True).annotate(
        priority=Case(
            When(slug__in=REALISTIC_SLUGS, then=1),
            default=0,
            output_field=IntegerField(),
        )
    )
    categories  = Category.objects.filter(is_active=True)

    price_choices = [
        ('all',      'All Prices'),
        ('0-100',    'Below ₹100'),
        ('100-500',  '₹100 - ₹500'),
        ('500-1000', '₹500 - ₹1000'),
        ('1000+',    'Above ₹1000'),
    ]

    category_slug = request.GET.get('category')
    if category_slug and category_slug != 'all':
        products_qs = products_qs.filter(category__slug=category_slug)

    price_range = request.GET.get('price')
    if price_range == '0-100':
        products_qs = products_qs.filter(price__lt=100)
    elif price_range == '100-500':
        products_qs = products_qs.filter(price__gte=100, price__lte=500)
    elif price_range == '500-1000':
        products_qs = products_qs.filter(price__gt=500, price__lte=1000)
    elif price_range == '1000+':
        products_qs = products_qs.filter(price__gt=1000)

    rx = request.GET.get('rx')
    if rx == 'yes':
        products_qs = products_qs.filter(requires_rx=True)
    elif rx == 'no':
        products_qs = products_qs.filter(requires_rx=False)

    search = request.GET.get('search', '')
    if search:
        products_qs = products_qs.filter(
            Q(name__icontains=search) |
            Q(brand__icontains=search) |
            Q(composition__icontains=search)
        )

    sort = request.GET.get('sort', 'relevance')
    if sort == 'price-low':
        products_qs = products_qs.order_by('price')
    elif sort == 'price-high':
        products_qs = products_qs.order_by('-price')
    else:
        # Prioritize generated images (priority 1) then by newest
        products_qs = products_qs.order_by('-priority', '-created_at')

    paginator = Paginator(products_qs, 9)
    page_obj  = paginator.get_page(request.GET.get('page', 1))

    return render(request, 'products.html', {
        'products':      page_obj,
        'page_obj':      page_obj,
        'categories':    categories,
        'price_choices': price_choices,
        'search':        search,
        'sort':          sort,
    })


# ──────────────────────────────────────────────
# PRODUCT DETAIL
# ──────────────────────────────────────────────

def product_detail(request, id):
    product = get_object_or_404(Product, id=id, is_active=True)
    reviews = product.reviews.all().order_by('-created_at')
    from django.db.models import Case, When, IntegerField
    similar = Product.objects.filter(category=product.category, is_active=True).exclude(id=id).annotate(
        priority=Case(
            When(slug__in=REALISTIC_SLUGS, then=1),
            default=0,
            output_field=IntegerField(),
        )
    ).order_by('-priority', '-created_at')[:4]

    in_wishlist = False
    user = get_session_user(request)
    if user:
        in_wishlist = Wishlist.objects.filter(user=user, product=product).exists()

    return render(request, 'product_detail.html', {
        'product':     product,
        'reviews':     reviews,
        'similar':     similar,
        'in_wishlist': in_wishlist,
    })


# ──────────────────────────────────────────────
# LOGIN
# ──────────────────────────────────────────────

def login_view(request):
    if get_session_user(request):
        return redirect('index')

    if request.method == 'POST':
        data   = json.loads(request.body)
        action = data.get('action')

        if action == 'send_otp':
            mobile = data.get('mobile', '').strip()
            if not mobile or len(mobile) != 10:
                return JsonResponse({'success': False, 'message': 'Invalid mobile number'})
            otp_code = str(random.randint(1000, 9999))
            OTP.objects.filter(mobile=mobile).delete()
            OTP.objects.create(mobile=mobile, otp=otp_code)
            print(f'>>> OTP for {mobile}: {otp_code}')
            return JsonResponse({'success': True, 'message': 'OTP sent!', 'dev_otp': otp_code})

        elif action == 'verify_otp':
            mobile   = data.get('mobile', '').strip()
            otp_code = data.get('otp', '').strip()
            try:
                otp_obj = OTP.objects.filter(mobile=mobile, is_used=False).latest('created_at')
            except OTP.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'OTP not found. Try again.'})
            if otp_obj.is_expired():
                return JsonResponse({'success': False, 'message': 'OTP expired. Request again.'})
            if otp_obj.otp != otp_code:
                return JsonResponse({'success': False, 'message': 'Wrong OTP. Try again.'})
            otp_obj.is_used = True
            otp_obj.save()
            user, created = User.objects.get_or_create(mobile=mobile)
            request.session['user_mobile'] = mobile
            request.session.modified = True
            request.session.save()
            return JsonResponse({
    'success':    True,
    'redirect':   '/pharmacy/',
    'first_name': user.first_name or '',
    'last_name':  user.last_name  or '',
    'mobile':     mobile,
    'is_admin':   user.is_admin,   # ← ADD THIS
})
    return render(request, 'login.html')


# ──────────────────────────────────────────────
# LOGOUT
# ──────────────────────────────────────────────

def logout_view(request):
    request.session.flush()
    return redirect('login')


# ──────────────────────────────────────────────
# PROFILE
# ──────────────────────────────────────────────

def profile(request):
    user = get_session_user(request)
    if not user:
        return redirect('login')

    if request.method == 'POST':
        user.first_name = request.POST.get('first_name', '')
        user.last_name  = request.POST.get('last_name', '')
        user.email      = request.POST.get('email', '')
        user.gender     = request.POST.get('gender', '')
        dob = request.POST.get('dob', '')
        if dob:
            user.dob = dob
        user.save()
        request.session['user_first_name'] = user.first_name
        request.session.save()
        from django.contrib import messages
        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')

    return render(request, 'profile.html', {
        'user':      user,
        'addresses': user.addresses.all(),
        'orders':    user.orders.all()[:5],
    })


# ──────────────────────────────────────────────
# WISHLIST
# ──────────────────────────────────────────────

def wishlist(request):
    user = get_session_user(request)
    if not user:
        return redirect('login')
    items = Wishlist.objects.filter(user=user).select_related('product')
    return render(request, 'wishlist.html', {'wishlist_items': items})


def toggle_wishlist(request, product_id):
    user = get_session_user(request)
    if not user:
        return JsonResponse({'status': 'login_required'})
    product      = get_object_or_404(Product, id=product_id)
    obj, created = Wishlist.objects.get_or_create(user=user, product=product)
    if not created:
        obj.delete()
        return JsonResponse({'status': 'removed'})
    return JsonResponse({'status': 'added'})


# ──────────────────────────────────────────────
# CART
# ──────────────────────────────────────────────

def add_to_cart(request, product_id):
    user = get_session_user(request)
    if not user:
        return JsonResponse({'status': 'login_required'})
    product       = get_object_or_404(Product, id=product_id)
    cart, _       = Cart.objects.get_or_create(user=user)
    item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        if item.quantity < product.stock:
            item.quantity += 1
            item.save()
    return JsonResponse({
        'status':     'success',
        'cart_count': cart.item_count,
        'message':    f'{product.name} added to cart!'
    })


def remove_from_cart(request, item_id):
    user = get_session_user(request)
    if not user:
        return JsonResponse({'status': 'login_required'})
    item = get_object_or_404(CartItem, id=item_id, cart__user=user)
    item.delete()
    return JsonResponse({'status': 'removed'})


def cart_data(request):
    user = get_session_user(request)
    if not user:
        return JsonResponse({'items': [], 'total': '0.00', 'item_count': 0})

    cart = Cart.objects.filter(user=user).first()
    if not cart:
        return JsonResponse({'items': [], 'total': '0.00', 'item_count': 0})

    items = []
    for item in cart.items.select_related('product').all():
        image = 'https://via.placeholder.com/80'
        if item.product and item.product.image:
            image = item.product.image.url
        items.append({
            'id':       item.id,
            'name':     item.product.name if item.product else 'Unknown',
            'price':    float(item.product.price) if item.product else 0,
            'quantity': item.quantity,
            'subtotal': float(item.subtotal),
            'image':    image,
            'stock':    item.product.stock if item.product else 0,
        })

    return JsonResponse({
        'items':      items,
        'total':      float(cart.total),
        'item_count': cart.item_count,
    })


def update_cart_qty(request, item_id):
    user = get_session_user(request)
    if not user:
        return JsonResponse({'status': 'login_required'})

    item = get_object_or_404(CartItem, id=item_id, cart__user=user)

    try:
        data = json.loads(request.body)
        qty  = int(data.get('quantity', 1))
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'status': 'error', 'message': 'Invalid quantity'})

    if qty < 1:
        item.delete()
        return JsonResponse({'status': 'removed'})

    if item.product and qty > item.product.stock:
        qty = item.product.stock

    item.quantity = qty
    item.save()

    cart = item.cart
    return JsonResponse({
        'status':     'updated',
        'quantity':   item.quantity,
        'subtotal':   float(item.subtotal),
        'cart_total': float(cart.total),
        'item_count': cart.item_count,
    })


def clear_cart(request):
    user = get_session_user(request)
    if not user:
        return JsonResponse({'status': 'login_required'})
    cart = Cart.objects.filter(user=user).first()
    if cart:
        cart.items.all().delete()
    return JsonResponse({'status': 'cleared'})


# ──────────────────────────────────────────────
# CHECKOUT
# ──────────────────────────────────────────────

def checkout(request):
    user = get_session_user(request)
    if not user:
        return redirect('login')
    cart      = Cart.objects.filter(user=user).first()
    addresses = user.addresses.all()
    return render(request, 'checkout.html', {'cart': cart, 'addresses': addresses})


def checkout_initiate(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid method'})

    user = get_session_user(request)
    if not user:
        return JsonResponse({'success': False, 'message': 'Login required'})

    cart = Cart.objects.filter(user=user).first()
    if not cart or cart.item_count == 0:
        return JsonResponse({'success': False, 'message': 'Cart is empty'})

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid request'})

    address_id     = data.get('address_id')
    payment_method = data.get('payment_method', 'esewa')
    coupon_code    = data.get('coupon_code', '').strip().upper()

    address  = get_object_or_404(Address, id=address_id, user=user)
    subtotal = cart.total
    delivery = 0 if subtotal >= 500 else 50
    discount = 0
    coupon   = None

    if coupon_code:
        try:
            coupon = Coupon.objects.get(code=coupon_code)
            if coupon.is_valid():
                discount = coupon.discount_value if coupon.discount_type == 'flat' else (subtotal * coupon.discount_value / 100)
                coupon.used_count += 1
                coupon.save()
            else:
                coupon = None
        except Coupon.DoesNotExist:
            coupon = None

    tax   = round(float(subtotal) * 5 / 100, 2)
    total = round(float(subtotal) + float(delivery) + float(tax) - float(discount), 2)

    order = Order.objects.create(
        user=user, address=address, coupon=coupon,
        payment_method=payment_method,
        subtotal=subtotal, delivery_charge=delivery,
        discount=discount, tax=tax, total=total,
        status='pending', payment_status='pending',
    )

    for item in cart.items.all():
        OrderItem.objects.create(
            order=order, product=item.product,
            name=item.product.name, price=item.product.price,
            quantity=item.quantity,
        )
        item.product.stock -= item.quantity
        item.product.save()

    request.session['pending_order_id'] = order.id
    request.session.save()

    if payment_method == 'esewa':
        return _esewa_payload(request, order, subtotal, tax, total)
    elif payment_method == 'khalti':
        return _khalti_initiate(request, order, total)

    return JsonResponse({'success': False, 'message': 'Unknown payment method'})


# ──────────────────────────────────────────────
# eSEWA
# ──────────────────────────────────────────────

def _esewa_payload(request, order, subtotal, tax, total):
    transaction_uuid = f"{order.id}-{uuid.uuid4().hex[:8]}"
    product_code     = getattr(settings, 'ESEWA_PRODUCT_CODE', 'EPAYTEST')
    secret_key       = getattr(settings, 'ESEWA_SECRET_KEY', '8gBm/:&EnhH.1/q')
    site_url         = getattr(settings, 'SITE_URL', 'http://localhost:8000')

    message   = f"total_amount={total},transaction_uuid={transaction_uuid},product_code={product_code}"
    signature = base64.b64encode(
        hmac.new(secret_key.encode(), message.encode(), hashlib.sha256).digest()
    ).decode()

    order.notes = transaction_uuid
    order.save(update_fields=['notes'])

    return JsonResponse({
        'success': True, 'gateway': 'esewa',
        'amount': str(subtotal), 'tax': str(tax), 'total': str(total),
        'transaction_uuid': transaction_uuid, 'product_code': product_code,
        'signature': signature,
        'success_url': f"{site_url}/pharmacy/payment/esewa/verify/",
        'failure_url': f"{site_url}/pharmacy/payment/esewa/failure/",
    })


def esewa_verify(request):
    encoded_data = request.GET.get('data', '')
    if not encoded_data:
        return redirect('checkout')
    try:
        payment_data = json.loads(base64.b64decode(encoded_data).decode('utf-8'))
    except Exception:
        return _payment_failed(request)

    if payment_data.get('status') != 'COMPLETE':
        return _payment_failed(request)

    try:
        order = Order.objects.get(notes=payment_data.get('transaction_uuid', ''))
    except Order.DoesNotExist:
        return _payment_failed(request)

    verify_url = getattr(settings, 'ESEWA_VERIFY_URL', 'https://rc.esewa.com.np/api/epay/transaction/status/')
    try:
        res = http_requests.get(verify_url, params={
            'product_code':     getattr(settings, 'ESEWA_PRODUCT_CODE', 'EPAYTEST'),
            'transaction_uuid': payment_data.get('transaction_uuid'),
            'total_amount':     payment_data.get('total_amount'),
        }, timeout=10)
        if res.json().get('status') != 'COMPLETE':
            return _payment_failed(request)
    except Exception:
        pass

    return _payment_success(request, order)


def esewa_failure(request):
    return _payment_failed(request)


# ──────────────────────────────────────────────
# KHALTI
# ──────────────────────────────────────────────

def _khalti_initiate(request, order, total):
    secret_key   = getattr(settings, 'KHALTI_SECRET_KEY', 'test_secret_key_f59e8b7d18b4499ca40f68195a846e9b')
    initiate_url = getattr(settings, 'KHALTI_INITIATE_URL', 'https://a.khalti.com/api/v2/epayment/initiate/')
    site_url     = getattr(settings, 'SITE_URL', 'http://localhost:8000')

    try:
        res = http_requests.post(initiate_url, json={
            'return_url':          f"{site_url}/pharmacy/payment/khalti/verify/",
            'website_url':         site_url,
            'amount':              int(float(total) * 100),
            'purchase_order_id':   str(order.id),
            'purchase_order_name': f"HealthMeds Order #{order.id}",
            'customer_info': {
                'name':  order.user.get_full_name(),
                'phone': order.user.mobile,
            }
        }, headers={'Authorization': f'Key {secret_key}'}, timeout=15)
        res_data = res.json()

        if res.status_code == 200 and 'payment_url' in res_data:
            order.notes = res_data.get('pidx', '')
            order.save(update_fields=['notes'])
            return JsonResponse({'success': True, 'gateway': 'khalti', 'payment_url': res_data['payment_url']})

        order.payment_status = 'failed'
        order.save(update_fields=['payment_status'])
        return JsonResponse({'success': False, 'message': res_data.get('detail', 'Khalti initiation failed.')})

    except Exception:
        order.payment_status = 'failed'
        order.save(update_fields=['payment_status'])
        return JsonResponse({'success': False, 'message': 'Could not connect to Khalti.'})


def khalti_verify(request):
    pidx   = request.GET.get('pidx', '')
    status = request.GET.get('status', '')
    oid    = request.GET.get('purchase_order_id', '')

    if status != 'Completed' or not pidx:
        return _payment_failed(request)

    try:
        order = Order.objects.get(id=oid)
    except (Order.DoesNotExist, ValueError):
        return _payment_failed(request)

    secret_key = getattr(settings, 'KHALTI_SECRET_KEY', 'test_secret_key_f59e8b7d18b4499ca40f68195a846e9b')
    verify_url = getattr(settings, 'KHALTI_VERIFY_URL', 'https://a.khalti.com/api/v2/epayment/lookup/')
    try:
        res = http_requests.post(verify_url, json={'pidx': pidx},
                                 headers={'Authorization': f'Key {secret_key}'}, timeout=10)
        if res.json().get('status') != 'Completed':
            return _payment_failed(request)
    except Exception:
        pass

    return _payment_success(request, order)


# ──────────────────────────────────────────────
# PAYMENT SUCCESS / FAILURE
# ──────────────────────────────────────────────

def _payment_success(request, order):
    order.payment_status = 'paid'
    order.status         = 'confirmed'
    order.save(update_fields=['payment_status', 'status'])

    cart = Cart.objects.filter(user=order.user).first()
    if cart:
        cart.items.all().delete()

    Notification.objects.create(
        user    = order.user,
        title   = '✅ Order Confirmed!',
        message = f'Your order #{order.id} has been confirmed. Payment received successfully.'
    )
    request.session.pop('pending_order_id', None)
    return redirect('order_success', order_id=order.id)


def _payment_failed(request, reason='Payment failed.'):
    order_id = request.session.get('pending_order_id')
    if order_id:
        try:
            order = Order.objects.get(id=order_id)
            order.payment_status = 'failed'
            order.save(update_fields=['payment_status'])
            for item in order.items.all():
                if item.product:
                    item.product.stock += item.quantity
                    item.product.save()
        except Order.DoesNotExist:
            pass
        request.session.pop('pending_order_id', None)
    return redirect('checkout')


def order_success(request, order_id):
    user = get_session_user(request)
    if not user:
        return redirect('login')
    order = get_object_or_404(Order, id=order_id, user=user)
    return render(request, 'order_success.html', {'order': order})


# ──────────────────────────────────────────────
# ORDERS
# ──────────────────────────────────────────────

def orders(request):
    user = get_session_user(request)
    if not user:
        return redirect('login')
    return render(request, 'orders.html', {
        'orders': user.orders.all().prefetch_related('items')
    })


def cancel_order(request, order_id):
    user = get_session_user(request)
    if not user:
        return JsonResponse({'status': 'login_required'})
    order = get_object_or_404(Order, id=order_id, user=user)
    if order.status == 'pending':
        order.status = 'cancelled'
        order.save()
        for item in order.items.all():
            if item.product:
                item.product.stock += item.quantity
                item.product.save()
        return JsonResponse({'status': 'cancelled'})
    return JsonResponse({'status': 'error', 'message': 'Cannot cancel this order'})


# ──────────────────────────────────────────────
# SETTINGS
# ──────────────────────────────────────────────

def settings_view(request):
    user = get_session_user(request)
    if not user:
        return redirect('login')
    addresses = user.addresses.all()
    return render(request, 'settings.html', {'addresses': addresses, 'user': user})


def add_address(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error'})
    user = get_session_user(request)
    if not user:
        return JsonResponse({'status': 'login_required'})
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid data'})

    full_name    = data.get('full_name', '').strip()
    phone        = data.get('phone', '').strip()
    address_line = data.get('address_line', '').strip()
    city         = data.get('city', '').strip()
    state        = data.get('state', '').strip()
    pincode      = data.get('pincode', '').strip()
    address_type = data.get('address_type', 'home')

    if not all([full_name, phone, address_line, city, state, pincode]):
        return JsonResponse({'status': 'error', 'message': 'All fields are required'})

    # First address becomes default automatically
    is_default = not user.addresses.exists()

    address = Address.objects.create(
        user=user,
        full_name=full_name,
        phone=phone,
        address_line=address_line,
        city=city,
        state=state,
        pincode=pincode,
        address_type=address_type,
        is_default=is_default,
    )
    return JsonResponse({
        'status': 'ok',
        'address': {
            'id':           address.id,
            'full_name':    address.full_name,
            'phone':        address.phone,
            'address_line': address.address_line,
            'city':         address.city,
            'state':        address.state,
            'pincode':      address.pincode,
            'address_type': address.address_type,
            'is_default':   address.is_default,
        }
    })


def delete_address(request, address_id):
    user = get_session_user(request)
    if not user:
        return JsonResponse({'status': 'login_required'})
    address = get_object_or_404(Address, id=address_id, user=user)
    was_default = address.is_default
    address.delete()
    # If deleted address was default, assign default to next available
    if was_default:
        next_addr = user.addresses.first()
        if next_addr:
            next_addr.is_default = True
            next_addr.save(update_fields=['is_default'])
    return JsonResponse({'status': 'ok'})


def set_default_address(request, address_id):
    user = get_session_user(request)
    if not user:
        return JsonResponse({'status': 'login_required'})
    # Clear all defaults for this user
    user.addresses.update(is_default=False)
    address = get_object_or_404(Address, id=address_id, user=user)
    address.is_default = True
    address.save(update_fields=['is_default'])
    return JsonResponse({'status': 'ok'})


def delete_account(request):
    user = get_session_user(request)
    if not user:
        return JsonResponse({'status': 'login_required'})
    request.session.flush()
    user.delete()
    return JsonResponse({'status': 'ok'})

# ──────────────────────────────────────────────
# ADMIN DASHBOARD
# ──────────────────────────────────────────────

def admin_dashboard(request):
    user = get_session_user(request)
    if not user:
        return redirect('login')
    if not user.is_admin:
        return redirect('index')

    return render(request, 'admin_dashboard.html', {
        'total_orders':   Order.objects.count(),
        'total_revenue':  sum(o.total for o in Order.objects.filter(payment_status='paid')),
        'total_users':    User.objects.count(),
        'total_products': Product.objects.count(),
        'recent_orders':  Order.objects.select_related('user').order_by('-created_at')[:10],
        'low_stock':      Product.objects.filter(stock__lt=10, is_active=True),
        'all_products':   Product.objects.select_related('category').all(),
    })


# ──────────────────────────────────────────────
# APPLY COUPON (AJAX)
# ──────────────────────────────────────────────

def apply_coupon(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        code = data.get('code', '').strip().upper()
        try:
            coupon = Coupon.objects.get(code=code)
            if coupon.is_valid():
                return JsonResponse({
                    'success':        True,
                    'discount_type':  coupon.discount_type,
                    'discount_value': float(coupon.discount_value),
                    'message':        f'Coupon applied! ₹{coupon.discount_value} off'
                })
            return JsonResponse({'success': False, 'message': 'Coupon expired or limit reached'})
        except Coupon.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Invalid coupon code'})


# ──────────────────────────────────────────────
# NOTIFICATIONS (AJAX)
# ──────────────────────────────────────────────

def notifications(request):
    user = get_session_user(request)
    if not user:
        return JsonResponse({'notifications': []})
 
    notifs = user.notifications.all()[:10]
    return JsonResponse({'notifications': [
        {
            'title':      n.title,
            'message':    n.message,
            'is_read':    n.is_read,
            'created_at': n.created_at.strftime('%b %d, %I:%M %p'),
        }
        for n in notifs
    ]})
 


def mark_notifications_read(request):
    user = get_session_user(request)
    if not user:
        return JsonResponse({'status': 'login_required'})
    user.notifications.update(is_read=True)
    return JsonResponse({'status': 'ok'})

# ──────────────────────────────────────────────
# ADD REVIEW
# ──────────────────────────────────────────────

def add_review(request, product_id):
    if request.method == 'POST':
        user = get_session_user(request)
        if not user:
            return redirect('login')
        product = get_object_or_404(Product, id=product_id)
        rating  = int(request.POST.get('rating', 5))
        comment = request.POST.get('comment', '')
        Review.objects.update_or_create(
            user=user, product=product,
            defaults={'rating': rating, 'comment': comment}
        )
    return redirect('product_detail', id=product_id)


# ──────────────────────────────────────────────
# PRESCRIPTION UPLOAD
# ──────────────────────────────────────────────

def prescription_upload(request):
    if request.method == 'POST':
        user = get_session_user(request)
        if not user:
            return JsonResponse({'status': 'error', 'message': 'Login required'})
        image = request.FILES.get('image')
        notes = request.POST.get('notes', '')
        if not image:
            return JsonResponse({'status': 'error', 'message': 'No file uploaded'})
        Prescription.objects.create(user=user, image=image, notes=notes)
        return JsonResponse({'status': 'ok', 'message': 'Prescription uploaded successfully!'})
    return JsonResponse({'status': 'error', 'message': 'Invalid method'})

# ──────────────────────────────────────────────
# ADMIN DASHBOARD
# ──────────────────────────────────────────────

from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth
import json

def admin_dashboard(request):
    user = get_session_user(request)
    if not user:
        return redirect('login')
    if not user.is_admin:
        return redirect('index')

    # ── Stats ──
    total_orders  = Order.objects.count()
    total_revenue = Order.objects.filter(payment_status='paid').aggregate(r=Sum('total'))['r'] or 0
    total_users   = User.objects.count()
    total_products= Product.objects.count()
    pending_orders= Order.objects.filter(status='pending').count()

    # ── Order status breakdown (for pie chart) ──
    status_counts = {
        'confirmed': Order.objects.filter(status='confirmed').count(),
        'shipped':   Order.objects.filter(status='shipped').count(),
        'pending':   Order.objects.filter(status='pending').count(),
        'cancelled': Order.objects.filter(status='cancelled').count(),
    }

    # ── Monthly revenue for bar chart (current year) ──
    from django.utils import timezone
    current_year = timezone.now().year
    monthly_data = (
        Order.objects.filter(payment_status='paid', created_at__year=current_year)
        .annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(total=Sum('total'))
        .order_by('month')
    )
    monthly_revenue = [0] * 12
    for entry in monthly_data:
        monthly_revenue[entry['month'].month - 1] = float(entry['total'])

    # ── Weekly orders (last 7 days) ──
    from datetime import timedelta
    today = timezone.now().date()
    weekly_orders = []
    weekly_labels = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        count = Order.objects.filter(created_at__date=day).count()
        weekly_orders.append(count)
        weekly_labels.append(day.strftime('%a'))

    # ── Top selling products ──
    top_products = (
        OrderItem.objects.values('name')
        .annotate(total_sold=Sum('quantity'))
        .order_by('-total_sold')[:5]
    )
    max_sold = top_products[0]['total_sold'] if top_products else 1

    # ── Recent orders ──
    recent_orders = Order.objects.select_related('user').order_by('-created_at')[:10]

    # ── All orders (for orders tab) ──
    all_orders = Order.objects.select_related('user').prefetch_related('items').order_by('-created_at')

    # ── All products ──
    all_products = Product.objects.select_related('category').order_by('-created_at')

    # ── All users ──
    all_users = User.objects.annotate(order_count=Count('orders')).order_by('-created_at')

    # ── Low stock ──
    low_stock = Product.objects.filter(stock__lt=10, is_active=True)

    return render(request, 'admin_dashboard.html', {
        'total_orders':    total_orders,
        'total_revenue':   total_revenue,
        'total_users':     total_users,
        'total_products':  total_products,
        'pending_orders':  pending_orders,
        'status_counts':   status_counts,
        'monthly_revenue': json.dumps(monthly_revenue),
        'weekly_orders':   json.dumps(weekly_orders),
        'weekly_labels':   json.dumps(weekly_labels),
        'top_products':    top_products,
        'max_sold':        max_sold,
        'recent_orders':   recent_orders,
        'all_orders':      all_orders,
        'all_products':    all_products,
        'all_users':       all_users,
        'low_stock':       low_stock,
    })


# ──────────────────────────────────────────────
# ADMIN AJAX — Update Order Status
# ──────────────────────────────────────────────

def admin_update_order_status(request, order_id):
    user = get_session_user(request)
    if not user or not user.is_admin:
        return JsonResponse({'status': 'forbidden'}, status=403)
    if request.method != 'POST':
        return JsonResponse({'status': 'error'})
    try:
        data      = json.loads(request.body)
        new_status= data.get('status')
        order     = Order.objects.get(id=order_id)
        allowed   = ['pending', 'confirmed', 'shipped', 'delivered', 'cancelled']
        if new_status not in allowed:
            return JsonResponse({'status': 'error', 'message': 'Invalid status'})
        # Restore stock if cancelling
        if new_status == 'cancelled' and order.status != 'cancelled':
            for item in order.items.all():
                if item.product:
                    item.product.stock += item.quantity
                    item.product.save()
        order.status = new_status
        order.save(update_fields=['status'])
        return JsonResponse({'status': 'ok', 'new_status': new_status})
    except Order.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Order not found'})


# ──────────────────────────────────────────────
# ADMIN AJAX — Toggle Product Active
# ──────────────────────────────────────────────

def admin_toggle_product(request, product_id):
    user = get_session_user(request)
    if not user or not user.is_admin:
        return JsonResponse({'status': 'forbidden'}, status=403)
    product = get_object_or_404(Product, id=product_id)
    product.is_active = not product.is_active
    product.save(update_fields=['is_active'])
    return JsonResponse({'status': 'ok', 'is_active': product.is_active})


# ──────────────────────────────────────────────
# ADMIN AJAX — Add Product
# ──────────────────────────────────────────────

def admin_add_product(request):
    user = get_session_user(request)
    if not user or not user.is_admin:
        return JsonResponse({'status': 'forbidden'}, status=403)
    if request.method != 'POST':
        return JsonResponse({'status': 'error'})
    try:
        name        = request.POST.get('name', '').strip()
        category_id = request.POST.get('category_id')
        price       = request.POST.get('price')
        stock       = request.POST.get('stock')
        description = request.POST.get('description', '')
        requires_rx = request.POST.get('requires_rx') == 'true'
        image       = request.FILES.get('image')

        if not all([name, category_id, price, stock]):
            return JsonResponse({'status': 'error', 'message': 'Missing required fields'})

        category = Category.objects.get(id=category_id)
        product  = Product.objects.create(
            name=name, category=category,
            price=price, stock=int(stock),
            description=description,
            requires_rx=requires_rx,
            is_active=True,
        )
        if image:
            product.image = image
            product.save()

        return JsonResponse({
            'status': 'ok',
            'product': {
                'id':       product.id,
                'name':     product.name,
                'category': product.category.name,
                'price':    float(product.price),
                'stock':    product.stock,
            }
        })
    except Category.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Category not found'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})


# ──────────────────────────────────────────────
# ADMIN AJAX — Admin Users List (JSON)
# ──────────────────────────────────────────────

def admin_users_data(request):
    user = get_session_user(request)
    if not user or not user.is_admin:
        return JsonResponse({'status': 'forbidden'}, status=403)
    users = User.objects.annotate(order_count=Count('orders')).order_by('-created_at')
    return JsonResponse({'users': [
        {
            'id':          u.id,
            'name':        u.get_full_name() or u.mobile,
            'mobile':      u.mobile,
            'orders':      u.order_count,
            'joined':      u.created_at.strftime('%b %Y'),
            'is_active':   u.is_active,
        }
        for u in users
    ]})