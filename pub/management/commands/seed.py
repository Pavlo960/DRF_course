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
        if not user.has_usable_password():
            user.set_password("beer12345")
            user.save()

        categories_data = [
            {"name": "Draft Beer", "description": "Fresh cold draft craft beer on tap"},
            {"name": "Bottled & Canned", "description": "Craft bottles and imported cans"},
            {"name": "Pub Snacks", "description": "Nuts, jerky, and tasty appetizers"},
        ]

        created_categories = {}
        for cat in categories_data:
            obj, _ = Category.objects.get_or_create(
                name=cat["name"],
                defaults={"description": cat["description"]}
            )
            created_categories[cat["name"]] = obj

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
                "name": "Smoked Beef Jerky",
                "category": created_categories["Pub Snacks"],
                "price_per_liter": 75.00,
                "description": "House-cured dried beef jerky seasoned with cracked black pepper.",
                "available": True,
            },
            {
                "name": "Salted Pretzel with Mustard",
                "category": created_categories["Pub Snacks"],
                "price_per_liter": 55.00,
                "description": "Warm Bavarian pretzel served with traditional spicy pub mustard.",
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