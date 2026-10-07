from django.core.management.base import BaseCommand
from pub.models import MenuItem, Order


class Command(BaseCommand):
    help = 'Seed the database with sample data'

    def handle(self, *args, **options):
        if MenuItem.objects.exists():
            self.stdout.write(self.style.WARNING('Data already exists, skipping.'))
            return

        beer1 = MenuItem.objects.create(name='Waissburg Lager', description='Світле фільтроване пиво', price_per_liter=74.00, available=True)
        beer2 = MenuItem.objects.create(name='Stout', description='Темне нефільтроване пиво', price_per_liter=85.00, available=True)
        
        Order.objects.create(menu_item=beer1, volume=1.5, customer_name='Oleg')
        Order.objects.create(menu_item=beer2, volume=0.5, customer_name='Andriy')

        self.stdout.write(self.style.SUCCESS('Done.'))