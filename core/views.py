from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from allauth.socialaccount.models import SocialApp
from django.db.models import Sum, Q, Count
from django.utils import timezone
from decimal import Decimal
import json
from django.contrib.auth.views import LoginView


# Imports des modèles
from .models import (
    Category, Product, Order, Review, Currency, 
    UserCurrencyPreference, User, OrderItem, ProductType
)

from core.currency_service import CurrencyConverter, get_user_currency
from .forms import ReviewForm


def home(request):
    """
    Page d'accueil 100% dynamique.
    Génère les sections basées sur les Types de Produits actifs définis dans l'admin.
    """
    # 1. Récupérer tous les TYPES DE PRODUITS actifs qui ont au moins une catégorie à afficher
    active_types = ProductType.objects.filter(
        is_active=True,
        products__category__display_on_home=True
    ).distinct().order_by('name')
    
    # 2. Construire les sections dynamiquement
    dynamic_sections = {}
    
    for p_type in active_types:
        categories = Category.objects.filter(
            is_active=True,
            display_on_home=True,
            products__product_type=p_type
        ).distinct().order_by('home_position', 'name')
        
        if categories.exists():
            dynamic_sections[p_type.slug] = {
                'name': p_type.name,
                'icon': p_type.icon,
                'categories': categories
            }
    
    # 3. Produits en vedette
    featured_products = Product.objects.filter(
        is_active=True, 
        is_featured=True
    ).select_related('category')[:8]
    
    # 4. Récupérer les filtres principaux pour la navbar
    all_filters = Category.objects.filter(
        is_active=True, 
        is_filter_main=True
    ).order_by('home_position')
    
    context = {
        'featured_products': featured_products,
        'dynamic_sections': dynamic_sections,
        'all_filters': all_filters,
    }
    
    return render(request, 'home.html', context)


def products_view(request):
    """Products listing page with filters"""
    products = Product.objects.filter(is_active=True).select_related('category', 'product_type')
    categories = Category.objects.filter(is_active=True)
    
    # Filter by category
    category_param = request.GET.get('category')
    selected_category = None
    if category_param:
        try:
            selected_category = Category.objects.get(slug=category_param)
            products = products.filter(category=selected_category)
        except (ValueError, Category.DoesNotExist):
            selected_category = Category.objects.filter(name__iexact=category_param).first()
            if selected_category:
                products = products.filter(category=selected_category)
    
    # Filter by price range (FCFA)
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        products = products.filter(price_fcfa__gte=min_price)
    if max_price:
        products = products.filter(price_fcfa__lte=max_price)
    
    # Search
    query = request.GET.get('q')
    if query:
        products = products.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query)
        )
    
    # Sorting
    sort_by = request.GET.get('sort', '-created_at')
    if sort_by == 'price':
        sort_by = 'price_fcfa'
    elif sort_by == '-price':
        sort_by = '-price_fcfa'
    products = products.order_by(sort_by)
    
    context = {
        'products': products,
        'categories': categories,
        'selected_category': selected_category,
        'query': query
    }
    return render(request, 'products.html', context)


def product_type_view(request, type_slug):
    """View products by dynamic product type."""
    p_type = get_object_or_404(ProductType, slug=type_slug, is_active=True)
    
    products = Product.objects.filter(
        product_type=p_type,
        is_active=True
    ).select_related('category')
    
    sub_categories = Category.objects.filter(
        products__product_type=p_type,
        is_active=True
    ).distinct()
    
    query = request.GET.get('q')
    if query:
        products = products.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query)
        )
    
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        products = products.filter(price_fcfa__gte=min_price)
    if max_price:
        products = products.filter(price_fcfa__lte=max_price)
    
    sort_by = request.GET.get('sort', '-created_at')
    if sort_by == 'price':
        sort_by = 'price_fcfa'
    elif sort_by == '-price':
        sort_by = '-price_fcfa'
    products = products.order_by(sort_by)
    
    context = {
        'products': products,
        'product_type': p_type,
        'product_type_display': p_type.name,
        'sub_categories': sub_categories,
        'query': query
    }
    return render(request, 'product_type.html', context)


def product_detail_view(request, product_id):
    """Product detail page with gestion des devises"""
    product = get_object_or_404(Product, id=product_id, is_active=True)
    reviews = product.reviews.select_related('user').all()
    related_products = Product.objects.filter(
        category=product.category, 
        is_active=True
    ).exclude(id=product_id)[:4]
    
    has_reviewed = False
    if request.user.is_authenticated:
        has_reviewed = Review.objects.filter(product=product, user=request.user).exists()
    
    try:
        price_eur = product.get_price_in_currency('EUR')
    except Exception as e:
        print(f"Erreur de conversion EUR: {e}")
        price_eur = product.price_fcfa / Decimal('655.957')
    
    context = {
        'product': product,
        'reviews': reviews,
        'related_products': related_products,
        'average_rating': product.rating if product.rating else 0,
        'has_reviewed': has_reviewed,
        'review_form': ReviewForm() if request.user.is_authenticated and not has_reviewed else None,
        'price_eur': price_eur,
    }
    return render(request, 'product_detail.html', context)


def cart_view(request):
    """Shopping cart page"""
    cart_items = request.session.get('cart', {})
    total_price_fcfa = Decimal('0')
    items = []
    
    for product_id, quantity in cart_items.items():
        try:
            product = Product.objects.get(id=product_id)
            item_total_fcfa = product.price_fcfa * Decimal(quantity)
            total_price_fcfa += item_total_fcfa
            items.append({
                'product': product,
                'quantity': quantity,
                'total_fcfa': item_total_fcfa,
                'total': item_total_fcfa
            })
        except Product.DoesNotExist:
            pass
    
    tax_fcfa = (total_price_fcfa * Decimal('0.20')).quantize(Decimal('0.01'))
    total_amount_fcfa = total_price_fcfa + tax_fcfa
    
    context = {
        'cart_items': items,
        'total_price_fcfa': total_price_fcfa,
        'total_price': total_price_fcfa,
        'tax_fcfa': tax_fcfa,
        'total_amount_fcfa': total_amount_fcfa,
        'cart_count': len(cart_items)
    }
    return render(request, 'cart.html', context)


@csrf_exempt
@require_POST
def add_to_cart_ajax(request):
    """AJAX endpoint to add product to cart"""
    try:
        data = json.loads(request.body)
        product_id = data.get('product_id')
        quantity = int(data.get('quantity', 1))
        
        try:
            product = Product.objects.get(id=product_id, is_active=True)
            
            cart = request.session.get('cart', {})
            product_id_str = str(product_id)
            
            if product_id_str in cart:
                cart[product_id_str] += quantity
            else:
                cart[product_id_str] = quantity
            
            request.session['cart'] = cart
            request.session.modified = True
            
            item_total_fcfa = product.price_fcfa * quantity
            
            return JsonResponse({
                'success': True,
                'message': f'{product.name} ajouté au panier!',
                'cart_count': sum(cart.values()),
                'product_name': product.name,
                'item_total_fcfa': str(item_total_fcfa),
                'item_total_formatted': f"{item_total_fcfa:,.0f} FCFA".replace(',', ' ')
            })
        except Product.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Produit non trouvé'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Erreur: {str(e)}'}, status=400)


def checkout_view(request):
    """Checkout page"""
    cart_items = request.session.get('cart', {})
    
    if not cart_items:
        return redirect('cart')
    
    total_price_fcfa = Decimal('0')
    items = []
    
    for product_id, quantity in cart_items.items():
        try:
            product = Product.objects.get(id=product_id)
            item_total_fcfa = product.price_fcfa * Decimal(quantity)
            total_price_fcfa += item_total_fcfa
            items.append({
                'product': product,
                'quantity': quantity,
                'total_fcfa': item_total_fcfa
            })
        except Product.DoesNotExist:
            pass
    
    shipping_method = request.POST.get('shipping', 'standard')
    shipping_costs_fcfa = {
        'standard': Decimal('0'),
        'express': Decimal('6559.60'),
        'overnight': Decimal('13119.20')
    }
    shipping_cost_fcfa = shipping_costs_fcfa.get(shipping_method, Decimal('0'))
    
    tax_fcfa = (total_price_fcfa * Decimal('0.20')).quantize(Decimal('0.01'))
    final_total_fcfa = (total_price_fcfa + shipping_cost_fcfa + tax_fcfa).quantize(Decimal('0.01'))
    
    context = {
        'cart_items': items,
        'total_price_fcfa': total_price_fcfa,
        'shipping_cost_fcfa': shipping_cost_fcfa,
        'tax_fcfa': tax_fcfa,
        'final_total_fcfa': final_total_fcfa,
        'total_amount_fcfa': final_total_fcfa,
        'user_addresses': [],
    }
    return render(request, 'checkout.html', context)


@csrf_exempt
@require_POST
def process_payment(request):
    """AJAX endpoint to process payment"""
    try:
        data = json.loads(request.body)
        cart_items = request.session.get('cart', {})
        
        if not cart_items:
            return JsonResponse({'success': False, 'message': 'Panier vide'}, status=400)
        
        total_price_fcfa = Decimal('0')
        for product_id, quantity in cart_items.items():
            try:
                product = Product.objects.get(id=product_id)
                total_price_fcfa += product.price_fcfa * Decimal(quantity)
            except Product.DoesNotExist:
                pass
        
        shipping_method = data.get('shipping_method', 'standard')
        shipping_costs_fcfa = {
            'standard': Decimal('0'),
            'express': Decimal('6559.60'),
            'overnight': Decimal('13119.20')
        }
        shipping_cost_fcfa = shipping_costs_fcfa.get(shipping_method, Decimal('0'))
        
        tax_fcfa = (total_price_fcfa * Decimal('0.20')).quantize(Decimal('0.01'))
        final_total_fcfa = (total_price_fcfa + shipping_cost_fcfa + tax_fcfa).quantize(Decimal('0.01'))
        
        first_name = data.get('first_name', 'Guest')
        last_name = data.get('last_name', '')
        email = data.get('email', '')
        phone = data.get('phone', '')
        address = data.get('address', '')
        city = data.get('city', '')
        postal_code = data.get('postal_code', '')
        
        order = None
        if request.user.is_authenticated:
            fcfa_currency = Currency.objects.get(code='XOF')
            
            order = Order.objects.create(
                user=request.user,
                total_amount=final_total_fcfa,
                total_amount_fcfa=final_total_fcfa,
                status='pending',
                currency_used=fcfa_currency,
                shipping_address=f"{address}, {city} {postal_code}",
                billing_address=f"{address}, {city} {postal_code}",
                payment_method='card',
                payment_status='pending'
            )
            
            for product_id, quantity in cart_items.items():
                try:
                    product = Product.objects.get(id=product_id)
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=quantity,
                        price_fcfa=product.price_fcfa,
                        total_fcfa=product.price_fcfa * quantity
                    )
                except Product.DoesNotExist:
                    pass
        
        request.session['cart'] = {}
        request.session.modified = True
        
        return JsonResponse({
            'success': True,
            'message': 'Commande créée avec succès',
            'order_id': order.id if order else None,
            'total': str(final_total_fcfa),
            'total_formatted': f"{final_total_fcfa:,.0f} FCFA".replace(',', ' ')
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)


def payment_success_view(request):
    """Payment success page"""
    return render(request, 'payment_success.html')


@login_required
def account_view(request):
    """Gère l'affichage du profil ET la mise à jour des infos personnelles"""
    user_currency_code = get_user_currency(request)
    
    # --- GESTION DE LA MISE À JOUR DU PROFIL (POST) ---
    if request.method == 'POST':
        # Vérifier si c'est une mise à jour de profil (et non un autre formulaire)
        if 'update_profile' in request.POST:
            first_name = request.POST.get('first_name', '')
            last_name = request.POST.get('last_name', '')
            email = request.POST.get('email', '')
            
            request.user.first_name = first_name
            request.user.last_name = last_name
            request.user.email = email
            request.user.save()
            
            messages.success(request, "✅ Vos informations ont été mises à jour avec succès !")
            return redirect('core:account')

    # --- CALCUL DES DONNÉES DYNAMIQUES (GET) ---
    total_spent_fcfa = Decimal('0')
    recent_orders_data = []
    total_orders_count = 0
    
    if hasattr(request.user, 'orders'):
        # Total dépensé
        total_spent_fcfa = request.user.orders.aggregate(
            total=Sum('total_amount_fcfa')
        )['total'] or Decimal('0')
        
        # Compteur
        total_orders_count = request.user.orders.count()
        
        # Dernières commandes (pour l'aperçu et l'onglet)
        orders_qs = request.user.orders.select_related('currency_used').order_by('-created_at')[:5]
        
        for order in orders_qs:
            converted_data = CurrencyConverter.convert_price(
                float(order.total_amount_fcfa), 'XOF', user_currency_code
            )
            recent_orders_data.append({
                'order': order,
                'items': order.items.all(), # Précharger les items si possible pour perf
                'converted_amount': converted_data['amount'],
                'formatted_amount': converted_data['formatted'],
                'symbol': converted_data['symbol'],
                'status_display': order.get_status_display()
            })
    
    # Conversion du total global
    total_spent_converted = CurrencyConverter.convert_price(
        float(total_spent_fcfa), 'XOF', user_currency_code
    )
    
    # Points de fidélité (1 pt = 1000 FCFA)
    loyalty_points = int(total_spent_fcfa / Decimal('1000'))
    
    # Wishlist (Placeholder pour l'instant)
    wishlist_count = 0 
    
    context = {
        'total_orders_count': total_orders_count,
        'total_spent_formatted': total_spent_converted['formatted'],
        'total_spent_symbol': total_spent_converted['symbol'],
        'loyalty_points': loyalty_points,
        'wishlist_count': wishlist_count,
        'recent_orders': recent_orders_data,
        'user_currency': user_currency_code,
        'CURRENCY_SYMBOL': CurrencyConverter.SUPPORTED_CURRENCIES.get(user_currency_code, {}).get('symbol', 'FCFA'),
    }
    
    return render(request, 'profile.html', context)

def login_view(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('core:dashboard')
        return redirect('core:account')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        next_url = request.POST.get('next', 'account')
        
        try:
            user = authenticate(request, username=email, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f'Bienvenue {user.first_name or user.username}! 👋')
                return redirect(next_url)
            else:
                messages.error(request, 'Email ou mot de passe invalide.')
        except Exception as e:
            messages.error(request, 'Une erreur est survenue lors de la connexion.')
    
    try:
        google_app = SocialApp.objects.get(provider='google')
    except SocialApp.DoesNotExist:
        google_app = None
    
    context = {'google_app': google_app}
    return render(request, 'login.html', context)


def signup_view(request):
    """View for user registration"""
    if request.user.is_authenticated:
        return redirect('account')
    
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        
        if not email or not password:
            messages.error(request, 'Email et mot de passe sont requis.')
            return render(request, 'signup.html')
        
        if password != password_confirm:
            messages.error(request, 'Les mots de passe ne correspondent pas.')
            return render(request, 'signup.html')
        
        if User.objects.filter(username=email).exists():
            messages.error(request, 'Un compte avec cet email existe déjà.')
            return render(request, 'signup.html')
        
        try:
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            messages.success(request, 'Compte créé avec succès ! Veuillez vous connecter.')
            return redirect('login')
        except Exception as e:
            messages.error(request, f'Erreur lors de la création du compte: {str(e)}')
    
    try:
        google_app = SocialApp.objects.get(provider='google')
    except SocialApp.DoesNotExist:
        google_app = None
    
    context = {'google_app': google_app}
    return render(request, 'signup.html', context)


def update_currency_preference(request):
    """Update user's currency preference"""
    if request.method == 'POST':
        currency_code = request.POST.get('currency')
        SUPPORTED_CURRENCIES = ['XOF', 'USD', 'EUR']
        
        if currency_code not in SUPPORTED_CURRENCIES:
            messages.error(request, "Devise invalide")
            return redirect(request.META.get('HTTP_REFERER', 'account'))

        if not request.user.is_authenticated:
            request.session['preferred_currency'] = currency_code
            request.session.modified = True
            messages.success(request, f"Devise mise à jour: {currency_code}")
            return redirect(request.META.get('HTTP_REFERER', 'home'))

        try:
            currency, _ = Currency.objects.get_or_create(
                code=currency_code,
                defaults={'name': currency_code, 'symbol': currency_code, 'is_default': False}
            )
            preference, _ = UserCurrencyPreference.objects.get_or_create(user=request.user)
            preference.preferred_currency = currency
            preference.save()
            messages.success(request, f"Devise mise à jour: {currency_code}")
        except Exception as e:
            messages.error(request, f"Erreur: {str(e)}")
    
    return redirect(request.META.get('HTTP_REFERER', 'account'))


def api_exchange_rates(request):
    """API pour récupérer les taux de change"""
    base_currency = request.GET.get('base', 'XOF')
    try:
        rates_data = CurrencyConverter.get_exchange_rates(base_currency)
        return JsonResponse({'success': True, 'data': rates_data})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


def api_convert_price(request):
    """API pour convertir un prix"""
    try:
        amount = float(request.GET.get('amount', 0))
        from_currency = request.GET.get('from', 'XOF')
        to_currency = request.GET.get('to', 'USD')
        
        result = CurrencyConverter.convert_price(amount, from_currency, to_currency)
        
        return JsonResponse({
            'success': True,
            'data': {
                'amount': str(result['amount']),
                'formatted': result['formatted'],
                'symbol': result['symbol'],
                'code': result['code']
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


def currency_context(request):
    """Context processor pour la devise"""
    user_currency = get_user_currency(request)
    currencies = CurrencyConverter.SUPPORTED_CURRENCIES
    
    return {
        'user_currency': user_currency,
        'CURRENCY_SYMBOL': currencies.get(user_currency, {}).get('symbol', 'FCFA'),
        'CURRENCY_CODE': user_currency,
        'currencies': currencies,
        'currency_config': currencies.get(user_currency, {})
    }
    

@login_required
def add_review(request, product_id):
    """Ajouter un avis sur un produit"""
    product = get_object_or_404(Product, id=product_id, is_active=True)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.is_verified = True
            review.save()
            
            reviews = product.reviews.all()
            if reviews.exists():
                total_rating = reviews.aggregate(total=Sum('rating'))['total'] or Decimal('0')
                average_rating = total_rating / reviews.count()
                product.rating = float(average_rating)
                product.reviews_count = reviews.count()
                product.save()
            
            messages.success(request, "✅ Merci pour votre avis ! Il a été publié avec succès.")
            return redirect('core:product_detail', product_id=product.id)
        else:
            messages.error(request, "❌ Veuillez corriger les erreurs dans le formulaire.")
            return redirect('core:product_detail', product_id=product.id)
    
    return redirect('core:product_detail', product_id=product.id)


@login_required
def dashboard_analytics_view(request):
    """Analytics dashboard"""
    if not request.user.is_staff:
        return redirect('core:home')
    
    total_customers = User.objects.count()
    thirty_days_ago = timezone.now() - timezone.timedelta(days=30)
    new_customers = User.objects.filter(date_joined__gte=thirty_days_ago).count()
    
    delivered_orders = Order.objects.filter(status='delivered')
    total_revenue = delivered_orders.aggregate(total=Sum('total_amount_fcfa'))['total'] or Decimal('0.00')
    total_orders_count = delivered_orders.count()
    avg_order_value = total_revenue / total_orders_count if total_orders_count > 0 else Decimal('0.00')
    
    best_rated = Product.objects.filter(is_active=True, reviews_count__gt=0).order_by('-rating', '-reviews_count')[:5]
    most_reviewed = Product.objects.filter(is_active=True).order_by('-reviews_count')[:5]
    
    total_revenue_fcfa = Order.objects.filter(status='delivered').aggregate(total=Sum('total_amount_fcfa'))['total'] or Decimal('0.00')
    
    today = timezone.now()
    start_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    revenue_this_month_fcfa = Order.objects.filter(
        status='delivered',
        created_at__gte=start_of_month
    ).aggregate(total=Sum('total_amount_fcfa'))['total'] or Decimal('0.00')
    
    context = {
        'total_customers': total_customers,
        'new_customers': new_customers,
        'avg_order_value': avg_order_value,
        'best_rated': best_rated,
        'most_reviewed': most_reviewed,
        'total_revenue_fcfa': total_revenue_fcfa,
        'revenue_this_month_fcfa': revenue_this_month_fcfa,
        'total_products': Product.objects.count(),
        'total_orders': Order.objects.count(),
    }
    
    return render(request, 'dashboard_analytics.html', context)


@login_required
def dashboard_view(request):
    """Dashboard admin avec statistiques"""
    if not request.user.is_staff:
        return redirect('core:home')
    
    total_revenue_fcfa = Order.objects.filter(status='delivered').aggregate(total=Sum('total_amount_fcfa'))['total'] or Decimal('0.00')
    
    today = timezone.now()
    start_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    revenue_this_month_fcfa = Order.objects.filter(
        status='delivered',
        created_at__gte=start_of_month
    ).aggregate(total=Sum('total_amount_fcfa'))['total'] or Decimal('0.00')
    
    recent_orders = Order.objects.select_related('user').order_by('-created_at')[:10]
    
    top_products = Product.objects.filter(is_active=True).annotate(
        delivered_count=Count('orderitem', filter=Q(orderitem__order__status='delivered'))
    ).order_by('-reviews_count')[:5]
    
    orders_by_status = Order.objects.values('status').annotate(count=Count('id')).order_by('status')
    total_orders_count = Order.objects.count()
    
    avg_order_value = total_revenue_fcfa / Decimal(total_orders_count) if total_orders_count > 0 else Decimal('0.00')
    
    monthly_revenue = []
    monthly_labels = []
    for i in range(5, -1, -1):
        month_start = (today.replace(day=1) - timezone.timedelta(days=30*i)).replace(day=1)
        month_end = (month_start + timezone.timedelta(days=32)).replace(day=1)
        revenue = Order.objects.filter(
            status='delivered',
            created_at__gte=month_start,
            created_at__lt=month_end
        ).aggregate(total=Sum('total_amount_fcfa'))['total'] or Decimal('0')
        monthly_revenue.append(float(revenue))
        monthly_labels.append(month_start.strftime('%b %Y'))
    
    status_data = {'labels': [], 'data': [], 'colors': []}
    status_colors = {
        'delivered': '#28a745', 'shipped': '#17a2b8', 'confirmed': '#ffc107',
        'pending': '#6c757d', 'cancelled': '#dc3545'
    }
    status_display_names = dict(Order.STATUS_CHOICES)
    
    for item in orders_by_status:
        status = item['status']
        count = item['count']
        status_data['labels'].append(status_display_names.get(status, status))
        status_data['data'].append(count)
        status_data['colors'].append(status_colors.get(status, '#6c757d'))
    
    top_selling_products = Product.objects.filter(
        is_active=True,
        orderitem__order__status='delivered'
    ).annotate(total_sold=Sum('orderitem__quantity')).order_by('-total_sold')[:5]
    
    top_products_labels = [p.name for p in top_selling_products]
    top_products_data = [int(p.total_sold or 0) for p in top_selling_products]
    
    delivered_orders_this_month = Order.objects.filter(
        status='delivered',
        created_at__gte=start_of_month
    ).count()
    
    conversion_rate = round((delivered_orders_this_month / total_orders_count * 100), 1) if total_orders_count > 0 else 0
    new_customers_this_month = User.objects.filter(date_joined__gte=start_of_month).count()
    recent_reviews = Review.objects.select_related('product', 'user').order_by('-created_at')[:5]
    
    context = {
        'total_products': Product.objects.count(),
        'total_categories': Category.objects.count(),
        'total_users': User.objects.count(),
        'total_orders': total_orders_count,
        'pending_orders': Order.objects.filter(status='pending').count(),
        'total_revenue_fcfa': total_revenue_fcfa,
        'revenue_this_month_fcfa': revenue_this_month_fcfa,
        'recent_orders': recent_orders,
        'top_products': top_products,
        'recent_reviews': recent_reviews,
        'monthly_labels': monthly_labels,
        'monthly_revenue': monthly_revenue,
        'status_labels': status_data['labels'],
        'status_data': status_data['data'],
        'status_colors': status_data['colors'],
        'top_products_labels': top_products_labels,
        'top_products_data': top_products_data,
        'avg_order_value': avg_order_value,
        'delivered_orders_this_month': delivered_orders_this_month,
        'conversion_rate': conversion_rate,
        'new_customers_this_month': new_customers_this_month,
        'positive_reviews_percentage': 87,
    }
    
    return render(request, 'dashboard.html', context)


def api_cart_update(request):
    """API pour mettre à jour le panier"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            product_id = str(data.get('product_id'))
            action = data.get('action')
            quantity = data.get('quantity', 1)
            
            cart = request.session.get('cart', {})
            
            if action == 'add':
                cart[product_id] = cart.get(product_id, 0) + quantity
            elif action == 'remove':
                if product_id in cart:
                    del cart[product_id]
            elif action == 'update':
                cart[product_id] = max(1, quantity)
            
            request.session['cart'] = cart
            request.session.modified = True
            
            total_fcfa = Decimal('0')
            for pid, qty in cart.items():
                try:
                    product = Product.objects.get(id=pid)
                    total_fcfa += product.price_fcfa * Decimal(qty)
                except Product.DoesNotExist:
                    pass
            
            tax_fcfa = (total_fcfa * Decimal('0.20')).quantize(Decimal('0.01'))
            total_with_tax_fcfa = total_fcfa + tax_fcfa
            
            return JsonResponse({
                'success': True,
                'cart_count': sum(cart.values()),
                'total_fcfa': str(total_fcfa),
                'total_formatted': f"{total_fcfa:,.0f} FCFA".replace(',', ' '),
                'tax_fcfa': str(tax_fcfa),
                'total_with_tax_fcfa': str(total_with_tax_fcfa),
                'total_with_tax_formatted': f"{total_with_tax_fcfa:,.0f} FCFA".replace(',', ' ')
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    
    return JsonResponse({'success': False, 'error': 'Méthode non autorisée'}, status=405)


def debug_session(request):
    """Vue de débogage"""
    session_info = {
        'session_id': request.session.session_key,
        'preferred_currency': request.session.get('preferred_currency'),
        'all_session_keys': list(request.session.keys()),
        'user_authenticated': request.user.is_authenticated,
        'user_id': request.user.id if request.user.is_authenticated else None,
        'user_currency_from_func': get_user_currency(request),
    }
    return JsonResponse(session_info)


# ... (tout le code précédent : api_cart_count, debug_session, etc.) ...

def api_cart_count(request):
    """API pour le compteur du panier"""
    try:
        cart = request.session.get('cart', {})
        cart_count = sum(cart.values()) if cart else 0
        return JsonResponse({'success': True, 'count': cart_count})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# ==============================================================================
# AUTHENTIFICATION & CLASSES (CORRIGÉ)
# ==============================================================================

class CustomLoginView(LoginView):
    """Vue de connexion personnalisée avec redirection selon le rôle"""
    def get_success_url(self):
        if self.request.user.is_staff:
            return reverse_lazy('core:dashboard')
        return super().get_success_url()

def logout_view(request):
    """Déconnecte l'utilisateur et affiche la page de confirmation ou redirige."""
    if request.method == "POST":
        logout(request)
        messages.success(request, "Vous avez été déconnecté(e). À bientôt !")
        return redirect('core:home')
    
    # CORRECTION ICI : On cherche 'logout.html' directement, pas 'core/logout.html'
    return render(request, 'logout.html')