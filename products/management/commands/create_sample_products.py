from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from users.models import UserTypes
from products.models import Product, ProductCategory
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Create sample products with different price types for testing'

    def add_arguments(self, parser):
        parser.add_argument('--supplier-username', type=str, help='Username of the supplier to create products for')
        parser.add_argument('--clear', action='store_true', help='Clear existing sample products')

    def handle(self, *args, **options):
        supplier_username = options.get('supplier_username')
        clear_existing = options.get('clear', False)
        
        if clear_existing:
            self.stdout.write(self.style.WARNING('Clearing existing sample products...'))
            Product.objects.filter(name_en__startswith='Sample ').delete()
            ProductCategory.objects.filter(name_en__startswith='Sample ').delete()
            self.stdout.write(self.style.SUCCESS('Existing sample products cleared.'))
            return

        supplier_user = None
        if supplier_username:
            try:
                supplier_user = User.objects.get(username=supplier_username, role=UserTypes.SUPPLIER)
            except User.DoesNotExist:
                raise CommandError(f'Supplier user "{supplier_username}" does not exist or is not a supplier.')
        else:
            # Try to find an existing supplier or create one
            try:
                supplier_user = User.objects.get(role=UserTypes.SUPPLIER)
            except User.DoesNotExist:
                self.stdout.write(self.style.WARNING('No supplier user found. Creating a default supplier user...'))
                supplier_user = User.objects.create_user(
                    username='default_supplier',
                    email='supplier@example.com',
                    password='password123',
                    role=UserTypes.SUPPLIER,
                    business_type='General Supplier',
                    is_verified=True
                )
                self.stdout.write(self.style.SUCCESS(f'Default supplier user "{supplier_user.username}" created.'))

        self.stdout.write(self.style.SUCCESS(f'Using supplier: {supplier_user.username}'))

        # Create sample categories if they don't exist
        categories_data = [
            {'name_en': 'Frozen Beef', 'name_ar': 'لحوم بقرية مجمدة'},
            {'name_en': 'Frozen Dairy', 'name_ar': 'ألبان مجمدة'},
            {'name_en': 'Frozen Potatoes', 'name_ar': 'بطاطس مجمدة'},
            {'name_en': 'Frozen Fruits', 'name_ar': 'فواكه مجمدة'},
            {'name_en': 'Frozen Lamb', 'name_ar': 'لحوم ضأن مجمدة'},
            {'name_en': 'Frozen Offals', 'name_ar': 'أحشاء مجمدة'},
            {'name_en': 'Frozen Poultry', 'name_ar': 'دواجن مجمدة'},
            {'name_en': 'Frozen Seafood', 'name_ar': 'مأكولات بحرية مجمدة'},
            {'name_en': 'Frozen Vegetables', 'name_ar': 'خضروات مجمدة'},
        ]

        categories = {}
        for cat_data in categories_data:
            category, created = ProductCategory.objects.get_or_create(
                name_en=cat_data['name_en'],
                defaults={'name_ar': cat_data['name_ar']}
            )
            categories[cat_data['name_en']] = category
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created category: {category.name_en}'))

        # Define 12 specific products based on the provided image
        products_data = [
            {
                'name_en': 'Tenderloin', 'name_ar': 'فيليه بقري', 'category': categories['Frozen Beef'],
                'end_user_price': 350.00, 'retail_price_b2c': 320.00,
                'retail_price_corporate': 300.00, 'retail_price_horeca': 310.00,
                'wholesale_price': 290.00, 'wholesale_min_quantity': 50, 'unit': 'KG', 'unit_size': 1
            },
            {
                'name_en': 'Unsalted Butter 25kg', 'name_ar': 'زبدة بدون ملح ٢٥ كجم', 'category': categories['Frozen Dairy'],
                'end_user_price': 2500.00, 'retail_price_b2c': 2300.00,
                'retail_price_corporate': 2200.00, 'retail_price_horeca': 2250.00,
                'wholesale_price': 2100.00, 'wholesale_min_quantity': 5, 'unit': 'Package', 'unit_size': 25
            },
            {
                'name_en': 'Straight Cut Fries 10mm', 'name_ar': 'بطاطس صوابع 10 مم', 'category': categories['Frozen Potatoes'],
                'end_user_price': 80.00, 'retail_price_b2c': 75.00,
                'retail_price_corporate': 70.00, 'retail_price_horeca': 72.00,
                'wholesale_price': 68.00, 'wholesale_min_quantity': 10, 'unit': 'KG', 'unit_size': 1
            },
            {
                'name_en': 'Frozen Strawberry', 'name_ar': 'فراولة مجمدة', 'category': categories['Frozen Fruits'],
                'end_user_price': 120.00, 'retail_price_b2c': 110.00,
                'retail_price_corporate': 100.00, 'retail_price_horeca': 105.00,
                'wholesale_price': 95.00, 'wholesale_min_quantity': 20, 'unit': 'KG', 'unit_size': 1
            },
            {
                'name_en': 'Lamb Leg', 'name_ar': 'فخذ ضاني', 'category': categories['Frozen Lamb'],
                'end_user_price': 400.00, 'retail_price_b2c': 380.00,
                'retail_price_corporate': 360.00, 'retail_price_horeca': 370.00,
                'wholesale_price': 350.00, 'wholesale_min_quantity': 5, 'unit': 'KG', 'unit_size': 1
            },
            {
                'name_en': 'Beef Liver', 'name_ar': 'كبدة بقري', 'category': categories['Frozen Offals'],
                'end_user_price': 150.00, 'retail_price_b2c': 140.00,
                'retail_price_corporate': 130.00, 'retail_price_horeca': 135.00,
                'wholesale_price': 125.00, 'wholesale_min_quantity': 10, 'unit': 'KG', 'unit_size': 1
            },
            {
                'name_en': 'Whole Chicken 900g', 'name_ar': 'فرخة كاملة ٩٠٠ جم', 'category': categories['Frozen Poultry'],
                'end_user_price': 150.00, 'retail_price_b2c': 140.00,
                'retail_price_corporate': 130.00, 'retail_price_horeca': 135.00,
                'wholesale_price': 125.00, 'wholesale_min_quantity': 20, 'unit': 'Piece', 'unit_size': 0.9
            },
            {
                'name_en': 'Frozen Tilapia', 'name_ar': 'بلطي مجمد', 'category': categories['Frozen Seafood'],
                'end_user_price': 180.00, 'retail_price_b2c': 170.00,
                'retail_price_corporate': 160.00, 'retail_price_horeca': 165.00,
                'wholesale_price': 155.00, 'wholesale_min_quantity': 15, 'unit': 'KG', 'unit_size': 1
            },
            {
                'name_en': 'Frozen Green Peas', 'name_ar': 'بسلة مجمدة', 'category': categories['Frozen Vegetables'],
                'end_user_price': 70.00, 'retail_price_b2c': 65.00,
                'retail_price_corporate': 60.00, 'retail_price_horeca': 62.00,
                'wholesale_price': 58.00, 'wholesale_min_quantity': 25, 'unit': 'KG', 'unit_size': 1
            },
            {
                'name_en': 'Ribeye Roll', 'name_ar': 'ريباي رول', 'category': categories['Frozen Beef'],
                'end_user_price': 380.00, 'retail_price_b2c': 350.00,
                'retail_price_corporate': 330.00, 'retail_price_horeca': 340.00,
                'wholesale_price': 320.00, 'wholesale_min_quantity': 40, 'unit': 'KG', 'unit_size': 1
            },
            {
                'name_en': 'Boneless Chicken Breast', 'name_ar': 'صدور فراخ فيليه', 'category': categories['Frozen Poultry'],
                'end_user_price': 220.00, 'retail_price_b2c': 200.00,
                'retail_price_corporate': 190.00, 'retail_price_horeca': 195.00,
                'wholesale_price': 185.00, 'wholesale_min_quantity': 30, 'unit': 'KG', 'unit_size': 1
            },
            {
                'name_en': 'Frozen Shrimp 40/50', 'name_ar': 'جمبري مجمد ٤٠/٥٠', 'category': categories['Frozen Seafood'],
                'end_user_price': 500.00, 'retail_price_b2c': 480.00,
                'retail_price_corporate': 460.00, 'retail_price_horeca': 470.00,
                'wholesale_price': 450.00, 'wholesale_min_quantity': 10, 'unit': 'KG', 'unit_size': 1
            },
        ]

        for product_data in products_data:
            product, created = Product.objects.get_or_create(
                name_en=product_data['name_en'],
                defaults={
                    'name_ar': product_data['name_ar'],
                    'category': product_data['category'],
                    'end_user_price': product_data['end_user_price'],
                    'retail_price_b2c': product_data['retail_price_b2c'],
                    'retail_price_corporate': product_data['retail_price_corporate'],
                    'retail_price_horeca': product_data['retail_price_horeca'],
                    'wholesale_price': product_data['wholesale_price'],
                    'wholesale_min_quantity': product_data['wholesale_min_quantity'],
                    'unit': product_data['unit'],
                    'unit_size': product_data['unit_size'],
                    'supplier': supplier_user,
                    'stock_quantity': random.randint(100, 1000),
                    'is_available': True,
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created product: {product.name_en}'))
            else:
                self.stdout.write(self.style.WARNING(f'Product already exists: {product.name_en}'))

        self.stdout.write(self.style.SUCCESS('Sample products creation complete.'))
