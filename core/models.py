from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify
from django.utils import timezone
from decimal import Decimal

# ==============================================================================
# NOUVEAU MODÈLE : GESTION DYNAMIQUE DES TYPES DE PRODUITS
# ==============================================================================

class ProductType(models.Model):
    """
    Modèle dynamique pour gérer les types de produits.
    Remplace l'ancienne liste statique PRODUCT_TYPES.
    Permet à l'admin de créer de nouveaux types (ex: Thés, Chocolats) sans coder.
    """
    name = models.CharField(max_length=100, unique=True, verbose_name="Nom du type")
    slug = models.SlugField(unique=True, blank=True, help_text="Identifiant URL (généré automatiquement)")
    icon = models.CharField(
        max_length=50, 
        default='fa-box',
        verbose_name="Icône FontAwesome",
        help_text="Ex: fa-coffee, fa-bread-slice, fa-leaf (sans le préfixe 'fas')"
    )
    description = models.TextField(blank=True, verbose_name="Description courte")
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Type de produit"
        verbose_name_plural = "Types de produits"
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


# ==============================================================================
# CATÉGORIES
# ==============================================================================

class Category(models.Model):
    """Catégorie de produits avec gestion hiérarchique et affichage page d'accueil"""
    
    # Champs de base
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Hiérarchie
    parent = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='children',
        verbose_name="Catégorie parente"
    )
    
    # Affichage Page d'Accueil
    display_on_home = models.BooleanField(
        default=False, 
        verbose_name="Afficher sur la page d'accueil",
        help_text="Cochez pour afficher cette catégorie dans la grille d'accueil."
    )
    
    home_position = models.IntegerField(
        default=0, 
        verbose_name="Ordre d'affichage",
        help_text="Plus le chiffre est bas, plus la catégorie apparaît tôt."
    )

    # --- NOUVEAUX CHAMPS POUR LES FILTRES DYNAMIQUES ---
    ICON_CHOICES = [
        ('fa-coffee', '☕ Café'),
        ('fa-bread-slice', '🍞 Pain'),
        ('fa-mug-hot', '☕ Tasse/Machine'),
        ('fa-blender', '🌪 Mixeur'),
        ('fa-utensils', '🍴 Accessoires'),
        ('fa-wine-bottle', '🍷 Boissons'),
        ('fa-cookie', '🍪 Snacks'),
        ('fa-leaf', '🌿 Thé/Infusion'),
        ('fa-box-open', '📦 Général'),
        ('fa-th-large', '🔲 Tous'),
    ]
    
    icon = models.CharField(
        max_length=50, 
        choices=ICON_CHOICES, 
        default='fa-box-open',
        verbose_name="Icône du filtre",
        help_text="Icône affichée dans la barre de navigation supérieure."
    )
    
    is_filter_main = models.BooleanField(
        default=False,
        verbose_name="Afficher dans la barre de filtres ?",
        help_text="Si coché, cette catégorie apparaîtra dans la barre de navigation supérieure."
    )

    class Meta:
        ordering = ['home_position', 'name']
        verbose_name_plural = 'Categories'
        indexes = [
            models.Index(fields=['home_position']),
            models.Index(fields=['is_active']),
            models.Index(fields=['display_on_home']),
            models.Index(fields=['is_filter_main']),
        ]

    def __str__(self):
        if self.parent:
            return f"{self.parent.name} > {self.name}"
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    # --- MÉTHODES UTILITAIRES ---

    def get_absolute_url(self):
        """Retourne l'URL canonique de la catégorie"""
        from django.urls import reverse
        return reverse('core:products') + f'?category={self.slug}'

    @property
    def product_count(self):
        """Compte le nombre de produits actifs dans cette catégorie"""
        return self.products.filter(is_active=True).count()

    @property
    def has_products(self):
        """Vérifie si la catégorie contient au moins un produit actif"""
        return self.products.filter(is_active=True).exists()

    def get_image_url(self):
        """Retourne l'URL de l'image ou une image par défaut"""
        if self.image and hasattr(self.image, 'url'):
            return self.image.url
        first_product = self.products.filter(is_active=True, image__isnull=False).first()
        if first_product:
            return first_product.image.url
        return None 

    @property
    def short_description(self):
        """Retourne les 20 premiers mots de la description"""
        if self.description:
            words = self.description.split()
            if len(words) > 20:
                return ' '.join(words[:20]) + '...'
            return self.description
        return "Découvrez notre sélection exclusive de qualité supérieure."
    
    @property
    def icon_class(self):
        """Retourne la classe CSS complète pour l'icône"""
        return f"fas {self.icon}"


# ==============================================================================
# DEVISES & TAUX DE CHANGE
# ==============================================================================

class Currency(models.Model):
    """Modèle pour stocker les devises disponibles"""
    CODE_CHOICES = [
        ('XOF', 'Franc CFA'),
        ('EUR', 'Euro'),
        ('USD', 'Dollar américain'),
    ]
    
    code = models.CharField(max_length=3, unique=True, choices=CODE_CHOICES, verbose_name="Code devise")
    name = models.CharField(max_length=50, verbose_name="Nom")
    symbol = models.CharField(max_length=10, verbose_name="Symbole")
    flag = models.CharField(max_length=10, verbose_name="Emoji drapeau")
    is_default = models.BooleanField(default=False, verbose_name="Devise par défaut")
    is_active = models.BooleanField(default=True, verbose_name="Active")
    
    class Meta:
        verbose_name = "Devise"
        verbose_name_plural = "Devises"
        ordering = ['-is_default', 'code']
    
    def __str__(self):
        return f"{self.flag} {self.code} - {self.name}"
    
    @classmethod
    def get_default(cls):
        """Retourne la devise par défaut (FCFA)"""
        return cls.objects.filter(is_default=True).first() or cls.objects.filter(code='XOF').first()


class ExchangeRate(models.Model):
    """Modèle pour stocker les taux de change"""
    base_currency = models.ForeignKey(
        Currency, 
        on_delete=models.CASCADE, 
        related_name='base_rates',
        verbose_name="Devise de base"
    )
    target_currency = models.ForeignKey(
        Currency, 
        on_delete=models.CASCADE, 
        related_name='target_rates',
        verbose_name="Devise cible"
    )
    rate = models.DecimalField(
        max_digits=12, 
        decimal_places=6, 
        verbose_name="Taux de change",
        help_text="1 unité de devise de base = X unités de devise cible"
    )
    last_updated = models.DateTimeField(auto_now=True, verbose_name="Dernière mise à jour")
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    
    class Meta:
        verbose_name = "Taux de change"
        verbose_name_plural = "Taux de change"
        unique_together = ['base_currency', 'target_currency']
        ordering = ['base_currency', 'target_currency']
    
    def __str__(self):
        return f"{self.base_currency.code} → {self.target_currency.code}: {self.rate}"
    
    @classmethod
    def convert(cls, amount, from_currency_code, to_currency_code):
        if from_currency_code == to_currency_code:
            return amount
        try:
            rate = cls.objects.get(
                base_currency__code=from_currency_code,
                target_currency__code=to_currency_code,
                is_active=True
            )
            return amount * rate.rate
        except cls.DoesNotExist:
            try:
                inverse_rate = cls.objects.get(
                    base_currency__code=to_currency_code,
                    target_currency__code=from_currency_code,
                    is_active=True
                )
                return amount / inverse_rate.rate
            except cls.DoesNotExist:
                return amount


# ==============================================================================
# PRODUITS
# ==============================================================================

class Product(models.Model):
    """Produit du site - FCFA comme devise principale"""
    
    # ❌ L'ancienne liste statique est supprimée car remplacée par le modèle ProductType
    
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    
    # ✅ NOUVEAU : Relation dynamique vers ProductType
    product_type = models.ForeignKey(
        ProductType, 
        on_delete=models.PROTECT, # Empêche la suppression si des produits existent
        related_name='products',
        verbose_name="Type de produit"
    )
    
    description = models.TextField()
    detailed_description = models.TextField(blank=True)
    
    # PRIX EN FCFA
    price_fcfa = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        validators=[MinValueValidator(0)],
        verbose_name="Prix en FCFA",
        help_text="Prix en Francs CFA (devise principale)",
        default=0
    )
    discount_price_fcfa = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(0)],
        verbose_name="Prix réduit en FCFA",
        help_text="Prix réduit en Francs CFA"
    )
    
    image = models.ImageField(upload_to='products/')
    back_image = models.ImageField(
        upload_to='products/backs/',
        null=True,
        blank=True,
        verbose_name="Image verso (au survol)"
    )
    stock = models.IntegerField(
        default=0,
        blank=True,
        validators=[MinValueValidator(0)],
        verbose_name="Stock"
    )
    display_stock = models.BooleanField(
        default=True,
        verbose_name="Afficher le stock sur le site ?"
    )
    
    rating = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(5)])
    reviews_count = models.IntegerField(default=0)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['category']),
            models.Index(fields=['is_active']),
            models.Index(fields=['product_type']),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_image_url(self):
        if self.image and hasattr(self.image, 'url'):
            return self.image.url
        return "https://via.placeholder.com/600x400?text=Image+non+disponible"
    
    def get_back_image_url(self):
        if self.back_image and hasattr(self.back_image, 'url'):
            return self.back_image.url
        return None
    
    def get_price_in_currency(self, currency_code='XOF'):
        if currency_code == 'XOF':
            return self.price_fcfa
        return ExchangeRate.convert(self.price_fcfa, 'XOF', currency_code)
    
    def get_discount_price_in_currency(self, currency_code='XOF'):
        if not self.discount_price_fcfa:
            return None
        if currency_code == 'XOF':
            return self.discount_price_fcfa
        return ExchangeRate.convert(self.discount_price_fcfa, 'XOF', currency_code)

    @property
    def price(self):
        return self.price_fcfa

    @property
    def discount_price(self):
        return self.discount_price_fcfa

    @property
    def get_price(self):
        return self.discount_price_fcfa if self.discount_price_fcfa else self.price_fcfa

    @property
    def discount_percentage(self):
        if self.discount_price_fcfa and self.price_fcfa:
            return round(((self.price_fcfa - self.discount_price_fcfa) / self.price_fcfa) * 100)
        return 0
    
    @property
    def has_back_image(self):
        return bool(self.back_image)
    
    def get_price_display(self, currency_code='XOF', format_type='simple'):
        try:
            currency = Currency.objects.get(code=currency_code)
            symbol = currency.symbol
        except Currency.DoesNotExist:
            symbol = 'FCFA' if currency_code == 'XOF' else currency_code
        
        price = self.get_price_in_currency(currency_code)
        discount_price = self.get_discount_price_in_currency(currency_code)
        
        if format_type == 'simple':
            if discount_price:
                return f"{discount_price:,.0f} {symbol}".replace(',', ' ')
            return f"{price:,.0f} {symbol}".replace(',', ' ')
        elif format_type == 'full':
            if discount_price:
                return f"""
                <span style="text-decoration: line-through; color: #999;">{price:,.0f} {symbol}</span>
                <span style="color: #D32F2F; font-weight: bold;">{discount_price:,.0f} {symbol}</span>
                """
            return f"{price:,.0f} {symbol}".replace(',', ' ')
        return f"{price:,.0f} {symbol}".replace(',', ' ')


# ==============================================================================
# AUTRES MODÈLES (Galerie, Commandes, Avis...)
# ==============================================================================

class ProductImage(models.Model):
    """Images supplémentaires pour les produits"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='gallery_images')
    image = models.ImageField(upload_to='products/gallery/')
    alt_text = models.CharField(max_length=255, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image - {self.alt_text or 'Product Gallery'}"
    
    def get_image_url(self):
        if self.image and hasattr(self.image, 'url'):
            return self.image.url
        return "https://via.placeholder.com/100?text=Galerie"


class Order(models.Model):
    """Commande client - FCFA comme devise principale"""
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('confirmed', 'Confirmée'),
        ('shipped', 'Expédiée'),
        ('delivered', 'Livrée'),
        ('cancelled', 'Annulée'),
        ('refunded', 'Remboursée'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    order_number = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    total_amount_fcfa = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        verbose_name="Montant total en FCFA",
        default=0
    )
    tax_amount_fcfa = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        verbose_name="Taxe en FCFA"
    )
    shipping_cost_fcfa = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        verbose_name="Frais de livraison en FCFA"
    )
    
    currency_used = models.ForeignKey(
        Currency, 
        on_delete=models.SET_NULL, 
        null=True,
        verbose_name="Devise utilisée",
        related_name='orders'
    )
    
    total_amount_converted = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        default=0,
        verbose_name="Montant total converti"
    )
    
    shipping_address = models.TextField()
    billing_address = models.TextField()
    
    payment_method = models.CharField(max_length=50, default='card')
    payment_status = models.CharField(max_length=20, default='pending')
    
    customer_notes = models.TextField(blank=True)
    admin_notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    shipped_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Commande {self.order_number}"
    
    def save(self, *args, **kwargs):
        if not self.currency_used:
            self.currency_used = Currency.get_default()
        
        if self.currency_used and self.currency_used.code != 'XOF':
            self.total_amount_converted = ExchangeRate.convert(
                self.total_amount_fcfa, 'XOF', self.currency_used.code
            )
        else:
            self.total_amount_converted = self.total_amount_fcfa
        
        super().save(*args, **kwargs)
    
    @property
    def total_amount(self):
        return self.total_amount_fcfa


class OrderItem(models.Model):
    """Produit dans une commande - FCFA comme devise principale"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    
    price_fcfa = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        verbose_name="Prix unitaire en FCFA"
    )
    total_fcfa = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        verbose_name="Total en FCFA"
    )
    
    price_converted = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        default=0,
        verbose_name="Prix unitaire converti"
    )
    total_converted = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        default=0,
        verbose_name="Total converti"
    )

    def __str__(self):
        return f"{self.quantity}x {self.product.name}"
    
    def save(self, *args, **kwargs):
        self.price_fcfa = self.product.price_fcfa
        self.total_fcfa = self.price_fcfa * self.quantity
        
        if self.order.currency_used and self.order.currency_used.code != 'XOF':
            self.price_converted = ExchangeRate.convert(
                self.price_fcfa, 'XOF', self.order.currency_used.code
            )
            self.total_converted = ExchangeRate.convert(
                self.total_fcfa, 'XOF', self.order.currency_used.code
            )
        else:
            self.price_converted = self.price_fcfa
            self.total_converted = self.total_fcfa
        
        super().save(*args, **kwargs)
    
    @property
    def price(self):
        return self.price_fcfa
    
    @property
    def total(self):
        return self.total_fcfa


class Review(models.Model):
    """Avis client"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    title = models.CharField(max_length=200)
    comment = models.TextField()
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['product', '-created_at']),
            models.Index(fields=['user', '-created_at']),
        ]

    def __str__(self):
        return f"Avis de {self.user.username} - {self.product.name}"


class UserCurrencyPreference(models.Model):
    """Modèle pour stocker la préférence de devise de l'utilisateur"""
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='currency_preference'
    )
    preferred_currency = models.ForeignKey(
        Currency, 
        on_delete=models.SET_NULL, 
        null=True,
        verbose_name="Devise préférée"
    )
    
    class Meta:
        verbose_name = "Préférence de devise"
        verbose_name_plural = "Préférences de devise"
    
    def __str__(self):
        return f"{self.user.username} - {self.preferred_currency.code if self.preferred_currency else 'None'}"