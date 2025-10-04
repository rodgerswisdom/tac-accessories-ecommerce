from django.core.management.base import BaseCommand
from catalog.models import Category, Product, Tag


class Command(BaseCommand):
    help = 'Populate the database with sample jewellery data'

    def handle(self, *args, **options):
        self.stdout.write('Creating jewellery categories...')
        
        # Create main categories
        rings_women, created = Category.objects.get_or_create(
            name='Rings',
            defaults={
                'description': 'Elegant rings for women',
                'gender': 'women',
                'sort_order': 1
            }
        )
        
        necklaces_women, created = Category.objects.get_or_create(
            name='Necklaces',
            defaults={
                'description': 'Beautiful necklaces and pendants',
                'gender': 'women',
                'sort_order': 2
            }
        )
        
        earrings_women, created = Category.objects.get_or_create(
            name='Earrings',
            defaults={
                'description': 'Stunning earrings for every occasion',
                'gender': 'women',
                'sort_order': 3
            }
        )
        
        bracelets_women, created = Category.objects.get_or_create(
            name='Bracelets',
            defaults={
                'description': 'Charming bracelets and bangles',
                'gender': 'women',
                'sort_order': 4
            }
        )
        
        rings_men, created = Category.objects.get_or_create(
            name='Men\'s Rings',
            defaults={
                'description': 'Bold rings for men',
                'gender': 'men',
                'sort_order': 5
            }
        )
        
        chains_men, created = Category.objects.get_or_create(
            name='Men\'s Chains',
            defaults={
                'description': 'Strong and stylish chains for men',
                'gender': 'men',
                'sort_order': 6
            }
        )
        
        watches_unisex, created = Category.objects.get_or_create(
            name='Watches',
            defaults={
                'description': 'Luxury timepieces for everyone',
                'gender': 'unisex',
                'sort_order': 7
            }
        )
        
        self.stdout.write('Creating tags...')
        
        # Create tags
        gold_tag, created = Tag.objects.get_or_create(
            name='Gold',
            defaults={'color': '#FFD700', 'description': 'Pure gold jewellery'}
        )
        
        silver_tag, created = Tag.objects.get_or_create(
            name='Silver',
            defaults={'color': '#C0C0C0', 'description': 'Sterling silver pieces'}
        )
        
        diamond_tag, created = Tag.objects.get_or_create(
            name='Diamond',
            defaults={'color': '#B9F2FF', 'description': 'Diamond-studded jewellery'}
        )
        
        vintage_tag, created = Tag.objects.get_or_create(
            name='Vintage',
            defaults={'color': '#8B4513', 'description': 'Vintage and antique style'}
        )
        
        modern_tag, created = Tag.objects.get_or_create(
            name='Modern',
            defaults={'color': '#000000', 'description': 'Contemporary designs'}
        )
        
        luxury_tag, created = Tag.objects.get_or_create(
            name='Luxury',
            defaults={'color': '#800080', 'description': 'High-end luxury pieces'}
        )
        
        self.stdout.write('Creating sample products...')
        
        # Create sample products
        products_data = [
            {
                'name': 'Classic Gold Wedding Ring',
                'category': rings_women,
                'description': 'A timeless 18K gold wedding ring with a classic design that will last forever.',
                'short_description': 'Timeless 18K gold wedding ring',
                'price_cents': 45000,  # KES 450.00
                'compare_price_cents': 50000,
                'material': 'gold',
                'carat': '18K',
                'stock_quantity': 10,
                'is_featured': True,
                'is_new': False,
                'tags': [gold_tag, luxury_tag]
            },
            {
                'name': 'Diamond Solitaire Necklace',
                'category': necklaces_women,
                'description': 'Elegant diamond solitaire pendant on a delicate gold chain.',
                'short_description': 'Elegant diamond solitaire pendant',
                'price_cents': 125000,  # KES 1,250.00
                'compare_price_cents': 150000,
                'material': 'gold',
                'carat': '18K',
                'stone_type': 'Diamond',
                'stone_count': 1,
                'stock_quantity': 5,
                'is_featured': True,
                'is_bestseller': True,
                'tags': [gold_tag, diamond_tag, luxury_tag]
            },
            {
                'name': 'Pearl Drop Earrings',
                'category': earrings_women,
                'description': 'Beautiful pearl drop earrings with sterling silver settings.',
                'short_description': 'Elegant pearl drop earrings',
                'price_cents': 25000,  # KES 250.00
                'material': 'silver',
                'stone_type': 'Pearl',
                'stone_count': 2,
                'stock_quantity': 15,
                'is_new': True,
                'tags': [silver_tag, vintage_tag]
            },
            {
                'name': 'Gold Tennis Bracelet',
                'category': bracelets_women,
                'description': 'Stunning tennis bracelet with alternating diamonds and gold links.',
                'short_description': 'Diamond tennis bracelet',
                'price_cents': 85000,  # KES 850.00
                'material': 'gold',
                'carat': '14K',
                'stone_type': 'Diamond',
                'stone_count': 20,
                'stock_quantity': 3,
                'is_featured': True,
                'tags': [gold_tag, diamond_tag, luxury_tag]
            },
            {
                'name': 'Men\'s Gold Signet Ring',
                'category': rings_men,
                'description': 'Bold 18K gold signet ring with classic masculine design.',
                'short_description': 'Bold gold signet ring',
                'price_cents': 65000,  # KES 650.00
                'material': 'gold',
                'carat': '18K',
                'stock_quantity': 8,
                'is_featured': True,
                'tags': [gold_tag, modern_tag]
            },
            {
                'name': 'Men\'s Gold Chain',
                'category': chains_men,
                'description': 'Heavy 18K gold chain with Cuban link design.',
                'short_description': 'Heavy gold Cuban link chain',
                'price_cents': 95000,  # KES 950.00
                'material': 'gold',
                'carat': '18K',
                'stock_quantity': 6,
                'is_bestseller': True,
                'tags': [gold_tag, modern_tag]
            },
            {
                'name': 'Luxury Gold Watch',
                'category': watches_unisex,
                'description': 'Premium gold watch with Swiss movement and diamond markers.',
                'short_description': 'Luxury gold watch with diamonds',
                'price_cents': 250000,  # KES 2,500.00
                'compare_price_cents': 300000,
                'material': 'gold',
                'carat': '18K',
                'stone_type': 'Diamond',
                'stone_count': 12,
                'stock_quantity': 2,
                'is_featured': True,
                'is_bestseller': True,
                'tags': [gold_tag, diamond_tag, luxury_tag]
            },
            {
                'name': 'Silver Hoop Earrings',
                'category': earrings_women,
                'description': 'Classic sterling silver hoop earrings, perfect for everyday wear.',
                'short_description': 'Classic silver hoop earrings',
                'price_cents': 15000,  # KES 150.00
                'material': 'silver',
                'stock_quantity': 20,
                'is_new': True,
                'tags': [silver_tag, modern_tag]
            },
            {
                'name': 'Rose Gold Engagement Ring',
                'category': rings_women,
                'description': 'Romantic rose gold engagement ring with a brilliant cut diamond.',
                'short_description': 'Romantic rose gold engagement ring',
                'price_cents': 180000,  # KES 1,800.00
                'compare_price_cents': 200000,
                'material': 'gold',
                'carat': '18K',
                'stone_type': 'Diamond',
                'stone_count': 1,
                'stock_quantity': 4,
                'is_featured': True,
                'is_new': True,
                'tags': [gold_tag, diamond_tag, luxury_tag]
            },
            {
                'name': 'Men\'s Silver Chain',
                'category': chains_men,
                'description': 'Stylish sterling silver chain with modern design.',
                'short_description': 'Stylish silver chain',
                'price_cents': 35000,  # KES 350.00
                'material': 'silver',
                'stock_quantity': 12,
                'is_new': True,
                'tags': [silver_tag, modern_tag]
            }
        ]
        
        for product_data in products_data:
            tags = product_data.pop('tags', [])
            product, created = Product.objects.get_or_create(
                name=product_data['name'],
                defaults=product_data
            )
            if created:
                product.tags.set(tags)
                self.stdout.write(f'Created: {product.name}')
            else:
                self.stdout.write(f'Already exists: {product.name}')
        
        self.stdout.write(
            self.style.SUCCESS('Successfully populated jewellery data!')
        )
