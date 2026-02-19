from django.contrib import admin
from .models import (
    Category, Currency, ExchangeRate, Product, ProductImage, 
    Order, OrderItem, Review, UserCurrencyPreference
)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = [
        'name', 
        'parent', 
        'slug', 
        'display_on_home', 
        'home_position', 
        'is_active', 
        'created_at'
    ]
    
    # CORRECTION ICI : J'ai supprimé 'is_featured' qui n'existe pas dans le modèle Category
    list_filter = [
        'is_active', 
        'display_on_home', 
        'parent'
    ]
    
    search_fields = ['name', 'description', 'parent__name']
    prepopulated_fields = {'slug': ('name',)}
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('name', 'slug', 'parent'),
            'description': "Le champ 'Parent' permet de créer des sous-catégories (hiérarchie)."
        }),
        ('Contenu', {
            'fields': ('description', 'image')
        }),
        ('Affichage Page d\'Accueil', {
            'fields': ('display_on_home', 'home_position'),
            'description': "Cochez 'Afficher sur la page d'accueil' et définissez l'ordre (0 = premier)."
        }),
        ('Statut', {
            'fields': ('is_active',)
        }),
        ('Dates (Lecture seule)', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'symbol', 'flag', 'is_default', 'is_active']
    list_filter = ['is_default', 'is_active']
    search_fields = ['code', 'name']
    
    fieldsets = (
        ('Informations Devise', {
            'fields': ('code', 'name', 'symbol', 'flag')
        }),
        ('Configuration', {
            'fields': ('is_default', 'is_active')
        }),
    )


@admin.register(ExchangeRate)
class ExchangeRateAdmin(admin.ModelAdmin):
    list_display = ['base_currency', 'target_currency', 'rate', 'is_active', 'last_updated']
    list_filter = ['is_active', 'base_currency', 'target_currency']
    search_fields = ['base_currency__code', 'target_currency__code']
    readonly_fields = ['last_updated']
    
    fieldsets = (
        ('Conversion', {
            'fields': ('base_currency', 'target_currency', 'rate'),
            'description': "Définissez le taux : 1 unité de devise de base = X unités de devise cible."
        }),
        ('Statut', {
            'fields': ('is_active', 'last_updated')
        }),
    )


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
    readonly_fields = ['rating', 'reviews_count', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('name', 'slug', 'category', 'product_type', 'description', 'detailed_description')
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
    
    prepopulated_fields = {'slug': ('name',)}
    
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
    list_display = ['product', 'alt_text', 'uploaded_at', 'image_preview']
    list_filter = ['product']
    search_fields = ['product__name', 'alt_text']
    
    def image_preview(self, obj):
        if obj.image:
            from django.utils.html import format_html
            return format_html('<img src="{}" style="max-height: 50px; border-radius: 4px;" />', obj.image.url)
        return "Aucune image"
    image_preview.short_description = "Aperçu"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'order_number', 
        'user', 
        'total_amount_fcfa_display',
        'status', 
        'currency_used', 
        'created_at',
        'payment_status'
    ]
    
    list_filter = ['status', 'payment_status', 'created_at', 'currency_used']
    search_fields = ['order_number', 'user__username', 'user__email', 'user__first_name']
    readonly_fields = [
        'order_number', 
        'total_amount_fcfa', 
        'tax_amount_fcfa', 
        'shipping_cost_fcfa',
        'total_amount_converted',
        'created_at', 
        'updated_at',
        'shipped_at',
        'delivered_at'
    ]
    
    fieldsets = (
        ('Informations commande', {
            'fields': ('order_number', 'user', 'status', 'currency_used')
        }),
        ('Montants (FCFA)', {
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
        ('Chronologie', {
            'fields': ('created_at', 'updated_at', 'shipped_at', 'delivered_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_confirmed', 'mark_as_shipped', 'mark_as_delivered']

    def mark_as_confirmed(self, request, queryset):
        queryset.update(status='confirmed')
        self.message_user(request, "Les commandes sélectionnées ont été confirmées.")
    mark_as_confirmed.short_description = "Marquer comme confirmée"

    def mark_as_shipped(self, request, queryset):
        queryset.update(status='shipped')
        self.message_user(request, "Les commandes sélectionnées ont été expédiées.")
    mark_as_shipped.short_description = "Marquer comme expédiée"

    def mark_as_delivered(self, request, queryset):
        queryset.update(status='delivered')
        self.message_user(request, "Les commandes sélectionnées ont été livrées.")
    mark_as_delivered.short_description = "Marquer comme livrée"
    
    def total_amount_fcfa_display(self, obj):
        return f"{obj.total_amount_fcfa:,.0f} FCFA".replace(',', ' ')
    total_amount_fcfa_display.short_description = 'Total FCFA'
    total_amount_fcfa_display.admin_order_field = 'total_amount_fcfa'


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'quantity', 'price_fcfa_display', 'total_fcfa_display']
    list_filter = ['order__status', 'order__created_at']
    search_fields = ['product__name', 'order__order_number']
    readonly_fields = ['price_fcfa', 'total_fcfa', 'price_converted', 'total_converted']
    
    fieldsets = (
        ('Informations produit', {
            'fields': ('order', 'product', 'quantity')
        }),
        ('Prix (FCFA)', {
            'fields': ('price_fcfa', 'total_fcfa')
        }),
        ('Prix converti (Référence)', {
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
    list_display = ['product', 'user', 'rating', 'is_verified', 'created_at', 'short_comment']
    list_filter = ['rating', 'is_verified', 'created_at', 'product__category']
    search_fields = ['product__name', 'user__username', 'comment', 'title']
    readonly_fields = ['created_at', 'updated_at']
    
    actions = ['mark_as_verified', 'mark_as_unverified']

    def mark_as_verified(self, request, queryset):
        queryset.update(is_verified=True)
        self.message_user(request, "Les avis sélectionnés ont été vérifiés.")
    mark_as_verified.short_description = "Marquer comme vérifié"

    def mark_as_unverified(self, request, queryset):
        queryset.update(is_verified=False)
        self.message_user(request, "Les avis sélectionnés ont été marqués comme non vérifiés.")
    mark_as_unverified.short_description = "Marquer comme non vérifié"

    def short_comment(self, obj):
        return f"{obj.comment[:50]}..." if len(obj.comment) > 50 else obj.comment
    short_comment.short_description = "Commentaire"


@admin.register(UserCurrencyPreference)
class UserCurrencyPreferenceAdmin(admin.ModelAdmin):
    list_display = ['user', 'preferred_currency', 'get_user_email']
    search_fields = ['user__username', 'user__email', 'user__first_name']
    list_filter = ['preferred_currency']
    
    def get_user_email(self, obj):
        return obj.user.email
    get_user_email.short_description = "Email utilisateur"