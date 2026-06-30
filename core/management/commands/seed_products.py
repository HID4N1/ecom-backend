from decimal import Decimal

from django.core.management.base import BaseCommand

from core.commerce_data import COMMERCE_DATA
from core.models import Product


DEFAULT_STOCK = 100


class Command(BaseCommand):
    help = "Populate backend products from the commerce storefront data."

    def add_arguments(self, parser):
        parser.add_argument(
            "--stock",
            type=int,
            default=DEFAULT_STOCK,
            help=f"Stock quantity assigned to each seeded product. Default: {DEFAULT_STOCK}",
        )

    def handle(self, *args, **options):
        stock = options["stock"]
        created_count = 0
        updated_count = 0

        for collection in COMMERCE_DATA["productCollections"]:
            collection_title = collection["title"]

            for product in collection["products"]:
                image_name = product["image"].split("/")[-1]
                description = (
                    f"{product['description']} - {collection_title} - "
                    f"{product['quantity']}"
                )

                _, created = Product.objects.update_or_create(
                    name=product["name"],
                    defaults={
                        "description": description,
                        "price": Decimal(str(product["priceValue"])),
                        "stock": stock,
                        "image": f"products/{image_name}",
                    },
                )

                if created:
                    created_count += 1
                else:
                    updated_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Seeded products: {created_count} created, {updated_count} updated."
            )
        )
