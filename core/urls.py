from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # ================= PAGES PRINCIPALES =================
    path('', views.home, name='home'),
    path('products/', views.products_view, name='products'),
    # Attention: Cette URL doit correspondre au slug du ProductType (ex: /products/cafe/)
    path('products/<str:product_type>/', views.product_type_view, name='product_type'),
    path('product/<int:product_id>/', views.product_detail_view, name='product_detail'),
    
    # ================= PANIER (CART) =================
    path('cart/', views.cart_view, name='cart'),
    
    # URLs API pour le panier (AJAX)
    # Correspond exactement au fetch('/api/cart/update/') dans cart.js
    path('api/cart/update/', views.api_cart_update, name='api_cart_update'),
    
    # Correspond exactement au fetch('/api/cart-count/') dans cart.js
    path('api/cart-count/', views.api_cart_count, name='api_cart_count'),
    
    # Ancienne URL d'ajout simple (gardée par sécurité si utilisée ailleurs, mais api_cart_update est préférée)
    path('cart/add/', views.add_to_cart_ajax, name='add_to_cart'),
    
    # ================= CHECKOUT & PAIEMENT =================
    path('checkout/', views.checkout_view, name='checkout'),
    path('payment/process/', views.process_payment, name='process_payment'),
    path('payment/success/', views.payment_success_view, name='payment_success'),
    
    # ================= COMPTE UTILISATEUR =================
    path('account/', views.account_view, name='account'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    # Déconnexion (si tu n'utilises pas allauth uniquement)
    path('logout/', views.logout_view, name='logout'),
    
    # ================= DEVISES =================
    path('currency/update/', views.update_currency_preference, name='update_currency'),
    path('api/exchange-rates/', views.api_exchange_rates, name='api_exchange_rates'),
    path('api/convert-price/', views.api_convert_price, name='api_convert_price'),
    
    # ================= AVIS PRODUITS =================
    path('review/add/<int:product_id>/', views.add_review, name='add_review'),
    
    # ================= DASHBOARD ADMIN =================
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('dashboard/analytics/', views.dashboard_analytics_view, name='dashboard_analytics'),
    
    # ================= DEBUG (Optionnel - À retirer en production) =================
    path('debug/session/', views.debug_session, name='debug_session'),
]

    
   