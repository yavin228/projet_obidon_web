from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify
from django.utils import timezone
from decimal import Decimal

class Category(models.Model):
    """Catégorie de produits"""
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


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
        """
        Convertit un montant d'une devise à une autre
        Retourne le montant converti ou le montant original si conversion impossible
        """
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
            # Si taux introuvable, essayer la conversion inverse
            try:
                inverse_rate = cls.objects.get(
                    base_currency__code=to_currency_code,
                    target_currency__code=from_currency_code,
                    is_active=True
                )
                return amount / inverse_rate.rate
            except cls.DoesNotExist:
                return amount  # Fallback: retourner le montant original


class Product(models.Model):
    """Produit du site - FCFA comme devise principale"""
    PRODUCT_TYPES = [
        ('cafe', 'Café'),
        ('pain', 'Pain'),
        ('machine', 'Machine à café'),
        ('accessoire', 'Accessoire'),
    ]

    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    product_type = models.CharField(max_length=50, choices=PRODUCT_TYPES)
    description = models.TextField()
    detailed_description = models.TextField(blank=True)
    
    # PRIX PRINCIPAL EN FCFA (devise par défaut) - CORRIGÉ
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
        """Retourne l'URL de l'image ou un placeholder si vide"""
        if self.image and hasattr(self.image, 'url'):
            return self.image.url
        return "https://via.placeholder.com/600x400?text=Image+non+disponible"
    
    def get_back_image_url(self):
        """Retourne l'URL de l'image verso ou None si vide"""
        if self.back_image and hasattr(self.back_image, 'url'):
            return self.back_image.url
        return None
    
    def get_price_in_currency(self, currency_code='XOF'):
        """
        Retourne le prix dans la devise spécifiée
        Utilise les taux de change pour la conversion
        """
        if currency_code == 'XOF':
            return self.price_fcfa
        
        # Convertir depuis FCFA vers la devise demandée
        return ExchangeRate.convert(self.price_fcfa, 'XOF', currency_code)
    
    def get_discount_price_in_currency(self, currency_code='XOF'):
        """
        Retourne le prix réduit dans la devise spécifiée
        """
        if not self.discount_price_fcfa:
            return None
        
        if currency_code == 'XOF':
            return self.discount_price_fcfa
        
        return ExchangeRate.convert(self.discount_price_fcfa, 'XOF', currency_code)

    @property
    def price(self):
        """Alias pour le prix en FCFA (rétrocompatibilité)"""
        return self.price_fcfa

    @property
    def discount_price(self):
        """Alias pour le prix réduit en FCFA (rétrocompatibilité)"""
        return self.discount_price_fcfa

    @property
    def get_price(self):
        """Retourne le prix réduit s'il existe, sinon le prix normal (en FCFA)"""
        return self.discount_price_fcfa if self.discount_price_fcfa else self.price_fcfa

    @property
    def discount_percentage(self):
        """Calcule le pourcentage de réduction basé sur les prix FCFA"""
        if self.discount_price_fcfa and self.price_fcfa:
            return round(((self.price_fcfa - self.discount_price_fcfa) / self.price_fcfa) * 100)
        return 0
    
    @property
    def has_back_image(self):
        """Vérifie si le produit a une image verso"""
        return bool(self.back_image)
    
    def get_price_display(self, currency_code='XOF', format_type='simple'):
        """Retourne le prix formaté dans la devise spécifiée"""
        # Obtenir le symbole de la devise
        try:
            currency = Currency.objects.get(code=currency_code)
            symbol = currency.symbol
        except Currency.DoesNotExist:
            symbol = 'FCFA' if currency_code == 'XOF' else currency_code
        
        # Obtenir le prix
        price = self.get_price_in_currency(currency_code)
        discount_price = self.get_discount_price_in_currency(currency_code)
        
        if format_type == 'simple':
            if discount_price:
                return f"{discount_price:,.0f} {symbol}".replace(',', ' ')
            return f"{price:,.0f} {symbol}".replace(',', ' ')
        
        elif format_type == 'full':
            if discount_price:
                return f"""
                <span style="text-decoration: line-through; color: #999;">
                    {price:,.0f} {symbol}
                </span>
                <span style="color: #D32F2F; font-weight: bold;">
                    {discount_price:,.0f} {symbol}
                </span>
                """
            return f"{price:,.0f} {symbol}".replace(',', ' ')
        
        return f"{price:,.0f} {symbol}".replace(',', ' ')


class ProductImage(models.Model):
    """Images supplémentaires pour les produits"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='gallery_images')
    image = models.ImageField(upload_to='products/gallery/')
    alt_text = models.CharField(max_length=255, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image - {self.alt_text or 'Product Gallery'}"
    
    def get_image_url(self):
        """Retourne l'URL de l'image de galerie ou un placeholder si vide"""
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
    
    # MONTANTS PRINCIPAUX EN FCFA (devise par défaut) - CORRIGÉ
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
    
    # Devise utilisée pour la commande
    currency_used = models.ForeignKey(
        Currency, 
        on_delete=models.SET_NULL, 
        null=True,
        verbose_name="Devise utilisée",
        related_name='orders'
    )
    
    # Montants convertis (pour référence)
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
        # Si currency_used n'est pas spécifié, utiliser FCFA par défaut
        if not self.currency_used:
            self.currency_used = Currency.get_default()
        
        # Si la devise utilisée n'est pas FCFA, convertir les montants
        if self.currency_used and self.currency_used.code != 'XOF':
            # Convertir de FCFA vers la devise utilisée
            self.total_amount_converted = ExchangeRate.convert(
                self.total_amount_fcfa, 'XOF', self.currency_used.code
            )
        else:
            self.total_amount_converted = self.total_amount_fcfa
        
        super().save(*args, **kwargs)
    
    @property
    def total_amount(self):
        """Alias pour rétrocompatibilité"""
        return self.total_amount_fcfa


class OrderItem(models.Model):
    """Produit dans une commande - FCFA comme devise principale"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    
    # PRIX EN FCFA (devise principale) - CORRIGÉ
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
    
    # Prix converti (pour référence)
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
        """Calculer automatiquement les totaux en FCFA"""
        # Utiliser le prix FCFA du produit
        self.price_fcfa = self.product.price_fcfa
        self.total_fcfa = self.price_fcfa * self.quantity
        
        # Si la commande a une devise différente de FCFA, convertir
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
        """Alias pour rétrocompatibilité"""
        return self.price_fcfa
    
    @property
    def total(self):
        """Alias pour rétrocompatibilité"""
        return self.total_fcfa


class Review(models.Model):
    """Avis client - VERSION CORRIGÉE POUR AVIS MULTIPLES"""
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
        # ✅ SUPPRESSION CRITIQUE : Contrainte UNIQUE supprimée pour autoriser les avis multiples
        # unique_together = ['product', 'user']  # ❌ LIGNE SUPPRIMÉE
        
        # ✅ AJOUT OPTIONNEL : Index pour performances (recommandé)
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