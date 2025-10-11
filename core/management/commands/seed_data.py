from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone
from django.utils.text import slugify

from accounts.models import CustomerAddress
from catalog.models import (
    Tag,
    Category,
    Product,
    ProductPrice,
    CurrencyRate,
)
from checkout.models import Address, Order, OrderItem


class Command(BaseCommand):
    help = "Seed the database with sample data for development and demos."

    def handle(self, *args, **options):
        with transaction.atomic():
            self.stdout.write(self.style.WARNING("Seeding database..."))

            users = self._create_users()
            tags = self._create_tags()
            categories = self._create_categories()
            products = self._create_products(categories)
            self._assign_tags_to_products(products, tags)
            self._create_regional_prices(products)
            self._create_currency_rates()
            self._create_orders(users, products)

            self.stdout.write(self.style.SUCCESS("Database seeded successfully."))

    def _create_users(self):
        user_specs = [
            {
                "username": "jdoe",
                "email": "jane.doe@example.com",
                "first_name": "Jane",
                "last_name": "Doe",
                "password": "password123",
                "profile": {
                    "phone": "+254700000001",
                    "gender": "female",
                    "preferred_currency": "KES",
                    "email_verified": True,
                },
                "addresses": [
                    {
                        "address_type": "shipping",
                        "full_name": "Jane Doe",
                        "phone": "+254700000001",
                        "line1": "123 Riverside Drive",
                        "line2": "Apartment 4B",
                        "city": "Nairobi",
                        "postal_code": "00100",
                        "county": "Nairobi",
                        "country": "Kenya",
                        "is_default": True,
                    }
                ],
            },
            {
                "username": "jbloggs",
                "email": "joe.bloggs@example.com",
                "first_name": "Joe",
                "last_name": "Bloggs",
                "password": "password123",
                "profile": {
                    "phone": "+254700000002",
                    "gender": "male",
                    "preferred_currency": "USD",
                    "email_verified": True,
                },
                "addresses": [
                    {
                        "address_type": "both",
                        "full_name": "Joe Bloggs",
                        "phone": "+254700000002",
                        "line1": "78 Mawingu Lane",
                        "line2": "",
                        "city": "Mombasa",
                        "postal_code": "80100",
                        "county": "Mombasa",
                        "country": "Kenya",
                        "is_default": True,
                    }
                ],
            },
        ]

        created_users = []
        for spec in user_specs:
            defaults = {
                "email": spec["email"],
                "first_name": spec["first_name"],
                "last_name": spec["last_name"],
            }
            user, created = User.objects.get_or_create(
                username=spec["username"], defaults=defaults
            )
            if created:
                user.set_password(spec["password"])
                user.save()
            else:
                User.objects.filter(pk=user.pk).update(**defaults)

            profile = user.profile
            for attr, value in spec["profile"].items():
                setattr(profile, attr, value)
            profile.email_verified = spec["profile"].get("email_verified", False)
            profile.save()

            for address_spec in spec["addresses"]:
                CustomerAddress.objects.update_or_create(
                    customer=user,
                    address_type=address_spec["address_type"],
                    line1=address_spec["line1"],
                    defaults={
                        key: value
                        for key, value in address_spec.items()
                        if key not in {"address_type", "line1"}
                    },
                )

            created_users.append(user)

        return created_users

    def _create_tags(self):
        tag_specs = [
            {
                "name": "Gold",
                "slug": "gold",
                "color": "#FFD700",
                "description": "Gold jewellery",
            },
            {
                "name": "Silver",
                "slug": "silver",
                "color": "#C0C0C0",
                "description": "Sterling silver items",
            },
            {
                "name": "Diamond",
                "slug": "diamond",
                "color": "#B9F2FF",
                "description": "Diamond studded pieces",
            },
            {
                "name": "Pearl",
                "slug": "pearl",
                "color": "#F5F5F5",
                "description": "Pearl and mother-of-pearl jewellery",
            },
            {
                "name": "Handcrafted",
                "slug": "handcrafted",
                "color": "#CD7F32",
                "description": "Handcrafted jewellery",
            },
        ]

        tags = []
        for spec in tag_specs:
            tag, _ = Tag.objects.update_or_create(
                slug=spec["slug"],
                defaults=spec,
            )
            tags.append(tag)
        return tags

    def _create_categories(self):
        category_specs = [
            {
                "name": "Rings",
                "description": "Engagement, wedding, and fashion rings",
                "gender": "unisex",
                "sort_order": 1,
            },
            {
                "name": "Necklaces",
                "description": "Necklaces and pendants",
                "gender": "women",
                "sort_order": 2,
            },
            {
                "name": "Bracelets",
                "description": "Bracelets and bangles",
                "gender": "unisex",
                "sort_order": 3,
            },
        ]

        categories = []
        for spec in category_specs:
            slug = slugify(spec["name"])
            category, _ = Category.objects.update_or_create(
                slug=slug,
                defaults={**spec, "slug": slug},
            )
            categories.append(category)
        return {category.slug: category for category in categories}

    def _create_products(self, categories):
        product_specs = [
            {
                "name": "Aurora Diamond Ring",
                "category_slug": "rings",
                "price_cents": 1500000,
                "compare_price_cents": 1800000,
                "sku": "RING-AURORA-001",
                "stock_quantity": 12,
                "material": "gold",
                "carat": "18K",
                "stone_type": "Diamond",
                "stone_count": 1,
                "size": "7",
                "weight_grams": 18,
                "short_description": "Brilliant solitaire diamond ring set in 18K gold.",
            },
            {
                "name": "Celeste Pearl Necklace",
                "category_slug": "necklaces",
                "price_cents": 850000,
                "compare_price_cents": 950000,
                "sku": "NECK-CELESTE-001",
                "stock_quantity": 8,
                "material": "pearl",
                "stone_type": "Pearl",
                "stone_count": 32,
                "size": "18 inch",
                "weight_grams": 22,
                "short_description": "Cultured pearl necklace with gold clasp.",
            },
            {
                "name": "Luna Silver Bracelet",
                "category_slug": "bracelets",
                "price_cents": 320000,
                "compare_price_cents": 320000,
                "sku": "BRAC-LUNA-001",
                "stock_quantity": 25,
                "material": "silver",
                "stone_type": "",
                "stone_count": 0,
                "size": "Adjustable",
                "weight_grams": 15,
                "short_description": "Polished sterling silver bracelet with clasp.",
            },
        ]

        products = []
        for spec in product_specs:
            category = categories.get(spec["category_slug"])
            if not category:
                continue

            slug = slugify(spec["sku"])
            cleaned_defaults = {
                key: value
                for key, value in spec.items()
                if key != "category_slug"
            }
            defaults = {
                **cleaned_defaults,
                "category": category,
                "slug": slug,
                "description": spec["short_description"],
                "track_inventory": True,
                "is_featured": True,
                "is_active": True,
            }
            product, _ = Product.objects.update_or_create(
                sku=spec["sku"],
                defaults=defaults,
            )
            products.append(product)
        return products

    def _assign_tags_to_products(self, products, tags):
        tag_map = {tag.slug: tag for tag in tags}
        product_tag_map = {
            "RING-AURORA-001": ["gold", "diamond"],
            "NECK-CELESTE-001": ["pearl", "handcrafted"],
            "BRAC-LUNA-001": ["silver", "handcrafted"],
        }

        for product in products:
            desired_tags = product_tag_map.get(product.sku, [])
            product.tags.clear()
            for tag_slug in desired_tags:
                tag = tag_map.get(tag_slug)
                if tag:
                    product.tags.add(tag)

    def _create_regional_prices(self, products):
        price_specs = [
            {
                "sku": "RING-AURORA-001",
                "entries": [
                    {"country_code": "KE", "currency": "KES", "price_cents": 1500000},
                    {"country_code": "US", "currency": "USD", "price_cents": 12000},
                ],
            },
            {
                "sku": "NECK-CELESTE-001",
                "entries": [
                    {"country_code": "KE", "currency": "KES", "price_cents": 850000},
                    {"country_code": "GB", "currency": "GBP", "price_cents": 6200},
                ],
            },
            {
                "sku": "BRAC-LUNA-001",
                "entries": [
                    {"country_code": "KE", "currency": "KES", "price_cents": 320000},
                    {"country_code": "ZA", "currency": "ZAR", "price_cents": 42000},
                ],
            },
        ]

        product_map = {product.sku: product for product in products}
        for spec in price_specs:
            product = product_map.get(spec["sku"])
            if not product:
                continue

            for entry in spec["entries"]:
                ProductPrice.objects.update_or_create(
                    product=product,
                    country_code=entry["country_code"],
                    currency=entry["currency"],
                    defaults={
                        "price_cents": entry["price_cents"],
                        "is_override": True,
                        "is_active": True,
                    },
                )

    def _create_currency_rates(self):
        rate_specs = [
            ("USD", "KES", "143.50"),
            ("GBP", "KES", "183.25"),
            ("USD", "EUR", "0.92"),
            ("EUR", "USD", "1.09"),
            ("KES", "USD", "0.0069"),
        ]

        for from_currency, to_currency, rate in rate_specs:
            CurrencyRate.objects.update_or_create(
                from_currency=from_currency,
                to_currency=to_currency,
                defaults={
                    "rate": rate,
                    "is_active": True,
                },
            )

    def _create_orders(self, users, products):
        if not users or not products:
            return

        product_map = {product.sku: product for product in products}
        user_map = {user.username: user for user in users}

        orders_specs = [
            {
                "username": "jdoe",
                "items": [
                    {"sku": "RING-AURORA-001", "quantity": 1},
                    {"sku": "BRAC-LUNA-001", "quantity": 2},
                ],
                "status": "processing",
                "payment_status": "paid",
                "payment_method": "mpesa",
                "shipping_cost_cents": 5000,
                "tax_cents": 2300,
            },
            {
                "username": "jbloggs",
                "items": [
                    {"sku": "NECK-CELESTE-001", "quantity": 1},
                ],
                "status": "confirmed",
                "payment_status": "pending",
                "payment_method": "card",
                "shipping_cost_cents": 5000,
                "tax_cents": 1800,
            },
        ]

        for spec in orders_specs:
            user = user_map.get(spec["username"])
            if not user:
                continue

            address_info = user.addresses.order_by("-is_default").first()
            if not address_info:
                continue

            order_address, _ = Address.objects.update_or_create(
                full_name=address_info.full_name,
                line1=address_info.line1,
                defaults={
                    "phone": address_info.phone,
                    "line2": address_info.line2,
                    "city": address_info.city,
                    "county": address_info.county,
                    "postal_code": address_info.postal_code,
                    "country": address_info.country,
                },
            )

            order_defaults = {
                "customer": user,
                "status": spec["status"],
                "payment_status": spec["payment_status"],
                "payment_method": spec["payment_method"],
                "shipping_cost_cents": spec["shipping_cost_cents"],
                "tax_cents": spec["tax_cents"],
                "notes": "Seeded order for demo purposes",
                "address": order_address,
            }

            order = Order.objects.create(**order_defaults)

            subtotal = 0
            for item in spec["items"]:
                product = product_map.get(item["sku"])
                if not product:
                    continue

                price_cents = product.price_cents
                quantity = item["quantity"]
                subtotal += price_cents * quantity

                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    price_cents=price_cents,
                    total_cents=price_cents * quantity,
                )

            Order.objects.filter(pk=order.pk).update(
                subtotal_cents=subtotal,
                total_cents=subtotal + spec["shipping_cost_cents"] + spec["tax_cents"],
                confirmed_at=timezone.now() if spec["status"] != "pending" else None,
            )
