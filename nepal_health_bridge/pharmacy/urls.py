from django.urls import path
from . import views

urlpatterns = [
    # ── Main Pages ───────────────────────────────
    path('',                          views.index,                  name='index'),
    path('products/',                 views.products,               name='products'),
    path('product/<int:id>/',         views.product_detail,         name='product_detail'),
    path('product/<int:product_id>/review/', views.add_review,     name='add_review'),
    # ── Auth ─────────────────────────────────────
    path('login/',                    views.login_view,             name='login'),
    path('logout/',                   views.logout_view,            name='logout'),
    # ── User Pages ───────────────────────────────
    path('profile/',                  views.profile,                name='profile'),
    path('orders/',                   views.orders,                 name='orders'),
    path('wishlist/',                 views.wishlist,               name='wishlist'),
    path('settings/',                 views.settings_view,          name='settings'),
    path('checkout/',                 views.checkout,               name='checkout'),
    # ── Admin ────────────────────────────────────
    path('dashboard/',                views.admin_dashboard,        name='admin_dashboard'),
    # ── Cart AJAX ────────────────────────────────
    path('cart/add/<int:product_id>/',    views.add_to_cart,        name='add_to_cart'),
    path('cart/remove/<int:item_id>/',    views.remove_from_cart,   name='remove_from_cart'),
    path('cart/update/<int:item_id>/',    views.update_cart_qty,    name='update_cart_qty'),
    path('cart/data/',                    views.cart_data,          name='cart_data'),
    path('cart/clear/',                   views.clear_cart,         name='clear_cart'),
    # ── Other AJAX ───────────────────────────────
    path('wishlist/toggle/<int:product_id>/', views.toggle_wishlist,         name='toggle_wishlist'),
    path('order/cancel/<int:order_id>/',      views.cancel_order,            name='cancel_order'),
    path('coupon/apply/',                     views.apply_coupon,            name='apply_coupon'),
    path('notifications/',                    views.notifications,           name='notifications'),
    path('notifications/read/',               views.mark_notifications_read, name='mark_notifications_read'),
    # ── Checkout & Payment ────────────────────────
    path('checkout/initiate/',                views.checkout_initiate,       name='checkout_initiate'),
    path('payment/esewa/verify/',             views.esewa_verify,            name='esewa_verify'),
    path('payment/esewa/failure/',            views.esewa_failure,           name='esewa_failure'),
    path('payment/khalti/verify/',            views.khalti_verify,           name='khalti_verify'),
    path('order/success/<int:order_id>/',     views.order_success,           name='order_success'),
    path('prescription/upload/',              views.prescription_upload,     name='prescription_upload'),

    # ── Admin AJAX ───────────────────────────────
path('admin/order/<int:order_id>/status/',  views.admin_update_order_status, name='admin_update_order_status'),
path('admin/product/add/',                  views.admin_add_product,         name='admin_add_product'),
path('admin/product/<int:product_id>/toggle/', views.admin_toggle_product,  name='admin_toggle_product'),
path('admin/users/data/',                   views.admin_users_data,          name='admin_users_data'),

# ── Settings AJAX ─────────────────────────────
path('settings/address/add/',                views.add_address,          name='add_address'),
path('settings/address/<int:address_id>/delete/', views.delete_address,  name='delete_address'),
path('settings/address/<int:address_id>/default/', views.set_default_address, name='set_default_address'),
path('settings/account/delete/',             views.delete_account,        name='delete_account'),
]