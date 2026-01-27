from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import Category, Product, Order, OrderItem, Review
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta
import random

class Command(BaseCommand):
    help = 'Remplit la base de données avec des données de test'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Début du remplissage de la base de données...'))

        # Créer des catégories
        categories = []
        categories_data = [ 
            {'name': 'Cafés dosettes', 'description': 'Les meilleurs cafés ....................'},
            {'name': 'Cafés en capsules', 'description': 'Cafés de qualité premium ..............'},
            {'name': 'Cafés en grains', 'description': 'Cafés de qualité premium en grains'},
            {'name': 'Cafés Moulus', 'description': 'Cafés moulus de qualité premium'},
            {'name': 'Cafés Americains', 'description': 'Cafés américains traditionnels'},
            {'name': 'Pains baguettes', 'description': 'Pains frais préparés quotidiennement'},
            {'name': 'Gros Pains', 'description': 'Pains  traditionnels'},
            {'name': 'Pains court', 'description': 'Pains court ...............................'},
            {'name': 'Petit pains', 'description': 'Pains sains et nutritifs'},
            {'name': 'Machines à capsules', 'description': 'Machines pour café professionnel'},
            {'name': 'Machines à dosettes', 'description': 'Machines pour café artisanal'},
        ]

        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={'description': cat_data['description'], 'is_active': True}
            )
            categories.append(category)
            if created:
                self.stdout.write(f'✓ Catégorie créée: {category.name}')

        # Créer des produits
        products_data = [
            {
                'name': 'Café Arabica Premium',
                'category': categories[0],
                'product_type': 'cafe',
                'description': 'Café arabica de haute qualité avec un goût riche et velouté',
                'price': Decimal('15.99'),
                'discount_price': Decimal('12.99'),
                'stock': 50,
                'rating': 4.8,
                'reviews_count': 120
            },
            {
                'name': 'Café Robusta Intense',
                'category': categories[0],
                'product_type': 'cafe',
                'description': 'Café robusta intense avec une belle crema',
                'price': Decimal('12.99'),
                'discount_price': None,
                'stock': 75,
                'rating': 4.5,
                'reviews_count': 85
            },
            {
                'name': 'Café Éthiopie Yirgacheffe',
                'category': categories[1],
                'product_type': 'cafe',
                'description': 'Café d\'Éthiopie avec notes florales délicates',
                'price': Decimal('18.99'),
                'discount_price': Decimal('15.99'),
                'stock': 30,
                'rating': 4.9,
                'reviews_count': 150
            },
            {
                'name': 'Pain Baguette Française',
                'category': categories[2],
                'product_type': 'pain',
                'description': 'Baguette traditionnelle française avec croûte croquante',
                'price': Decimal('4.99'),
                'discount_price': None,
                'stock': 100,
                'rating': 4.7,
                'reviews_count': 200
            },
            {
                'name': 'Pain Complet Bio',
                'category': categories[3],
                'product_type': 'pain',
                'description': 'Pain complet biologique riche en fibres',
                'price': Decimal('6.99'),
                'discount_price': Decimal('5.99'),
                'stock': 60,
                'rating': 4.6,
                'reviews_count': 95
            },
            {
                'name': 'Machine Espresso DeLuxe',
                'category': categories[4],
                'product_type': 'machine',
                'description': 'Machine espresso automatique avec broyeur intégré',
                'price': Decimal('299.99'),
                'discount_price': Decimal('249.99'),
                'stock': 15,
                'rating': 4.9,
                'reviews_count': 65
            },
            {
                'name': 'Machine à Café Manuelle',
                'category': categories[5],
                'product_type': 'machine',
                'description': 'Machine manuelle pour café artisanal',
                'price': Decimal('89.99'),
                'discount_price': None,
                'stock': 25,
                'rating': 4.4,
                'reviews_count': 40
            },
            {
                'name': 'Café Mélange Maison',
                'category': categories[0],
                'product_type': 'cafe',
                'description': 'Mélange spécial de nos meilleurs crus',
                'price': Decimal('14.99'),
                'discount_price': Decimal('11.99'),
                'stock': 80,
                'rating': 4.7,
                'reviews_count': 110
            },
        ]

        products = []
        for prod_data in products_data:
            product, created = Product.objects.get_or_create(
                name=prod_data['name'],
                defaults={
                    'category': prod_data['category'],
                    'product_type': prod_data['product_type'],
                    'description': prod_data['description'],
                    'detailed_description': f"Détails complets: {prod_data['description']}. Ce produit est soigneusement sélectionné pour vous offrir la meilleure qualité.",
                    'price': prod_data['price'],
                    'discount_price': prod_data['discount_price'],
                    'stock': prod_data['stock'],
                    'rating': prod_data['rating'],
                    'reviews_count': prod_data['reviews_count'],
                    'is_featured': random.choice([True, False]),
                    'is_active': True
                }
            )
            products.append(product)
            if created:
                self.stdout.write(f'✓ Produit créé: {product.name}')

        # Créer un utilisateur test s'il n'existe pas
        user, created = User.objects.get_or_create(
            username='client@obidon.com',
            defaults={
                'email': 'client@obidon.com',
                'first_name': 'Jean',
                'last_name': 'Dupont',
            }
        )
        if created:
            user.set_password('password123')
            user.save()
            self.stdout.write(f'✓ Utilisateur créé: {user.username}')

        # Créer des commandes
        for i in range(5):
            order_number = f'CMD-{timezone.now().year}-{1000 + i}'
            order, created = Order.objects.get_or_create(
                order_number=order_number,
                defaults={
                    'user': user,
                    'status': random.choice(['pending', 'confirmed', 'shipped', 'delivered']),
                    'total_amount': Decimal(random.randint(50, 500)),
                    'tax_amount': Decimal(random.randint(5, 50)),
                    'shipping_cost': Decimal('10.00'),
                    'shipping_address': '123 Rue de Paris, 75000 Paris',
                    'billing_address': '123 Rue de Paris, 75000 Paris',
                    'payment_method': random.choice(['card', 'transfer', 'paypal']),
                    'payment_status': 'completed',
                    'admin_notes': f'Commande #{i+1}',
                    'created_at': timezone.now() - timedelta(days=random.randint(1, 30))
                }
            )
            
            if created:
                # Ajouter des articles à la commande
                for product in random.sample(products, k=random.randint(1, 3)):
                    quantity = random.randint(1, 3)
                    price = product.get_price
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=quantity,
                        price=price,
                        total=price * quantity
                    )
                self.stdout.write(f'✓ Commande créée: {order.order_number}')

        # Créer des avis
        review_titles = [
            'Excellent produit!',
            'Très satisfait',
            'Conforme à mes attentes',
            'Produit de qualité',
            'Recommandé',
            'Je le reprends',
            'Parfait',
            'Livraison rapide'
        ]

        review_comments = [
            'Produit conforme à la description, très satisfait de mon achat.',
            'Excellent rapport qualité-prix, je recommande vivement.',
            'Livraison rapide et produit de très bonne qualité.',
            'Conforme à mes attentes, je suis très satisfait.',
            'Très bon produit, à conseiller à tous les amateurs.',
            'Je suis ravi de cet achat, c\'est du haut de gamme.',
            'Produit excellent, je repasserai commande sans hésiter.',
            'Parfait ! Exactement ce que j\'attendais.'
        ]

        for product in products:
            for _ in range(random.randint(2, 5)):
                review, created = Review.objects.get_or_create(
                    product=product,
                    user=user,
                    defaults={
                        'rating': random.randint(4, 5),
                        'title': random.choice(review_titles),
                        'comment': random.choice(review_comments),
                        'is_verified': True
                    }
                )
                if created:
                    self.stdout.write(f'✓ Avis créé pour: {product.name}')
                break  # Une seule review par user/product

        self.stdout.write(self.style.SUCCESS('✓ Base de données remplie avec succès!'))
        self.stdout.write(self.style.SUCCESS(f'✓ {len(categories)} catégories créées'))
        self.stdout.write(self.style.SUCCESS(f'✓ {len(products)} produits créés'))
        self.stdout.write(self.style.SUCCESS('✓ 5 commandes créées'))
        self.stdout.write(self.style.SUCCESS('✓ Avis créés'))
