"""
Management command to set up initial currency exchange rates
"""
from django.core.management.base import BaseCommand
from catalog.models import CurrencyRate


class Command(BaseCommand):
    help = 'Set up initial currency exchange rates'

    def handle(self, *args, **options):
        # Sample exchange rates (these should be updated with real rates)
        rates = [
            # USD to other currencies
            ('USD', 'KES', 150.0),
            ('USD', 'EUR', 0.85),
            ('USD', 'GBP', 0.73),
            ('USD', 'NGN', 750.0),
            ('USD', 'ZAR', 18.5),
            ('USD', 'GHS', 12.0),
            ('USD', 'EGP', 31.0),
            ('USD', 'MAD', 9.8),
            ('USD', 'TND', 3.1),
            
            # EUR to other currencies
            ('EUR', 'KES', 176.5),
            ('EUR', 'GBP', 0.86),
            ('EUR', 'NGN', 882.4),
            ('EUR', 'ZAR', 21.8),
            ('EUR', 'GHS', 14.1),
            ('EUR', 'EGP', 36.5),
            ('EUR', 'MAD', 11.5),
            ('EUR', 'TND', 3.65),
            
            # GBP to other currencies
            ('GBP', 'KES', 205.5),
            ('GBP', 'NGN', 1027.4),
            ('GBP', 'ZAR', 25.3),
            ('GBP', 'GHS', 16.4),
            ('GBP', 'EGP', 42.5),
            ('GBP', 'MAD', 13.4),
            ('GBP', 'TND', 4.25),
            
            # KES to other currencies
            ('KES', 'NGN', 5.0),
            ('KES', 'ZAR', 0.123),
            ('KES', 'GHS', 0.08),
            ('KES', 'EGP', 0.207),
            ('KES', 'MAD', 0.065),
            ('KES', 'TND', 0.021),
        ]
        
        created_count = 0
        updated_count = 0
        
        for from_currency, to_currency, rate in rates:
            rate_obj, created = CurrencyRate.objects.get_or_create(
                from_currency=from_currency,
                to_currency=to_currency,
                defaults={'rate': rate, 'is_active': True}
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created rate: {from_currency} -> {to_currency} = {rate}')
                )
            else:
                rate_obj.rate = rate
                rate_obj.is_active = True
                rate_obj.save()
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'Updated rate: {from_currency} -> {to_currency} = {rate}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully processed {len(rates)} currency rates. '
                f'Created: {created_count}, Updated: {updated_count}'
            )
        )
