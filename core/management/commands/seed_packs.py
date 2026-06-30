from decimal import Decimal

from django.core.management.base import BaseCommand

from core.commerce_data import COMMERCE_DATA
from core.models import Pack, PackProduct, Product


PACK_PRODUCTS = {
    "Pack Duo": [
        ("CLEAR 26", 1),
        ("TAN 26", 1),
    ],
    "Pack Sommeil": [
        ("CLEAR 30", 2),
    ],
    "Pack Performance": [
        ("TAN 30", 2),
    ],
    "Pack Annuel": [
        ("CLEAR 44", 2),
        ("TAN 44", 2),
    ],
}


class Command(BaseCommand):
    help = "Populate backend packs from the commerce storefront data."

    def handle(self, *args, **options):
        created_count = 0
        updated_count = 0

        for pack in COMMERCE_DATA["curatedPacks"]:
            pack_instance, created = Pack.objects.update_or_create(
                title=pack["title"],
                defaults={
                    "description": pack["description"],
                    "price": Decimal(str(pack["priceValue"])),
                    "cta": pack["cta"],
                    "includes": pack["includes"],
                },
            )
            pack_instance.pack_products.all().delete()

            for order, (product_name, quantity) in enumerate(PACK_PRODUCTS[pack["title"]]):
                product = Product.objects.get(name=product_name)
                PackProduct.objects.create(
                    pack=pack_instance,
                    product=product,
                    quantity=quantity,
                    order=order,
                )

            if created:
                created_count += 1
            else:
                updated_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Seeded packs: {created_count} created, {updated_count} updated."
            )
        )
