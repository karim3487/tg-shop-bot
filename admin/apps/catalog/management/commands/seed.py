import io
import random
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.db import transaction
from PIL import Image, ImageDraw, ImageFont

from catalog.models import Category, Product, ProductImage
from clients.models import Client
from faq.models import FAQItem
from orders.models import Order, OrderItem

User = get_user_model()


CATEGORIES = [
    {"name": "Электроника", "children": ["Смартфоны", "Ноутбуки", "Аксессуары"]},
    {"name": "Одежда", "children": ["Мужская", "Женская"]},
    {"name": "Продукты питания", "children": ["Напитки", "Снеки"]},
]

# (name, description, price, category, bg_color)
PRODUCTS = [
    ("iPhone 15 Pro", "Флагманский смартфон Apple", Decimal("89990"), "Смартфоны", (30, 30, 30)),
    ("Samsung Galaxy S24", "Флагман Samsung на Android", Decimal("74990"), "Смартфоны", (20, 40, 80)),
    ("MacBook Air M3", "Лёгкий ноутбук Apple", Decimal("129990"), "Ноутбуки", (50, 50, 50)),
    ("Lenovo ThinkPad X1", "Бизнес-ноутбук", Decimal("95000"), "Ноутбуки", (20, 20, 60)),
    ("AirPods Pro", "Беспроводные наушники Apple с ANC", Decimal("24990"), "Аксессуары", (200, 200, 200)),
    ("Кабель USB-C 1м", "Зарядный кабель USB-C", Decimal("990"), "Аксессуары", (80, 60, 20)),
    ("Футболка базовая", "Хлопковая футболка, разные цвета", Decimal("1490"), "Мужская", (180, 60, 60)),
    ("Джинсы slim fit", "Классические джинсы", Decimal("3990"), "Мужская", (40, 60, 120)),
    ("Платье летнее", "Лёгкое платье для лета", Decimal("2990"), "Женская", (180, 100, 140)),
    ("Кофе в зёрнах 1кг", "Арабика, средняя обжарка", Decimal("1290"), "Напитки", (80, 40, 10)),
    ("Протеиновый батончик", "Шоколадный, 60г", Decimal("190"), "Снеки", (100, 60, 20)),
]

CLIENTS = [
    {"telegram_id": 100000001, "username": "ivan_petrov", "first_name": "Иван", "last_name": "Петров"},
    {"telegram_id": 100000002, "username": "anna_k", "first_name": "Анна", "last_name": "Козлова"},
    {"telegram_id": 100000003, "username": None, "first_name": "Михаил", "last_name": "Сидоров"},
]

FAQ_ITEMS = [
    ("Как оформить заказ?", "Выберите товары, добавьте в корзину и нажмите «Оформить заказ»."),
    ("Какие способы оплаты доступны?", "Принимаем оплату картой через Telegram Payments."),
    ("Сколько времени занимает доставка?", "Доставка по городу 1–2 дня, по России 3–7 дней."),
    ("Как отследить заказ?", "После отправки вы получите трек-номер в боте."),
    ("Можно ли вернуть товар?", "Да, в течение 14 дней при сохранении товарного вида."),
]


def _make_image(label: str, bg_color: tuple, variant: int = 0) -> ContentFile:
    """Generate a 600×600 placeholder JPEG with a label."""
    # Slightly vary brightness for the second image
    r, g, b = bg_color
    if variant == 1:
        r = min(255, r + 40)
        g = min(255, g + 40)
        b = min(255, b + 40)

    img = Image.new("RGB", (600, 600), color=(r, g, b))
    draw = ImageDraw.Draw(img)

    # Draw a subtle grid pattern
    for x in range(0, 600, 60):
        draw.line([(x, 0), (x, 600)], fill=(min(255, r + 15), min(255, g + 15), min(255, b + 15)), width=1)
    for y in range(0, 600, 60):
        draw.line([(0, y), (600, y)], fill=(min(255, r + 15), min(255, g + 15), min(255, b + 15)), width=1)

    # Draw centered label (wrapped)
    text_color = (255, 255, 255) if (r * 0.299 + g * 0.587 + b * 0.114) < 128 else (30, 30, 30)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36)
        small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
    except OSError:
        font = ImageFont.load_default()
        small_font = font

    # Wrap label into lines of ~20 chars
    words = label.split()
    lines: list[str] = []
    current = ""
    for word in words:
        if len(current) + len(word) + 1 > 20:
            if current:
                lines.append(current)
            current = word
        else:
            current = f"{current} {word}".strip()
    if current:
        lines.append(current)

    total_height = len(lines) * 44
    y_start = (600 - total_height) // 2
    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=font)
        w = bbox[2] - bbox[0]
        draw.text(((600 - w) // 2, y_start + i * 44), line, fill=text_color, font=font)

    # Variant label
    variant_text = f"Фото {variant + 1}"
    bbox = draw.textbbox((0, 0), variant_text, font=small_font)
    draw.text((600 - bbox[2] - 10, 600 - bbox[3] - 10), variant_text, fill=text_color, font=small_font)

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=85)
    return ContentFile(buf.getvalue())


class Command(BaseCommand):
    help = "Заполняет базу данных тестовыми данными"

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Удалить существующие данные перед заполнением",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options["clear"]:
            self.stdout.write("Удаление существующих данных...")
            OrderItem.objects.all().delete()
            Order.objects.all().delete()
            Client.objects.all().delete()
            ProductImage.objects.all().delete()
            Product.objects.all().delete()
            Category.objects.all().delete()
            FAQItem.objects.all().delete()
            self.stdout.write(self.style.WARNING("Данные удалены."))

        # Categories
        self.stdout.write("Создание категорий...")
        cat_map: dict[str, Category] = {}
        for cat_data in CATEGORIES:
            parent, _ = Category.objects.get_or_create(name=cat_data["name"])
            cat_map[cat_data["name"]] = parent
            for child_name in cat_data.get("children", []):
                child, _ = Category.objects.get_or_create(name=child_name, defaults={"parent": parent})
                cat_map[child_name] = child
        self.stdout.write(f"  Категорий: {len(cat_map)}")

        # Products + images
        self.stdout.write("Создание товаров и загрузка изображений в MinIO...")
        products_created = 0
        images_uploaded = 0
        product_map: dict[str, Product] = {}
        for name, description, price, cat_name, bg_color in PRODUCTS:
            category = cat_map.get(cat_name)
            product, created = Product.objects.get_or_create(
                name=name,
                defaults={"description": description, "price": price, "category": category},
            )
            product_map[name] = product
            if created:
                products_created += 1
                num_images = random.randint(1, 6)
                for i in range(num_images):
                    img_file = _make_image(name, bg_color, variant=i)
                    slug = name.lower().replace(" ", "_")[:30]
                    filename = f"{slug}_{i + 1}.jpg"
                    pi = ProductImage(product=product, order=i)
                    pi.image.save(filename, img_file, save=True)
                    images_uploaded += 1
        self.stdout.write(f"  Товаров: {products_created}, изображений загружено: {images_uploaded}")

        # Clients
        self.stdout.write("Создание клиентов...")
        clients_created = 0
        created_clients: list[Client] = []
        for c in CLIENTS:
            client, created = Client.objects.get_or_create(
                telegram_id=c["telegram_id"],
                defaults={
                    "username": c["username"],
                    "first_name": c["first_name"],
                    "last_name": c["last_name"],
                },
            )
            created_clients.append(client)
            if created:
                clients_created += 1
        self.stdout.write(f"  Клиентов: {clients_created}")

        # Orders
        self.stdout.write("Создание заказов...")
        sample_orders = [
            {
                "client": created_clients[0],
                "full_name": "Иван Петров",
                "phone": "+79001234567",
                "address": "г. Москва, ул. Ленина, д. 1, кв. 10",
                "status": Order.Status.DELIVERED,
                "items": [
                    {"product": product_map["AirPods Pro"], "quantity": 1},
                    {"product": product_map["Кабель USB-C 1м"], "quantity": 2},
                ],
            },
            {
                "client": created_clients[1],
                "full_name": "Анна Козлова",
                "phone": "+79007654321",
                "address": "г. Санкт-Петербург, пр. Невский, д. 50",
                "status": Order.Status.PROCESSING,
                "items": [
                    {"product": product_map["Платье летнее"], "quantity": 1},
                ],
            },
            {
                "client": created_clients[2],
                "full_name": "Михаил Сидоров",
                "phone": "+79009998877",
                "address": "г. Казань, ул. Баумана, д. 5",
                "status": Order.Status.PENDING,
                "items": [
                    {"product": product_map["Протеиновый батончик"], "quantity": 5},
                    {"product": product_map["Кофе в зёрнах 1кг"], "quantity": 2},
                ],
            },
        ]
        orders_created = 0
        for order_data in sample_orders:
            total = sum(item["product"].price * item["quantity"] for item in order_data["items"])
            order = Order.objects.create(
                client=order_data["client"],
                full_name=order_data["full_name"],
                phone=order_data["phone"],
                address=order_data["address"],
                status=order_data["status"],
                total_price=total,
            )
            for item in order_data["items"]:
                OrderItem.objects.create(
                    order=order,
                    product=item["product"],
                    product_name=item["product"].name,
                    price=item["product"].price,
                    quantity=item["quantity"],
                )
            orders_created += 1
        self.stdout.write(f"  Заказов: {orders_created}")

        # FAQ
        self.stdout.write("Создание FAQ...")
        faq_created = 0
        for question, answer in FAQ_ITEMS:
            _, created = FAQItem.objects.get_or_create(question=question, defaults={"answer": answer})
            if created:
                faq_created += 1
        self.stdout.write(f"  FAQ: {faq_created}")

        # Superuser
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser(username="admin", password="admin", email="admin@example.com")
            self.stdout.write(self.style.WARNING("  Создан superuser: admin / admin"))

        self.stdout.write(self.style.SUCCESS("Seed завершён успешно."))
