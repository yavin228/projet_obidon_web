from django.contrib import admin
from .models import (
    Category, Currency, ExchangeRate, Product, ProductImage, 
    Order, OrderItem, Review, UserCurrencyPreference
)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'symbol', 'flag', 'is_default', 'is_active']
    list_filter = ['is_default', 'is_active']
    search_fields = ['code', 'name']


@admin.register(ExchangeRate)
class ExchangeRateAdmin(admin.ModelAdmin):
    list_display = ['base_currency', 'target_currency', 'rate', 'is_active', 'last_updated']
    list_filter = ['is_active', 'base_currency', 'target_currency']
    search_fields = ['base_currency__code', 'target_currency__code']
    readonly_fields = ['last_updated']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'name', 
        'category', 
        'product_type', 
        'price_fcfa_display', 
        'discount_price_fcfa_display', 
        'stock', 
        'is_featured', 
        'is_active',
        'created_at'
    ]
    
    list_filter = ['category', 'is_featured', 'is_active', 'product_type']
    search_fields = ['name', 'description']
    readonly_fields = ['rating', 'reviews_count', 'created_at', 'updated_at']  # ✅ 'slug' SUPPRIMÉ
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('name', 'category', 'product_type', 'description', 'detailed_description')  # ✅ 'slug' SUPPRIMÉ
        }),
        ('Prix (en FCFA)', {
            'fields': ('price_fcfa', 'discount_price_fcfa'),
            'description': "Tous les prix sont en Francs CFA (FCFA). La conversion vers d'autres devises est automatique."
        }),
        ('Images', {
            'fields': ('image', 'back_image')
        }),
        ('Stock et visibilité', {
            'fields': ('stock', 'display_stock', 'is_featured', 'is_active')
        }),
        ('Statistiques (lecture seule)', {
            'fields': ('rating', 'reviews_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    # ✅ SUPPRESSION TOTALE de prepopulated_fields (inutile)
    # prepopulated_fields = {'slug': ('name',)}  # ❌ SUPPRIMÉ
    
    # Méthodes d'affichage personnalisées
    def price_fcfa_display(self, obj):
        return f"{obj.price_fcfa:,.0f} FCFA".replace(',', ' ')
    price_fcfa_display.short_description = 'Prix FCFA'
    price_fcfa_display.admin_order_field = 'price_fcfa'
    
    def discount_price_fcfa_display(self, obj):
        if obj.discount_price_fcfa:
            return f"{obj.discount_price_fcfa:,.0f} FCFA".replace(',', ' ')
        return "—"
    discount_price_fcfa_display.short_description = 'Prix réduit FCFA'


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'alt_text', 'uploaded_at']
    list_filter = ['product']
    search_fields = ['product__name', 'alt_text']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    # ✅ CORRECTION : Utilisation de total_amount_fcfa au lieu de total_amount
    list_display = [
        'order_number', 
        'user', 
        'total_amount_fcfa_display',
        'status', 
        'currency_used', 
        'created_at'
    ]
    
    list_filter = ['status', 'created_at', 'currency_used']
    search_fields = ['order_number', 'user__username', 'user__email']
    readonly_fields = [
        'order_number', 
        'total_amount_fcfa', 
        'tax_amount_fcfa', 
        'shipping_cost_fcfa',
        'total_amount_converted',
        'created_at', 
        'updated_at'
    ]
    
    fieldsets = (
        ('Informations commande', {
            'fields': ('order_number', 'user', 'status', 'currency_used')
        }),
        ('Montants (FCFA)', {  # ✅ Titre explicite
            'fields': ('total_amount_fcfa', 'tax_amount_fcfa', 'shipping_cost_fcfa', 'total_amount_converted')
        }),
        ('Adresses', {
            'fields': ('shipping_address', 'billing_address')
        }),
        ('Paiement', {
            'fields': ('payment_method', 'payment_status')
        }),
        ('Notes', {
            'fields': ('customer_notes', 'admin_notes')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at', 'shipped_at', 'delivered_at'),
            'classes': ('collapse',)
        }),
    )
    
    def total_amount_fcfa_display(self, obj):
        return f"{obj.total_amount_fcfa:,.0f} FCFA".replace(',', ' ')
    total_amount_fcfa_display.short_description = 'Total FCFA'
    total_amount_fcfa_display.admin_order_field = 'total_amount_fcfa'


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    # ✅ CORRECTION : Utilisation de price_fcfa et total_fcfa
    list_display = ['order', 'product', 'quantity', 'price_fcfa_display', 'total_fcfa_display']
    list_filter = ['order']
    search_fields = ['product__name', 'order__order_number']
    readonly_fields = ['price_fcfa', 'total_fcfa', 'price_converted', 'total_converted']
    
    fieldsets = (
        ('Informations produit', {
            'fields': ('order', 'product', 'quantity')
        }),
        ('Prix (FCFA)', {  # ✅ Titre explicite
            'fields': ('price_fcfa', 'total_fcfa')
        }),
        ('Prix converti', {
            'fields': ('price_converted', 'total_converted'),
            'classes': ('collapse',)
        }),
    )
    
    def price_fcfa_display(self, obj):
        return f"{obj.price_fcfa:,.0f} FCFA".replace(',', ' ')
    price_fcfa_display.short_description = 'Prix unitaire FCFA'
    
    def total_fcfa_display(self, obj):
        return f"{obj.total_fcfa:,.0f} FCFA".replace(',', ' ')
    total_fcfa_display.short_description = 'Total FCFA'


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'rating', 'is_verified', 'created_at']
    list_filter = ['rating', 'is_verified', 'created_at']
    search_fields = ['product__name', 'user__username', 'comment']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(UserCurrencyPreference)
class UserCurrencyPreferenceAdmin(admin.ModelAdmin):
    list_display = ['user', 'preferred_currency']
    search_fields = ['user__username', 'user__email']
    list_filter = ['preferred_currency']