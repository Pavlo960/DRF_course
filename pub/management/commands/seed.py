from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from pub.models import Category, MenuItem


class Command(BaseCommand):
    help = "Seed initial data for BeerHub (categories, menu items, sample user)"

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Seeding data..."))

        User = get_user_model()
        user, _ = User.objects.get_or_create(
            username="barman",
            defaults={"email": "barman@beerhub.local"}
        )
        user.is_staff = True
        user.is_superuser = True
        # Demo credentials for local development only
        user.set_password("beer12345")
        user.save()
        self.stdout.write(self.style.WARNING("Demo superuser: barman / beer12345 (dev only)"))

        category_names = [
            "Draft Beer",
            "Bottled & Canned",
        ]

        created_categories = {}
        for cat_name in category_names:
            obj, _ = Category.objects.get_or_create(name=cat_name)
            created_categories[cat_name] = obj

        items_data = [
            {
                "name": "Lviv Golden Ale",
                "category": created_categories["Draft Beer"],
                "price_per_liter": 85.00,
                "description": "Crisp local ale with subtle caramel notes and light bitterness.",
                "available": True,
            },
            {
                "name": "IPA Citra Haze",
                "category": created_categories["Draft Beer"],
                "price_per_liter": 110.00,
                "description": "Juicy, tropical aroma with intense citrus hop flavor.",
                "available": True,
            },
            {
                "name": "Oatmeal Stout",
                "category": created_categories["Draft Beer"],
                "price_per_liter": 95.00,
                "description": "Smooth dark beer with dark chocolate and roasted coffee roast.",
                "available": True,
            },
            {
                "name": "Baltic Porter",
                "category": created_categories["Bottled & Canned"],
                "price_per_liter": 120.00,
                "description": "Strong dark lager with notes of plum, licorice and toasted malt.",
                "available": True,
            },
        ]

        for item in items_data:
            MenuItem.objects.get_or_create(
                name=item["name"],
                defaults={
                    "category": item["category"],
                    "price_per_liter": item["price_per_liter"],
                    "description": item["description"],
                    "available": item["available"],
                }
            )

        self.stdout.write(self.style.SUCCESS("BeerHub database successfully seeded!"))