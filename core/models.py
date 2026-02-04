from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify
from django.utils import timezone

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


class Product(models.Model):
    """Produit du site"""
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
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    discount_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(0)]
    )
    
    image = models.ImageField(upload_to='products/')
    back_image = models.ImageField(
        upload_to='products/backs/',
        null=True,
        blank=True,
        verbose_name="Image verso (au survol)",
        help_text="Image qui apparaîtra quand l'utilisateur survole l'image principale"
    )
    stock = models.IntegerField(
        default=0,
        blank=True,
        validators=[MinValueValidator(0)],
        verbose_name="Stock",
        help_text="Laisser vide = stock à 0 (rupture de stock)"
    )
    display_stock = models.BooleanField(
        default=True,
        verbose_name="Afficher le stock sur le site ?",
        help_text="Décochez si vous ne voulez PAS montrer le stock au public (ex: produits en précommande, stock caché...)"
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
    
    def get_thumbnail_url(self):
        """Retourne l'URL pour les miniatures"""
        if self.image and hasattr(self.image, 'url'):
            return self.image.url
        return "https://via.placeholder.com/100?text=Recto"


    @property
    def get_price(self):
        """Retourne le prix réduit s'il existe, sinon le prix normal"""
        return self.discount_price if self.discount_price else self.price

    @property
    def discount_percentage(self):
        """Calcule le pourcentage de réduction"""
        if self.discount_price and self.price:
            return round(((self.price - self.discount_price) / self.price) * 100)
        return 0
    
    @property
    def has_back_image(self):
        """Vérifie si le produit a une image verso"""
        return bool(self.back_image)
    
    

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
    """Commande client"""
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
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
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


class OrderItem(models.Model):
    """Produit dans une commande"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    price = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.quantity}x {self.product.name}"


class Review(models.Model):
    """Avis client"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    title = models.CharField(max_length=200)
    comment = models.TextField()
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ['product', 'user']

    def __str__(self):
        return f"Avis de {self.user.username} - {self.product.name}"


class Currency(models.Model):
    """Modèle pour stocker les devises disponibles"""
    code = models.CharField(max_length=3, unique=True, verbose_name="Code devise")
    name = models.CharField(max_length=50, verbose_name="Nom")
    symbol = models.CharField(max_length=10, verbose_name="Symbole")
    flag = models.CharField(max_length=10, verbose_name="Emoji drapeau")
    is_default = models.BooleanField(default=False, verbose_name="Devise par défaut")
    
    class Meta:
        verbose_name = "Devise"
        verbose_name_plural = "Devises"
        ordering = ['code']
    
    def __str__(self):
        return f"{self.code} - {self.name}"


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
        verbose_name="Taux de change"
    )
    last_updated = models.DateTimeField(auto_now=True, verbose_name="Dernière mise à jour")
    
    class Meta:
        verbose_name = "Taux de change"
        verbose_name_plural = "Taux de change"
        unique_together = ['base_currency', 'target_currency']
    
    def __str__(self):
        return f"{self.base_currency.code} -> {self.target_currency.code}: {self.rate}"


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