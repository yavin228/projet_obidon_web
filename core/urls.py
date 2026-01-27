from django.urls import path
from django.contrib.auth.views import LogoutView
from .views import (
    home, login_view, signup_view, account_view, products_view, 
    product_detail_view, product_type_view, cart_view, checkout_view, add_to_cart_ajax, 
    process_payment, payment_success_view
)
from .dashboard_views import dashboard, dashboard_analytics

urlpatterns = [
    path('', home, name='home'),
    path('login/', login_view, name='login'),
    path('signup/', signup_view, name='signup'),
    path('account/', account_view, name='account'),
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),
    path('products/', products_view, name='products'),
    path('products/<str:product_type>/', product_type_view, name='product_type'),
    path('product/<int:product_id>/', product_detail_view, name='product_detail'),
    path('cart/', cart_view, name='cart'),
    path('checkout/', checkout_view, name='checkout'),
    path('checkout/success/', payment_success_view, name='payment_success'),
    path('api/add-to-cart/', add_to_cart_ajax, name='add_to_cart_ajax'),
    path('api/process-payment/', process_payment, name='process_payment'),
    path('admin-dashboard/', dashboard, name='dashboard'),
    path('admin-dashboard/analytics/', dashboard_analytics, name='dashboard_analytics'),
]
