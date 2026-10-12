from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from pub.models import Category, MenuItem  # підкоригуй назви моделей, якщо вони у тебе відрізняються


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
            obj, created = Category.objects.get_or_create(
                name=cat["name"],
                defaults={"description": cat["description"]}
            )
            created_categories[cat["name"]] = obj
        items_data = [
            {
                "name": "Lviv Golden Ale",
                "category": created_categories["Draft Beer"],
                "price": "85.00",
                "description": "Crisp local ale with subtle caramel notes and light bitterness.",
            },
            {
                "name": "IPA Citra Haze",
                "category": created_categories["Draft Beer"],
                "price": "110.00",
                "description": "Juicy, tropical aroma with intense citrus hop flavor.",
            },
            {
                "name": "Oatmeal Stout",
                "category": created_categories["Draft Beer"],
                "price": "95.00",
                "description": "Smooth dark beer with dark chocolate and roasted coffee roast.",
            },
            {
                "name": "Smoked Beef Jerky",
                "category": created_categories["Pub Snacks"],
                "price": "75.00",
                "description": "House-cured dried beef jerky seasoned with cracked black pepper.",
            },
            {
                "name": "Salted Pretzel with Mustard",
                "category": created_categories["Pub Snacks"],
                "price": "55.00",
                "description": "Warm Bavarian pretzel served with traditional spicy pub mustard.",
            },
        ]

        for item in items_data:
            MenuItem.objects.get_or_create(
                name=item["name"],
                defaults={
                    "category": item["category"],
                    "price": item["price"],
                    "description": item["description"],
                }
            )

        self.stdout.write(self.style.SUCCESS("BeerHub database successfully seeded!"))