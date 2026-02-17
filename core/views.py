from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from allauth.socialaccount.models import SocialApp
from django.db.models import Sum, Q, Count
from django.utils import timezone
from decimal import Decimal
import json
from .models import Category, Product, Order, Review, Currency, UserCurrencyPreference, User, OrderItem
from core.currency_service import CurrencyConverter, get_user_currency  # IMPORT CORRECT
from .forms import ReviewForm


def home(request):
    """Home page with featured products"""
    featured_products = Product.objects.filter(is_featured=True)[:4]
    categories = Category.objects.filter(is_active=True)
    context = {
        'featured_products': featured_products,
        'categories': categories
    }
    return render(request, 'home.html', context)

def products_view(request):
    """Products listing page with filters"""
    products = Product.objects.filter(is_active=True)
    categories = Category.objects.filter(is_active=True)
    
    # Filter by category
    category_param = request.GET.get('category')
    selected_category = None
    if category_param:
        try:
            # Try to get by ID first
            selected_category = Category.objects.get(id=int(category_param))
            products = products.filter(category=selected_category)
        except (ValueError, Category.DoesNotExist):
            # If not ID, try by name
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
    
    # Sorting - utiliser price_fcfa au lieu de price
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

def product_type_view(request, product_type):
    """View products by type (cafe, pain, machine, accessoire)"""
    product_type_display = dict(Product.PRODUCT_TYPES).get(product_type, '')
    
    products = Product.objects.filter(
        product_type=product_type,
        is_active=True
    )
    
    # Get all categories for this product type
    sub_categories = Category.objects.filter(
        products__product_type=product_type,
        is_active=True
    ).distinct()
    
    # Search within type
    query = request.GET.get('q')
    if query:
        products = products.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query)
        )
    
    # Filter by price range (FCFA)
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        products = products.filter(price_fcfa__gte=min_price)
    if max_price:
        products = products.filter(price_fcfa__lte=max_price)
    
    # Sorting - utiliser price_fcfa au lieu de price
    sort_by = request.GET.get('sort', '-created_at')
    if sort_by == 'price':
        sort_by = 'price_fcfa'
    elif sort_by == '-price':
        sort_by = '-price_fcfa'
    products = products.order_by(sort_by)
    
    context = {
        'products': products,
        'product_type': product_type,
        'product_type_display': product_type_display,
        'sub_categories': sub_categories,
        'query': query
    }
    return render(request, 'product_type.html', context)

def product_detail_view(request, product_id):
    """Product detail page with gestion des devises"""
    product = get_object_or_404(Product, id=product_id, is_active=True)
    reviews = product.reviews.all()
    related_products = Product.objects.filter(
        category=product.category, 
        is_active=True
    ).exclude(id=product_id)[:4]
    
    # Vérifier si l'utilisateur a déjà donné un avis
    has_reviewed = False
    if request.user.is_authenticated:
        has_reviewed = Review.objects.filter(product=product, user=request.user).exists()
    
    # ✅ CORRECTION : Utilisation de la méthode de conversion
    try:
        price_eur = product.get_price_in_currency('EUR')
    except Exception as e:
        print(f"Erreur de conversion EUR: {e}")
        price_eur = product.price_fcfa / Decimal('655.957')
    
    context = {
        'product': product,  # ✅ DOIT ÊTRE ICI
        'reviews': reviews,
        'related_products': related_products,
        'average_rating': product.rating if product.rating else 0,
        'has_reviewed': has_reviewed,
        'review_form': ReviewForm() if request.user.is_authenticated and not has_reviewed else None,
        'price_eur': price_eur,
    
    }
    return render(request, 'product_detail.html', context)

def cart_view(request):
    """Shopping cart page - Mise à jour pour FCFA"""
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
                'total': item_total_fcfa  # Compatibilité
            })
        except Product.DoesNotExist:
            pass
    
    # Calculer la TVA (20%) et le total
    tax_fcfa = (total_price_fcfa * Decimal('0.20')).quantize(Decimal('0.01'))
    total_amount_fcfa = total_price_fcfa + tax_fcfa
    
    context = {
        'cart_items': items,
        'total_price_fcfa': total_price_fcfa,
        'total_price': total_price_fcfa,  # Compatibilité
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
            
            # Get or create cart in session
            cart = request.session.get('cart', {})
            product_id_str = str(product_id)
            
            # Add or update quantity
            if product_id_str in cart:
                cart[product_id_str] += quantity
            else:
                cart[product_id_str] = quantity
            
            request.session['cart'] = cart
            request.session.modified = True
            
            # Calculer le sous-total pour la réponse
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
            return JsonResponse({
                'success': False,
                'message': 'Produit non trouvé'
            }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False, 
            'message': f'Erreur: {str(e)}'
        }, status=400)

def checkout_view(request):
    """Checkout page - Mise à jour pour FCFA"""
    cart_items = request.session.get('cart', {})
    
    # Redirect to cart if empty
    if not cart_items:
        return redirect('cart')
    
    # Calculate cart totals in FCFA
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
    
    # Determine shipping cost in FCFA
    shipping_method = request.POST.get('shipping', 'standard')
    shipping_costs_fcfa = {
        'standard': Decimal('0'),
        'express': Decimal('6559.60'),  # 9.99€ → ~6559.60 FCFA
        'overnight': Decimal('13119.20')  # 19.99€ → ~13119.20 FCFA
    }
    shipping_cost_fcfa = shipping_costs_fcfa.get(shipping_method, Decimal('0'))
    
    # Calculate tax (20%)
    tax_fcfa = (total_price_fcfa * Decimal('0.20')).quantize(Decimal('0.01'))
    final_total_fcfa = (total_price_fcfa + shipping_cost_fcfa + tax_fcfa).quantize(Decimal('0.01'))
    
    # Get user addresses if authenticated
    user_addresses = []
    if request.user.is_authenticated:
        # Supposant que vous avez un modèle UserAddress lié à l'utilisateur
        # user_addresses = request.user.addresses.all()
        pass
    
    context = {
        'cart_items': items,
        'total_price_fcfa': total_price_fcfa,
        'shipping_cost_fcfa': shipping_cost_fcfa,
        'tax_fcfa': tax_fcfa,
        'final_total_fcfa': final_total_fcfa,
        'total_amount_fcfa': final_total_fcfa,
        'user_addresses': user_addresses,
    }
    return render(request, 'checkout.html', context)

@csrf_exempt
@require_POST
def process_payment(request):
    """AJAX endpoint to process payment - Mise à jour pour FCFA"""
    try:
        data = json.loads(request.body)
        cart_items = request.session.get('cart', {})
        
        if not cart_items:
            return JsonResponse({'success': False, 'message': 'Panier vide'}, status=400)
        
        # Calculate totals in FCFA
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
        
        # Get address info
        first_name = data.get('first_name', 'Guest')
        last_name = data.get('last_name', '')
        email = data.get('email', '')
        phone = data.get('phone', '')
        address = data.get('address', '')
        city = data.get('city', '')
        postal_code = data.get('postal_code', '')
        
        # Create order with FCFA fields
        if request.user.is_authenticated:
            # Récupérer la devise FCFA
            fcfa_currency = Currency.objects.get(code='XOF')
            
            order = Order.objects.create(
                user=request.user,
                total_amount=final_total_fcfa,  # Montant dans la devise d'origine
                total_amount_fcfa=final_total_fcfa,  # Montant en FCFA
                shipping_method=shipping_method,
                status='pending',
                currency_used=fcfa_currency,
                shipping_address=f"{address}, {city} {postal_code}",
                billing_address=f"{address}, {city} {postal_code}",
                payment_method='card',
                payment_status='pending'
            )
            
            # Add items to order
            for product_id, quantity in cart_items.items():
                try:
                    product = Product.objects.get(id=product_id)
                    # Créer OrderItem avec prix FCFA
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=quantity,
                        price=product.price,  # Prix original
                        price_fcfa=product.price_fcfa,  # Prix en FCFA
                        total=product.price * quantity,  # Total original
                        total_fcfa=product.price_fcfa * quantity  # Total en FCFA
                    )
                except Product.DoesNotExist:
                    pass
        
        # Clear cart
        request.session['cart'] = {}
        request.session.modified = True
        
        return JsonResponse({
            'success': True,
            'message': 'Commande créée avec succès',
            'order_id': order.id if request.user.is_authenticated else None,
            'total': str(final_total_fcfa),
            'total_formatted': f"{final_total_fcfa:,.0f} FCFA".replace(',', ' ')
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)

def payment_success_view(request):
    """Payment success page"""
    return render(request, 'payment_success.html')

## @login_required(login_url='login')
def account_view(request):
    """View for user account/profile page avec conversion de devise"""
    # Get user's preferred currency
    user_currency_code = get_user_currency(request)
    
    # Calculate total spent in FCFA
    total_spent_fcfa = Decimal('0')
    recent_orders_data = []
    total_orders_count = 0
    
    if hasattr(request.user, 'orders'):
        total_spent_fcfa = request.user.orders.aggregate(
            total=Sum('total_amount_fcfa')
        )['total'] or Decimal('0')
        
        # Get recent orders (last 5)
        recent_orders = request.user.orders.select_related('currency_used').order_by('-created_at')[:5]
        total_orders_count = request.user.orders.count()
        
        # Convert order amounts to user's currency
        for order in recent_orders:
            # Get order items for display
            order_items = order.items.all()
            
            # Convert order amount
            converted_data = CurrencyConverter.convert_price(
                float(order.total_amount_fcfa),
                'XOF',  # Base currency is FCFA
                user_currency_code
            )
            
            recent_orders_data.append({
                'order': order,
                'items': order_items,
                'converted_amount': converted_data['amount'],
                'formatted_amount': converted_data['formatted'],
                'currency_symbol': converted_data['symbol'],
                'status_display': order.get_status_display()
            })
    
    # Convert total spent to user's currency
    total_spent_converted = CurrencyConverter.convert_price(
        float(total_spent_fcfa),
        'XOF',
        user_currency_code
    )
    
    # Get wishlist count (assuming you have a wishlist model)
    wishlist_count = 0
    if hasattr(request.user, 'wishlist_items'):
        wishlist_count = request.user.wishlist_items.count()
    
    # Calculate loyalty points (example: 1 point per 1000 FCFA spent)
    loyalty_points = int(total_spent_fcfa / Decimal('1000'))
    
    # Get all supported currencies for display
    currencies = CurrencyConverter.SUPPORTED_CURRENCIES
    
    context = {
        # Total spent
        'total_spent_fcfa': total_spent_fcfa,
        'total_spent_converted': total_spent_converted['amount'],
        'total_spent_formatted': total_spent_converted['formatted'],
        'currency_symbol': total_spent_converted['symbol'],
        'currency_code': user_currency_code,
        
        # Orders
        'orders_count': total_orders_count,
        'recent_orders': recent_orders_data,
        
        # Other stats
        'wishlist_count': wishlist_count,
        'loyalty_points': loyalty_points,
        
        # Currency data
        'currencies': currencies,
        'user_currency': user_currency_code,
        'CURRENCY_SYMBOL': currencies.get(user_currency_code, {}).get('symbol', 'FCFA'),
    }
    return render(request, 'profile.html', context)

def login_view(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('core:dashboard')  # ✅ Redirection admin
        return redirect('core:account')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        next_url = request.POST.get('next', 'account')
        
        try:
            # Try to authenticate with email (if using email as username)
            user = authenticate(request, username=email, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f'Bienvenue {user.first_name or user.username}! 👋')
                return redirect(next_url)
            else:
                messages.error(request, 'Email ou mot de passe invalide.')
        except Exception as e:
            messages.error(request, 'Une erreur est survenue lors de la connexion.')
    
    # Check if Google OAuth is configured
    try:
        google_app = SocialApp.objects.get(provider='google')
    except SocialApp.DoesNotExist:
        google_app = None
    
    context = {
        'google_app': google_app
    }
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
        newsletter = request.POST.get('newsletter')
        
        # Validate inputs
        if not email or not password:
            messages.error(request, 'Email et mot de passe sont requis.')
            return render(request, 'signup.html')
        
        if password != password_confirm:
            messages.error(request, 'Les mots de passe ne correspondent pas.')
            return render(request, 'signup.html')
        
        # Check if user already exists
        if User.objects.filter(username=email).exists():
            messages.error(request, 'Un compte avec cet email existe déjà.')
            return render(request, 'signup.html')
        
        # Create user
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
    
    # Check if Google OAuth is configured
    try:
        google_app = SocialApp.objects.get(provider='google')
    except SocialApp.DoesNotExist:
        google_app = None
    
    context = {
        'google_app': google_app
    }
    return render(request, 'signup.html', context)

def update_currency_preference(request):
    """Update user's currency preference"""
    if request.method == 'POST':
        currency_code = request.POST.get('currency')
        
        # Codes de devise supportés
        SUPPORTED_CURRENCIES = ['XOF', 'USD', 'EUR']
        
        if currency_code not in SUPPORTED_CURRENCIES:
            messages.error(request, "Devise invalide")
            return redirect(request.META.get('HTTP_REFERER', 'account'))

        # Pour les utilisateurs anonymes : stocker en session
        if not request.user.is_authenticated:
            request.session['preferred_currency'] = currency_code
            request.session.modified = True
            messages.success(request, f"Devise mise à jour: {currency_code}")
            return redirect(request.META.get('HTTP_REFERER', 'home'))

        # Pour les utilisateurs connectés
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
    
    # Rediriger vers la page précédente ou account
    return redirect(request.META.get('HTTP_REFERER', 'account'))

def api_exchange_rates(request):
    """API pour récupérer les taux de change en temps réel"""
    base_currency = request.GET.get('base', 'XOF')
    
    try:
        rates_data = CurrencyConverter.get_exchange_rates(base_currency)
        return JsonResponse({
            'success': True,
            'data': rates_data
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

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
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)

# Context processor pour rendre la devise disponible dans tous les templates
def currency_context(request):
    """Make currency information available in all templates"""
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
    """
    Ajouter un avis sur un produit - VERSION AVEC AVIS MULTIPLES AUTORISÉS
    Les utilisateurs peuvent maintenant poster autant d'avis qu'ils le souhaitent
    """
    product = get_object_or_404(Product, id=product_id, is_active=True)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            # Créer l'avis SANS vérification d'existence préalable
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.is_verified = True  # À adapter selon votre logique de vérification
            review.save()
            
            # Mettre à jour la note moyenne du produit
            reviews = product.reviews.all()
            if reviews.exists():
                # Calcul de la moyenne avec Sum (plus précis que Avg pour les Decimal)
                total_rating = reviews.aggregate(total=Sum('rating'))['total'] or Decimal('0')
                average_rating = total_rating / reviews.count()
                product.rating = float(average_rating)  # Convertir en float pour le champ FloatField
                product.reviews_count = reviews.count()
                product.save()
            
            messages.success(request, "✅ Merci pour votre avis ! Il a été publié avec succès.")
            return redirect('core:product_detail', product_id=product.id)
        else:
            # Gestion des erreurs de formulaire
            messages.error(request, "❌ Veuillez corriger les erreurs dans le formulaire.")
            # Renvoyer vers la page produit avec les erreurs
            return redirect('core:product_detail', product_id=product.id)
    
    # Pour les requêtes GET, rediriger vers la page produit
    return redirect('core:product_detail', product_id=product.id)

@login_required
def dashboard_analytics_view(request):
    """Analytics dashboard avec insights détaillés - LIÉ AU DASHBOARD PRINCIPAL"""
    if not request.user.is_staff:
        return redirect('core:home')
    
    # Total clients (tous les utilisateurs)
    total_customers = User.objects.count()
    
    # Nouveaux clients (30 derniers jours)
    thirty_days_ago = timezone.now() - timezone.timedelta(days=30)
    new_customers = User.objects.filter(date_joined__gte=thirty_days_ago).count()
    
    # Panier moyen (en FCFA)
    delivered_orders = Order.objects.filter(status='delivered')
    total_revenue = delivered_orders.aggregate(total=Sum('total_amount_fcfa'))['total'] or Decimal('0.00')
    total_orders_count = delivered_orders.count()
    avg_order_value = total_revenue / total_orders_count if total_orders_count > 0 else Decimal('0.00')
    
    # Produits mieux notés (top 5)
    best_rated = Product.objects.filter(
        is_active=True, 
        reviews_count__gt=0
    ).order_by('-rating', '-reviews_count')[:5]
    
    # Produits avec le plus d'avis (top 5)
    most_reviewed = Product.objects.filter(
        is_active=True
    ).order_by('-reviews_count')[:5]
    
    # KPIs supplémentaires pour cohérence avec le dashboard principal
    total_revenue_fcfa = Order.objects.filter(status='delivered').aggregate(
        total=Sum('total_amount_fcfa')
    )['total'] or Decimal('0.00')
    
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
        
        # KPIs pour cohérence avec le dashboard principal
        'total_revenue_fcfa': total_revenue_fcfa,
        'revenue_this_month_fcfa': revenue_this_month_fcfa,
        'total_products': Product.objects.count(),
        'total_orders': Order.objects.count(),
    }
    
    return render(request, 'dashboard_analytics.html', context)

login_required
def dashboard_view(request):
    """Dashboard admin avec statistiques en FCFA et graphiques Chart.js"""
    if not request.user.is_staff:
        return redirect('core:home')
    
    # Calculer les revenus en FCFA
    total_revenue_fcfa = Order.objects.filter(status='delivered').aggregate(
        total=Sum('total_amount_fcfa')
    )['total'] or Decimal('0.00')
    
    # Revenu du mois en FCFA
    today = timezone.now()
    start_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    revenue_this_month_fcfa = Order.objects.filter(
        status='delivered',
        created_at__gte=start_of_month
    ).aggregate(total=Sum('total_amount_fcfa'))['total'] or Decimal('0.00')
    
    # Commandes récentes avec montants FCFA
    recent_orders = Order.objects.select_related('user').order_by('-created_at')[:10]
    
    # Produits populaires (par nombre d'avis)
    top_products = Product.objects.filter(is_active=True).annotate(
    delivered_count=Count('orderitem', filter=Q(orderitem__order__status='delivered'))
    ).order_by('-reviews_count')[:5]
    
    
    # Commandes par statut
    orders_by_status = Order.objects.values('status').annotate(
        count=Count('id')
    ).order_by('status')
    
    total_orders_count = Order.objects.count()
    
    # ✅ CORRECTION 1 : Calcul sécurisé du panier moyen (évite division par zéro)
    avg_order_value = total_revenue_fcfa / Decimal(total_orders_count) if total_orders_count > 0 else Decimal('0.00')
    
    # ✅ CORRECTION 2 : Revenus mensuels (6 derniers mois) - SÉCURISÉ
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
    
    # ✅ CORRECTION 3 : Répartition des commandes par statut - SÉCURISÉ
    status_data = {'labels': [], 'data': [], 'colors': []}
    status_colors = {
        'delivered': '#28a745',
        'shipped': '#17a2b8',
        'confirmed': '#ffc107',
        'pending': '#6c757d',
        'cancelled': '#dc3545'
    }
    status_display_names = dict(Order.STATUS_CHOICES)  # Conversion sécurisée
    
    for item in orders_by_status:
        status = item['status']
        count = item['count']
        status_data['labels'].append(status_display_names.get(status, status))
        status_data['data'].append(count)
        status_data['colors'].append(status_colors.get(status, '#6c757d'))
    
    # ✅ CORRECTION 4 : Top 5 produits les plus vendus - SÉCURISÉ
    top_selling_products = Product.objects.filter(
        is_active=True,
        orderitem__order__status='delivered'
    ).annotate(
        total_sold=Sum('orderitem__quantity')
    ).order_by('-total_sold')[:5]
    
    top_products_labels = [p.name for p in top_selling_products]
    top_products_data = [int(p.total_sold or 0) for p in top_selling_products]
    
    # ✅ CORRECTION 5 : KPIs supplémentaires - SÉCURISÉS
    delivered_orders_this_month = Order.objects.filter(
        status='delivered',
        created_at__gte=start_of_month
    ).count()
    
    # Taux de conversion : commandes livrées ce mois / total commandes (éviter division par zéro)
    conversion_rate = round((delivered_orders_this_month / total_orders_count * 100), 1) if total_orders_count > 0 else 0
    
    # Nouveaux clients ce mois
    new_customers_this_month = User.objects.filter(
        date_joined__gte=start_of_month
    ).count()
    
    # ✅ CORRECTION 6 : Avis récents (défini mais non utilisé dans le template - gardé pour compatibilité)
    recent_reviews = Review.objects.select_related('product', 'user').order_by('-created_at')[:5]
    
    # ✅ CONTEXTE COMPLET ET SÉCURISÉ
    context = {
        # Statistiques de base
        'total_products': Product.objects.count(),
        'total_categories': Category.objects.count(),
        'total_users': User.objects.count(),
        'total_orders': total_orders_count,
        'pending_orders': Order.objects.filter(status='pending').count(),
        'total_revenue_fcfa': total_revenue_fcfa,
        'revenue_this_month_fcfa': revenue_this_month_fcfa,
        'recent_orders': recent_orders,
        'top_products': top_products,
        'recent_reviews': recent_reviews,  # Maintenu pour compatibilité
        
        # Données pour les graphiques Chart.js
        'monthly_labels': monthly_labels,
        'monthly_revenue': monthly_revenue,
        'status_labels': status_data['labels'],
        'status_data': status_data['data'],
        'status_colors': status_data['colors'],
        'top_products_labels': top_products_labels,
        'top_products_data': top_products_data,
        
        # KPIs avancés
        'avg_order_value': avg_order_value,
        'delivered_orders_this_month': delivered_orders_this_month,
        'conversion_rate': conversion_rate,
        'new_customers_this_month': new_customers_this_month,
        'positive_reviews_percentage': 87,  # À calculer dynamiquement si nécessaire
    }
    
    return render(request, 'dashboard.html', context)

def api_cart_update(request):
    """API pour mettre à jour le panier"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            product_id = str(data.get('product_id'))
            action = data.get('action')  # 'add', 'remove', 'update'
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
            
            # Recalculer les totaux en FCFA
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
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
    
    return JsonResponse({'success': False, 'error': 'Méthode non autorisée'}, status=405)

def debug_session(request):
    """Vue de débogage pour vérifier les sessions"""
    from django.http import JsonResponse
    
    session_info = {
        'session_id': request.session.session_key,
        'preferred_currency': request.session.get('preferred_currency'),
        'all_session_keys': list(request.session.keys()),
        'user_authenticated': request.user.is_authenticated,
        'user_id': request.user.id if request.user.is_authenticated else None,
        'user_currency_from_func': get_user_currency(request),
    }
    
    return JsonResponse(session_info)



def api_cart_count(request):
    """
    API endpoint pour récupérer le nombre d'articles dans le panier
    """
    try:
        cart = request.session.get('cart', {})
        cart_count = sum(cart.values()) if cart else 0
        
        return JsonResponse({
            'success': True,
            'count': cart_count
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
        
from django.contrib.auth.views import LoginView

class CustomLoginView(LoginView):
    def get_success_url(self):
        if self.request.user.is_staff:
            return reverse_lazy('core:dashboard')
        return super().get_success_url()