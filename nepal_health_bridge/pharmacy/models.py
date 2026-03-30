from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils import timezone


# ──────────────────────────────────────────────
# 1. CUSTOM USER (Mobile OTP based, no password)
# ──────────────────────────────────────────────

class UserManager(BaseUserManager):
    def create_user(self, mobile, **extra_fields):
        if not mobile:
            raise ValueError('Mobile number is required')
        user = self.model(mobile=mobile, **extra_fields)
        user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, mobile, **extra_fields):
        extra_fields.setdefault('is_admin', True)
        extra_fields.setdefault('is_staff', True)
        return self.create_user(mobile, **extra_fields)


class User(AbstractBaseUser):
    mobile      = models.CharField(max_length=15, unique=True)
    first_name  = models.CharField(max_length=50, blank=True)
    last_name   = models.CharField(max_length=50, blank=True)
    email       = models.EmailField(blank=True)
    dob         = models.DateField(null=True, blank=True)
    gender      = models.CharField(max_length=10, blank=True)
    is_active   = models.BooleanField(default=True)
    is_admin    = models.BooleanField(default=False)
    is_staff    = models.BooleanField(default=False)
    created_at  = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD  = 'mobile'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.mobile

    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'.strip() or self.mobile

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return self.is_admin


# ──────────────────────────────────────────────
# 2. OTP (for mobile login)
# ──────────────────────────────────────────────

class OTP(models.Model):
    mobile      = models.CharField(max_length=15)
    otp         = models.CharField(max_length=6)
    created_at  = models.DateTimeField(auto_now_add=True)
    is_used     = models.BooleanField(default=False)

    def is_expired(self):
        # OTP expires after 10 minutes
        return (timezone.now() - self.created_at).seconds > 600

    def __str__(self):
        return f'{self.mobile} - {self.otp}'


# ──────────────────────────────────────────────
# 3. ADDRESS
# ──────────────────────────────────────────────

class Address(models.Model):
    ADDRESS_TYPES = [
        ('home',   'Home'),
        ('office', 'Office'),
        ('other',  'Other'),
    ]
    user         = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    address_type = models.CharField(max_length=10, choices=ADDRESS_TYPES, default='home')
    full_name    = models.CharField(max_length=100)
    phone        = models.CharField(max_length=15)
    address_line = models.TextField()
    city         = models.CharField(max_length=50)
    state        = models.CharField(max_length=50)
    pincode      = models.CharField(max_length=10)
    is_default   = models.BooleanField(default=False)
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Addresses'

    def __str__(self):
        return f'{self.full_name} - {self.city}'


# ──────────────────────────────────────────────
# 4. CATEGORY
# ──────────────────────────────────────────────

class Category(models.Model):
    name       = models.CharField(max_length=100)
    slug       = models.SlugField(unique=True)
    icon       = models.CharField(max_length=50, blank=True)  # FontAwesome class
    image      = models.ImageField(upload_to='categories/', blank=True, null=True)
    is_active  = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


# ──────────────────────────────────────────────
# 5. PRODUCT
# ──────────────────────────────────────────────

class Product(models.Model):
    category        = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products')
    name            = models.CharField(max_length=200)
    slug            = models.SlugField(unique=True)
    brand           = models.CharField(max_length=100, blank=True)
    description     = models.TextField(blank=True)
    composition     = models.CharField(max_length=200, blank=True)
    form            = models.CharField(max_length=50, blank=True)   # Tablet, Syrup, etc.
    strength        = models.CharField(max_length=50, blank=True)   # 500mg, etc.
    pack_size       = models.CharField(max_length=50, blank=True)   # 10 Tablets
    manufacturer    = models.CharField(max_length=100, blank=True)
    price           = models.DecimalField(max_digits=10, decimal_places=2)
    original_price  = models.DecimalField(max_digits=10, decimal_places=2)
    stock           = models.PositiveIntegerField(default=0)
    image           = models.ImageField(upload_to='products/', blank=True, null=True)
    requires_rx     = models.BooleanField(default=False)   # Prescription required
    is_active       = models.BooleanField(default=True)
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    @property
    def discount_percent(self):
        if self.original_price > 0:
            return int(((self.original_price - self.price) / self.original_price) * 100)
        return 0

    @property
    def is_in_stock(self):
        return self.stock > 0

    @property
    def average_rating(self):
        reviews = self.reviews.all()
        if reviews.exists():
            return round(sum(r.rating for r in reviews) / reviews.count(), 1)
        return 0


# ──────────────────────────────────────────────
# 6. PRODUCT IMAGE (multiple images per product)
# ──────────────────────────────────────────────

class ProductImage(models.Model):
    product    = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image      = models.ImageField(upload_to='products/gallery/')
    is_primary = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.product.name} - image'


# ──────────────────────────────────────────────
# 7. PRODUCT REVIEW
# ──────────────────────────────────────────────

class Review(models.Model):
    product    = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user       = models.ForeignKey(User, on_delete=models.CASCADE)
    rating     = models.PositiveSmallIntegerField()   # 1 to 5
    comment    = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('product', 'user')  # One review per user per product

    def __str__(self):
        return f'{self.user.mobile} - {self.product.name} - {self.rating}★'


# ──────────────────────────────────────────────
# 8. WISHLIST
# ──────────────────────────────────────────────

class Wishlist(models.Model):
    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist')
    product    = models.ForeignKey(Product, on_delete=models.CASCADE)
    added_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')  # No duplicates

    def __str__(self):
        return f'{self.user.mobile} - {self.product.name}'


# ──────────────────────────────────────────────
# 9. CART
# ──────────────────────────────────────────────

class Cart(models.Model):
    user       = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Cart of {self.user.mobile}'

    @property
    def total(self):
        return sum(item.subtotal for item in self.items.all())

    @property
    def item_count(self):
        return self.items.count()


class CartItem(models.Model):
    cart       = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product    = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity   = models.PositiveIntegerField(default=1)
    added_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('cart', 'product')

    def __str__(self):
        return f'{self.product.name} x {self.quantity}'

    @property
    def subtotal(self):
        return self.product.price * self.quantity


# ──────────────────────────────────────────────
# 10. COUPON
# ──────────────────────────────────────────────

class Coupon(models.Model):
    code           = models.CharField(max_length=20, unique=True)
    discount_type  = models.CharField(max_length=10, choices=[('flat', 'Flat'), ('percent', 'Percent')])
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    min_order      = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    max_uses       = models.PositiveIntegerField(default=100)
    used_count     = models.PositiveIntegerField(default=0)
    is_active      = models.BooleanField(default=True)
    valid_from     = models.DateTimeField()
    valid_to       = models.DateTimeField()

    def __str__(self):
        return self.code

    def is_valid(self):
        now = timezone.now()
        return self.is_active and self.valid_from <= now <= self.valid_to and self.used_count < self.max_uses


# ──────────────────────────────────────────────
# 11. ORDER
# ──────────────────────────────────────────────

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending',   'Pending'),
        ('confirmed', 'Confirmed'),
        ('shipped',   'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    PAYMENT_METHODS = [
        ('khalti',     'Khalti'),
        ('esewa',      'eSewa'),
        ('netbanking', 'Nepal Bank Transfer'),
        ('card',       'Credit/Debit Card'),
        ('cod',        'Cash on Delivery'),
    ]
    PAYMENT_STATUS = [
        ('pending', 'Pending'),
        ('paid',    'Paid'),
        ('failed',  'Failed'),
        ('refunded','Refunded'),
    ]

    user              = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    address           = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True)
    coupon            = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)
    status            = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_method    = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    payment_status    = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    subtotal          = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_charge   = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount          = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax               = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total             = models.DecimalField(max_digits=10, decimal_places=2)
    tracking_number   = models.CharField(max_length=50, blank=True)
    notes             = models.TextField(blank=True)
    created_at        = models.DateTimeField(auto_now_add=True)
    updated_at        = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Order #{self.id} by {self.user.mobile}'


class OrderItem(models.Model):
    order      = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product    = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    name       = models.CharField(max_length=200)   # snapshot of product name
    price      = models.DecimalField(max_digits=10, decimal_places=2)  # snapshot of price
    quantity   = models.PositiveIntegerField()

    def __str__(self):
        return f'{self.name} x {self.quantity}'

    @property
    def subtotal(self):
        return self.price * self.quantity


# ──────────────────────────────────────────────
# 12. PRESCRIPTION
# ──────────────────────────────────────────────

class Prescription(models.Model):
    STATUS_CHOICES = [
        ('pending',  'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='prescriptions')
    image      = models.ImageField(upload_to='prescriptions/')
    notes      = models.TextField(blank=True)
    status     = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Prescription by {self.user.mobile} - {self.status}'


# ──────────────────────────────────────────────
# 13. NOTIFICATION
# ──────────────────────────────────────────────

class Notification(models.Model):
    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title      = models.CharField(max_length=100)
    message    = models.TextField()
    is_read    = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.mobile} - {self.title}'