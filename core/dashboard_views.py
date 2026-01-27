from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.db.models import Count, Sum, Q, Avg
from django.utils import timezone
from datetime import timedelta
from .models import Product, Category, Order, OrderItem, Review

def is_admin(user):
    """Check if user is admin"""
    return user.is_staff or user.is_superuser

@login_required(login_url='login')
@user_passes_test(is_admin, login_url='home')
def dashboard(request):
    """Admin Dashboard View"""
    
    # Statistics
    total_products = Product.objects.count()
    total_categories = Category.objects.count()
    total_users = User.objects.count()
    total_orders = Order.objects.count()
    
    # Revenue stats
    total_revenue = Order.objects.filter(status='delivered').aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    pending_orders = Order.objects.filter(status__in=['pending', 'confirmed']).count()
    
    # Recent orders
    recent_orders = Order.objects.select_related('user').order_by('-created_at')[:5]
    
    # Top products
    top_products = Product.objects.annotate(
        order_count=Count('orderitem')
    ).order_by('-order_count')[:5]
    
    # Recent reviews
    recent_reviews = Review.objects.select_related('product', 'user').order_by('-created_at')[:5]
    
    # Orders by status
    orders_by_status = Order.objects.values('status').annotate(count=Count('id')).order_by('status')
    
    # Revenue this month
    today = timezone.now()
    month_start = today.replace(day=1)
    revenue_this_month = Order.objects.filter(
        created_at__gte=month_start,
        status='delivered'
    ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    
    context = {
        'total_products': total_products,
        'total_categories': total_categories,
        'total_users': total_users,
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'pending_orders': pending_orders,
        'revenue_this_month': revenue_this_month,
        'recent_orders': recent_orders,
        'top_products': top_products,
        'recent_reviews': recent_reviews,
        'orders_by_status': orders_by_status,
    }
    
    return render(request, 'dashboard.html', context)


@login_required(login_url='login')
@user_passes_test(is_admin, login_url='home')
def dashboard_analytics(request):
    """Analytics page"""
    
    # Sales data
    orders_last_7_days = Order.objects.filter(
        created_at__gte=timezone.now() - timedelta(days=7),
        status='delivered'
    ).annotate(day=Count('id')).order_by('created_at__date')
    
    # Customer stats
    total_customers = User.objects.count()
    new_customers = User.objects.filter(
        date_joined__gte=timezone.now() - timedelta(days=30)
    ).count()
    
    # Product performance
    best_rated = Product.objects.filter(rating__gt=0).order_by('-rating')[:5]
    most_reviewed = Product.objects.annotate(review_count=Count('reviews')).order_by('-review_count')[:5]
    
    # Average order value
    avg_order_value = Order.objects.filter(status='delivered').aggregate(Avg('total_amount'))['total_amount__avg'] or 0
    
    context = {
        'total_customers': total_customers,
        'new_customers': new_customers,
        'best_rated': best_rated,
        'most_reviewed': most_reviewed,
        'avg_order_value': avg_order_value,
    }
    
    return render(request, 'dashboard_analytics.html', context)
