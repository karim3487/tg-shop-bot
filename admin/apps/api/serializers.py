from rest_framework import serializers

from cart.models import CartItem
from catalog.models import Category, Product, ProductImage
from faq.models import FAQItem
from orders.models import Order, OrderItem


class ProductImageSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = ProductImage
        fields = ("id", "url", "order")

    def get_url(self, obj):
        request = self.context.get("request")
        if obj.image and hasattr(obj.image, "url"):
            url = obj.image.url
            if request:
                return request.build_absolute_uri(url)
            return url
        return None


class CategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ("id", "name", "parent", "children")

    def get_children(self, obj):
        return list(obj.children.filter(is_active=True).values("id", "name"))


class ProductListSerializer(serializers.ModelSerializer):
    thumbnail = serializers.SerializerMethodField()
    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = Product
        fields = ("id", "name", "price", "category", "category_name", "thumbnail")

    def get_thumbnail(self, obj):
        # Use prefetched images if available to avoid N+1
        images = obj.images.all()
        if images:
            return ProductImageSerializer(images[0], context=self.context).data
        return None


class ProductDetailSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Product
        fields = ("id", "name", "description", "price", "category", "images", "created_at")


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.filter(is_active=True),
        source="product",
        write_only=True,
    )
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ("id", "product", "product_id", "quantity", "subtotal")

    def get_subtotal(self, obj):
        return str(obj.product.price * obj.quantity)


class OrderItemSerializer(serializers.ModelSerializer):
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ("id", "product_name", "price", "quantity", "subtotal")

    def get_subtotal(self, obj):
        return str(obj.price * obj.quantity)


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = Order
        fields = ("id", "full_name", "phone", "address", "status", "status_display",
                  "total_price", "items", "created_at")
        read_only_fields = ("id", "status", "total_price", "created_at")


class CreateOrderSerializer(serializers.Serializer):
    full_name = serializers.CharField(max_length=255)
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True, default="")
    address = serializers.CharField()


class FAQItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQItem
        fields = ("id", "question", "answer")
