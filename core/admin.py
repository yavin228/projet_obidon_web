from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Product, ProductImage, Order, OrderItem, Review


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'product_count', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Informations générales', {'fields': ('name', 'slug', 'description')}),
        ('Médias', {'fields': ('image',)}),
        ('Statut', {'fields': ('is_active',)}),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def product_count(self, obj):
        count = obj.products.count()
        return format_html(
            '<span style="background-color: #417690; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            count
        )
    product_count.short_description = 'Produits'


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ['image', 'alt_text']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'category',
        'product_type_display',
        'price_display',
        'has_back_image_display',  # ← NOUVEAU : colonne pour l'image verso
        'stock_display',
        'display_stock_badge',
        'rating_display',
        'is_featured',
        'is_active'
    ]
    list_filter = [
        'category',
        'product_type',
        'display_stock',
        'is_featured',
        'is_active',
        'created_at'
    ]
    search_fields = ['name', 'description', 'category__name']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at', 'rating', 'reviews_count', 
                      'image_preview', 'back_image_preview']  # ← AJOUT des aperçus
    inlines = [ProductImageInline]

    fieldsets = (
        ('Informations générales', {
            'fields': ('name', 'slug', 'category', 'product_type', 'description', 'detailed_description')
        }),
        ('Pricing', {
            'fields': ('price', 'discount_price')
        }),
        ('Médias', {
            'fields': ('image', 'image_preview', 'back_image', 'back_image_preview'),
            'description': "Image: image principale (recto)<br>Image verso: image secondaire qui apparaît au survol"
        }),
        ('Stock et disponibilité', {
            'fields': ('stock', 'display_stock', 'is_active', 'is_featured')
        }),
        ('Avis', {
            'fields': ('rating', 'reviews_count'),
            'classes': ('collapse',)
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def product_type_display(self, obj):
        colors = {
            'cafe': '#8B4513',
            'pain': '#D2B48C',
            'machine': '#404040',
            'accessoire': '#D4AF37'
        }
        color = colors.get(obj.product_type, '#000')
        display = dict(obj.PRODUCT_TYPES).get(obj.product_type, obj.product_type)
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            color, display
        )
    product_type_display.short_description = 'Type'

    def price_display(self, obj):
        if obj.discount_price:
            return format_html(
                '<span style="text-decoration: line-through;">{}</span> → <span style="color: #D32F2F; font-weight: bold;">{}</span>',
                f"{obj.price:.2f}", f"{obj.discount_price:.2f}"
            )
        return f"{obj.price:.2f}"
    price_display.short_description = 'Prix'

    def has_back_image_display(self, obj):
        if obj.back_image:
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 4px 10px; border-radius: 12px; font-size: 12px;">✓</span>'
            )
        else:
            return format_html(
                '<span style="background-color: #6c757d; color: white; padding: 4px 10px; border-radius: 12px; font-size: 12px;">✗</span>'
            )
    has_back_image_display.short_description = 'Image verso ?'

    def stock_display(self, obj):
        if obj.display_stock:
            color = '#28a745' if obj.stock > 0 else '#dc3545'
            text = obj.stock
        else:
            color = '#6c757d'
            text = "Caché"
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            color, text
        )
    stock_display.short_description = 'Stock'

    def display_stock_badge(self, obj):
        if obj.display_stock:
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 4px 10px; border-radius: 12px; font-size: 12px;">Oui</span>'
            )
        else:
            return format_html(
                '<span style="background-color: #dc3545; color: white; padding: 4px 10px; border-radius: 12px; font-size: 12px;">Non</span>'
            )
    display_stock_badge.short_description = 'Afficher stock ?'

    def rating_display(self, obj):
        stars = '⭐' * int(obj.rating or 0)
        return format_html('{} ({}/5 - {} avis)', stars, obj.rating, obj.reviews_count)
    rating_display.short_description = 'Évaluation'

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 100px; max-width: 100px; border: 1px solid #ddd; padding: 2px; margin-top: 5px;" />',
                obj.image.url
            )
        return "Pas d'image principale"
    image_preview.short_description = 'Aperçu recto'

    def back_image_preview(self, obj):
        if obj.back_image:
            return format_html(
                '<img src="{}" style="max-height: 100px; max-width: 100px; border: 1px solid #ddd; padding: 2px; margin-top: 5px;" />',
                obj.back_image.url
            )
        return "Pas d'image verso"
    back_image_preview.short_description = 'Aperçu verso'


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['alt_text', 'image_preview', 'uploaded_at']
    search_fields = ['alt_text']
    readonly_fields = ['image_preview', 'uploaded_at']

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 50px; max-width: 50px;" />', obj.image.url)
        return "No image"
    image_preview.short_description = 'Aperçu'


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'quantity', 'price', 'total']
    can_delete = False
    fields = ['product', 'quantity', 'price', 'total']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'user_display', 'status_display', 'total_amount', 'payment_status_display', 'created_at']
    list_filter = ['status', 'payment_status', 'created_at', 'user']
    search_fields = ['order_number', 'user__email', 'user__first_name']
    readonly_fields = ['order_number', 'created_at', 'updated_at', 'shipped_at', 'delivered_at']
    inlines = [OrderItemInline]

    fieldsets = (
        ('Informations de la commande', {'fields': ('order_number', 'user', 'status', 'created_at', 'updated_at')}),
        ('Adresses', {'fields': ('shipping_address', 'billing_address')}),
        ('Montants', {'fields': ('total_amount', 'tax_amount', 'shipping_cost')}),
        ('Paiement', {'fields': ('payment_method', 'payment_status')}),
        ('Livraison', {'fields': ('shipped_at', 'delivered_at')}),
        ('Notes', {'fields': ('customer_notes', 'admin_notes')}),
    )

    def user_display(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}".strip() or obj.user.email
    user_display.short_description = 'Client'

    def status_display(self, obj):
        colors = {
            'pending': '#ffc107',
            'confirmed': '#17a2b8',
            'shipped': '#007bff',
            'delivered': '#28a745',
            'cancelled': '#dc3545',
            'refunded': '#6c757d',
        }
        color = colors.get(obj.status, '#000')
        display = dict(obj.STATUS_CHOICES).get(obj.status, obj.status)
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            color, display
        )
    status_display.short_description = 'Statut'

    def payment_status_display(self, obj):
        color = '#28a745' if obj.payment_status == 'completed' else '#ffc107'
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            color, obj.payment_status
        )
    payment_status_display.short_description = 'Paiement'


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'quantity', 'price', 'total']
    list_filter = ['order__created_at', 'order__status']
    search_fields = ['order__order_number', 'product__name']
    readonly_fields = ['order', 'product', 'quantity', 'price', 'total']

    def has_add_permission(self, request):
        return False


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating_stars', 'verified_badge', 'created_at')
    list_filter = ('rating', 'is_verified', 'created_at')
    search_fields = ('product__name', 'user__username', 'title', 'comment')
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('Informations', {'fields': ('product', 'user', 'is_verified')}),
        ('Contenu', {'fields': ('rating', 'title', 'comment')}),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def rating_stars(self, obj):
        stars = "⭐" * int(obj.rating or 0)
        return format_html(
            '<span style="font-size:18px;">{}</span> ({}/5)',
            stars, obj.rating
        )
    rating_stars.short_description = 'Évaluation'

    def verified_badge(self, obj):
        label = "✓ Vérifié" if obj.is_verified else "En attente"
        color = "#28a745" if obj.is_verified else "#6c757d"
        return format_html(
            '<span style="background-color:{}; color:white; padding:3px 8px; border-radius:3px;">{}</span>',
            color, label
        )
    verified_badge.short_description = 'Statut'