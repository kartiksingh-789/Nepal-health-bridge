from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    User, OTP, Address, Category, Product, ProductImage,
    Review, Wishlist, Cart, CartItem, Coupon,
    Order, OrderItem, Prescription, Notification
)


# ── User ────────────────────────────────────────
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display    = ('mobile', 'first_name', 'last_name', 'email', 'is_active', 'is_admin', 'created_at')
    list_filter     = ('is_active', 'is_admin')
    search_fields   = ('mobile', 'first_name', 'last_name', 'email')
    ordering        = ('-created_at',)
    filter_horizontal = ()
    fieldsets = (
        (None,           {'fields': ('mobile',)}),
        ('Personal Info',{'fields': ('first_name', 'last_name', 'email', 'dob', 'gender')}),
        ('Permissions',  {'fields': ('is_active', 'is_admin', 'is_staff')}),
    )
    add_fieldsets = (
        (None, {'classes': ('wide',), 'fields': ('mobile', 'first_name', 'last_name')}),
    )


# ── OTP ─────────────────────────────────────────
@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    list_display  = ('mobile', 'otp', 'is_used', 'created_at')
    list_filter   = ('is_used',)
    search_fields = ('mobile',)


# ── Address ─────────────────────────────────────
@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display  = ('full_name', 'user', 'address_type', 'city', 'state', 'is_default')
    list_filter   = ('address_type', 'is_default', 'state')
    search_fields = ('full_name', 'user__mobile', 'city')


# ── Category ────────────────────────────────────
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display  = ('name', 'slug', 'is_active', 'created_at')
    list_filter   = ('is_active',)
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


# ── Product ─────────────────────────────────────
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 3

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display   = ('name', 'category', 'brand', 'price', 'original_price', 'stock', 'requires_rx', 'is_active')
    list_filter    = ('category', 'requires_rx', 'is_active')
    search_fields  = ('name', 'brand', 'composition')
    prepopulated_fields = {'slug': ('name',)}
    inlines        = [ProductImageInline]
    list_editable  = ('price', 'stock', 'is_active')


# ── Review ──────────────────────────────────────
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display  = ('product', 'user', 'rating', 'created_at')
    list_filter   = ('rating',)
    search_fields = ('product__name', 'user__mobile')


# ── Wishlist ─────────────────────────────────────
@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display  = ('user', 'product', 'added_at')
    search_fields = ('user__mobile', 'product__name')


# ── Cart ─────────────────────────────────────────
class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'item_count', 'total', 'created_at')
    inlines      = [CartItemInline]


# ── Coupon ───────────────────────────────────────
@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display  = ('code', 'discount_type', 'discount_value', 'used_count', 'max_uses', 'is_active', 'valid_to')
    list_filter   = ('discount_type', 'is_active')
    search_fields = ('code',)
    list_editable = ('is_active',)


# ── Order ────────────────────────────────────────
class OrderItemInline(admin.TabularInline):
    model  = OrderItem
    extra  = 0
    fields = ('product', 'name', 'price', 'quantity')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display   = ('id', 'user', 'status', 'payment_method', 'payment_status', 'total', 'created_at')
    list_filter    = ('status', 'payment_method', 'payment_status')
    search_fields  = ('user__mobile', 'tracking_number')
    list_editable  = ('status', 'payment_status')
    inlines        = [OrderItemInline]
    ordering       = ('-created_at',)


# ── Prescription ─────────────────────────────────
@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display  = ('user', 'status', 'created_at')
    list_filter   = ('status',)
    search_fields = ('user__mobile',)
    list_editable = ('status',)


# ── Notification ─────────────────────────────────
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display  = ('user', 'title', 'is_read', 'created_at')
    list_filter   = ('is_read',)
    search_fields = ('user__mobile', 'title')