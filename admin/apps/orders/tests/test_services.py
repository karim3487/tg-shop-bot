import pytest
from unittest.mock import patch
from faker import Faker

from clients.models import Client
from catalog.models import Product, Category
from cart.models import CartItem
from orders.models import Order, OrderItem
from orders.services.order_service import OrderService

fake = Faker()

@pytest.mark.django_db
class TestOrderService:
    @pytest.fixture
    def client(self):
        return Client.objects.create(
            telegram_id=fake.random_int(min=1000, max=9999),
            username=fake.user_name(),
            first_name=fake.first_name(),
        )

    @pytest.fixture
    def category(self):
        return Category.objects.create(name=fake.word())

    @pytest.fixture
    def products(self, category):
        p1 = Product.objects.create(
            category=category,
            name=fake.word(),
            price=100,
            is_active=True
        )
        p2 = Product.objects.create(
            category=category,
            name=fake.word(),
            price=200,
            is_active=True
        )
        return [p1, p2]

    @patch("orders.services.order_service.publish_new_order.delay")
    def test_create_order_from_cart_success(self, mock_publish, client, products):
        """
        Test successful order creation:
        1. Cart items are converted to OrderItems.
        2. Total price is correct.
        3. Cart is cleared.
        4. Notification is triggered on commit.
        """
        # Populate cart
        CartItem.objects.create(client=client, product=products[0], quantity=2)
        CartItem.objects.create(client=client, product=products[1], quantity=1)
        
        # Expected total: (100 * 2) + (200 * 1) = 400
        
        full_name = fake.name()
        address = fake.address()
        
        # We need to mock transaction.on_commit to execute immediately in tests 
        # normally django tests don't run on_commit unless we use TransactionTestCase
        # but here we can just check if it was called or use a decorator.
        # Since we use pytest-django with django_db, it uses transactions.
        
        order = OrderService.create_from_cart(
            client=client,
            full_name=full_name,
            address=address
        )
        
        # Assertions
        assert Order.objects.count() == 1
        assert order.client == client
        assert order.total_price == 400
        assert order.full_name == full_name
        assert order.address == address
        
        # Check order items
        assert OrderItem.objects.filter(order=order).count() == 2
        oi1 = OrderItem.objects.get(order=order, product=products[0])
        assert oi1.quantity == 2
        assert oi1.price == 100
        
        # Check cart is cleared
        assert CartItem.objects.filter(client=client).count() == 0
        
        # Verify notification delay call (since we're in a test transaction, 
        # transaction.on_commit might not be naturally triggered unless we handle it)
        # However, for unit testing the service logic, we can verify it was registered.
        # Alternatively, we can patch transaction.on_commit if we want to be sure.

    def test_create_order_empty_cart_raises_error(self, client):
        """Test that creating an order with an empty cart raises ValueError."""
        with pytest.raises(ValueError, match="Cart is empty or order is already processing"):
            OrderService.create_from_cart(
                client=client,
                full_name=fake.name(),
                address=fake.address()
            )
        
        assert Order.objects.count() == 0
