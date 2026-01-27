from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from allauth.socialaccount.models import SocialApp
from django.db.models import Sum, Q
from .models import Category, Product, Order, Review
from decimal import Decimal
import json

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
    
    # Filter by price range
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)
    
    # Search
    query = request.GET.get('q')
    if query:
        products = products.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query)
        )
    
    # Sorting
    sort_by = request.GET.get('sort', '-created_at')
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
    
    # Filter by price range
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)
    
    # Sorting
    sort_by = request.GET.get('sort', '-created_at')
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
    """Product detail page"""
    product = get_object_or_404(Product, id=product_id, is_active=True)
    reviews = product.reviews.all()
    related_products = Product.objects.filter(
        category=product.category, 
        is_active=True
    ).exclude(id=product_id)[:4]
    
    context = {
        'product': product,
        'reviews': reviews,
        'related_products': related_products,
        'average_rating': product.rating if product.rating else 0
    }
    return render(request, 'product_detail.html', context)

def cart_view(request):
    """Shopping cart page"""
    cart_items = request.session.get('cart', {})
    total_price = Decimal('0')
    items = []
    
    for product_id, quantity in cart_items.items():
        try:
            product = Product.objects.get(id=product_id)
            total_price += product.price * quantity
            items.append({
                'product': product,
                'quantity': quantity,
                'total': product.price * quantity
            })
        except Product.DoesNotExist:
            pass
    
    context = {
        'cart_items': items,
        'total_price': total_price,
        'cart_count': len(cart_items)
    }
    return render(request, 'cart.html', context)

def add_to_cart_ajax(request):
    """AJAX endpoint to add product to cart"""
    if request.method == 'POST':
        import json
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
            
            return JsonResponse({
                'success': True,
                'message': f'{product.name} ajouté au panier!',
                'cart_count': sum(cart.values()),
                'product_name': product.name
            })
        except Product.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Produit non trouvé'
            }, status=404)
    
    return JsonResponse({'success': False, 'message': 'Requête invalide'}, status=400)

def checkout_view(request):
    """Checkout page - Redirect to payment"""
    cart_items = request.session.get('cart', {})
    
    # Redirect to cart if empty
    if not cart_items:
        return redirect('cart')
    
    # Calculate cart totals
    total_price = 0
    items = []
    
    for product_id, quantity in cart_items.items():
        try:
            product = Product.objects.get(id=product_id)
            item_total = product.price * quantity
            total_price += item_total
            items.append({
                'product': product,
                'quantity': quantity,
                'total': item_total
            })
        except Product.DoesNotExist:
            pass
    
    # Determine shipping cost
    shipping_method = request.POST.get('shipping', 'standard')
    shipping_costs = {
        'standard': Decimal('0'),
        'express': Decimal('9.99'),
        'overnight': Decimal('19.99')
    }
    shipping_cost = shipping_costs.get(shipping_method, Decimal('0'))
    
    # Calculate tax (20%)
    tax = (total_price * Decimal('0.20')).quantize(Decimal('0.01'))
    final_total = (total_price + shipping_cost + tax).quantize(Decimal('0.01'))
    
    context = {
        'cart_items': items,
        'cart_total': total_price,
        'shipping_cost': shipping_cost,
        'tax': tax,
        'final_total': final_total,
        'total': final_total,
    }
    return render(request, 'payment.html', context)

def process_payment(request):
    """AJAX endpoint to process payment"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            cart_items = request.session.get('cart', {})
            
            if not cart_items:
                return JsonResponse({'success': False, 'message': 'Panier vide'}, status=400)
            
            # Calculate totals
            total_price = Decimal('0')
            for product_id, quantity in cart_items.items():
                try:
                    product = Product.objects.get(id=product_id)
                    total_price += product.price * quantity
                except Product.DoesNotExist:
                    pass
            
            shipping_method = data.get('shipping_method', 'standard')
            shipping_costs = {
                'standard': Decimal('0'),
                'express': Decimal('9.99'),
                'overnight': Decimal('19.99')
            }
            shipping_cost = shipping_costs.get(shipping_method, Decimal('0'))
            
            tax = (total_price * Decimal('0.20')).quantize(Decimal('0.01'))
            final_total = (total_price + shipping_cost + tax).quantize(Decimal('0.01'))
            
            # Get address info
            first_name = data.get('first_name', 'Guest')
            last_name = data.get('last_name', '')
            email = data.get('email', '')
            phone = data.get('phone', '')
            address = data.get('address', '')
            city = data.get('city', '')
            postal_code = data.get('postal_code', '')
            
            # Create order
            if request.user.is_authenticated:
                order = Order.objects.create(
                    user=request.user,
                    total_amount=final_total,
                    shipping_method=shipping_method,
                    status='pending'
                )
                
                # Add items to order
                for product_id, quantity in cart_items.items():
                    try:
                        product = Product.objects.get(id=product_id)
                        # Assuming OrderItem model exists
                        # OrderItem.objects.create(order=order, product=product, quantity=quantity)
                    except Product.DoesNotExist:
                        pass
            
            # Clear cart
            request.session['cart'] = {}
            request.session.modified = True
            
            return JsonResponse({
                'success': True,
                'message': 'Commande créée avec succès',
                'order_id': order.id if request.user.is_authenticated else None,
                'total': final_total
            })
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=400)
    
    return JsonResponse({'success': False, 'message': 'Requête invalide'}, status=400)

def payment_success_view(request):
    """Payment success page"""
    return render(request, 'payment_success.html')

@login_required(login_url='login')
def account_view(request):
    """View for user account/profile page"""
    # Calculate total spent
    total_spent = 0
    if hasattr(request.user, 'orders'):
        total_spent = request.user.orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    
    context = {
        'total_spent': total_spent,
        'orders_count': request.user.orders.count() if hasattr(request.user, 'orders') else 0,
    }
    return render(request, 'profile.html', context)

def login_view(request):
    """View for user login with redirect to profile"""
    if request.user.is_authenticated:
        return redirect('account')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        next_url = request.POST.get('next', 'account')
        
        try:
            # Try to authenticate with email (if using email as username)
            user = authenticate(request, username=email, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome {user.first_name or user.username}! 👋')
                return redirect(next_url)
            else:
                messages.error(request, 'Invalid email or password.')
        except Exception as e:
            messages.error(request, 'An error occurred during login.')
    
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
            messages.error(request, 'Email and password are required.')
            return render(request, 'signup.html')
        
        if password != password_confirm:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'signup.html')
        
        # Check if user already exists
        from django.contrib.auth.models import User
        if User.objects.filter(username=email).exists():
            messages.error(request, 'An account with this email already exists.')
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
            messages.success(request, 'Account created successfully! Please log in.')
            return redirect('login')
        except Exception as e:
            messages.error(request, f'Error creating account: {str(e)}')
    
    # Check if Google OAuth is configured
    try:
        google_app = SocialApp.objects.get(provider='google')
    except SocialApp.DoesNotExist:
        google_app = None
    
    context = {
        'google_app': google_app
    }
    return render(request, 'signup.html', context)

