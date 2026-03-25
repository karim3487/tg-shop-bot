from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet

from api.authentication import TelegramInitDataAuthentication
from cart.services.cart_service import CartService
from catalog.models import Category, Product
from faq.models import FAQItem
from orders.models import Order
from orders.services.order_service import OrderService
from api.exceptions import OrderNotFoundError

from .serializers import (
    CartItemSerializer,
    CategorySerializer,
    CreateOrderSerializer,
    FAQItemSerializer,
    OrderSerializer,
    ProductDetailSerializer,
    ProductListSerializer,
)

_AUTH = [TelegramInitDataAuthentication]
_PERM = [IsAuthenticated]


@method_decorator(cache_page(60 * 15), name="dispatch")
class CategoryViewSet(ReadOnlyModelViewSet):
    """
    list   — GET /api/categories/          — top-level categories
    detail — GET /api/categories/{id}/
    products — GET /api/categories/{id}/products/
    """
    permission_classes = [AllowAny]
    serializer_class = CategorySerializer

    def get_queryset(self):
        qs = Category.objects.filter(is_active=True).prefetch_related("children")
        if self.action == "list":
            qs = qs.filter(parent__isnull=True)
        return qs

    @action(detail=True, methods=["get"])
    def products(self, request, pk=None):
        category = self.get_object()
        # Include products from all child categories
        category_ids = [category.pk]
        category_ids += list(
            Category.objects.filter(parent=category, is_active=True).values_list("id", flat=True)
        )
        products = (
            Product.objects.filter(category__in=category_ids, is_active=True)
            .prefetch_related("images")
            .select_related("category")
        )
        serializer = ProductListSerializer(products, many=True, context={"request": request})
        return Response(serializer.data)


@method_decorator(cache_page(60 * 15), name="dispatch")
class ProductViewSet(ReadOnlyModelViewSet):
    """
    list   — GET /api/products/?search=&category=
    detail — GET /api/products/{id}/
    """
    permission_classes = [AllowAny]

    def get_queryset(self):
        qs = Product.objects.filter(is_active=True).select_related("category").prefetch_related("images")
        search = self.request.query_params.get("search", "").strip()
        category_id = self.request.query_params.get("category", "").strip()
        if search:
            qs = qs.filter(name__icontains=search)
        if category_id:
            child_ids = Category.objects.filter(
                parent_id=category_id, is_active=True
            ).values_list("id", flat=True)
            qs = qs.filter(category_id__in=[int(category_id), *child_ids])
        return qs

    def get_serializer_class(self):
        if self.action == "retrieve":
            return ProductDetailSerializer
        return ProductListSerializer

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["request"] = self.request
        return ctx


@method_decorator(cache_page(60 * 15), name="dispatch")
class FAQViewSet(ReadOnlyModelViewSet):
    """
    list — GET /api/faq/
    """
    permission_classes = [AllowAny]
    serializer_class = FAQItemSerializer
    queryset = FAQItem.objects.filter(is_active=True)


class CartView(APIView):
    """
    GET    /api/cart/           — list items
    POST   /api/cart/           — add/update item {product_id, quantity}
    DELETE /api/cart/           — clear cart
    DELETE /api/cart/{id}/      — remove specific item
    """

    authentication_classes = _AUTH
    permission_classes = _PERM

    def get(self, request):
        items = CartService.get_items(request.user)
        total = CartService.calculate_total(request.user)
        serializer = CartItemSerializer(items, many=True, context={"request": request})
        return Response({"items": serializer.data, "total": str(total)})

    def post(self, request):
        serializer = CartItemSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        CartService.add_or_update_item(
            client=request.user,
            product=serializer.validated_data["product"],
            quantity=serializer.validated_data.get("quantity", 1),
        )

        # Refresh data for response
        items = CartService.get_items(request.user)
        total = CartService.calculate_total(request.user)
        out = CartItemSerializer(items, many=True, context={"request": request})
        return Response({"items": out.data, "total": str(total)}, status=status.HTTP_200_OK)

    def delete(self, request, item_id=None):
        CartService.remove_item(request.user, item_id)
        return Response(status=status.HTTP_204_NO_CONTENT)


class OrderView(APIView):
    """
    GET  /api/orders/      — list user's orders
    POST /api/orders/      — create order from cart
    GET  /api/orders/{id}/ — order detail
    """

    authentication_classes = _AUTH
    permission_classes = _PERM

    def get(self, request, order_id=None):
        if order_id:
            try:
                order = Order.objects.prefetch_related("items").get(pk=order_id, client=request.user)
            except Order.DoesNotExist:
                raise OrderNotFoundError()
            return Response(OrderSerializer(order).data)

        orders = Order.objects.filter(client=request.user).prefetch_related("items")
        return Response(OrderSerializer(orders, many=True).data)

    def post(self, request):
        serializer = CreateOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        order = OrderService.create_from_cart(
            client=request.user,
            full_name=data["full_name"],
            address=data["address"],
            phone=data.get("phone"),
        )

        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

    def patch(self, request, order_id=None):
        if not order_id:
            # We can let serializers handle it normally or raise our standard exception, but typically 400.
            from api.exceptions import InvalidRequestStateError
            raise InvalidRequestStateError("Order ID required.")

        order = OrderService.mark_as_paid(order_id=order_id, client=request.user)

        return Response(OrderSerializer(order).data, status=status.HTTP_200_OK)



def health_check(request):
    """
    Simple health check for Docker/Railway.
    """
    from django.db import connection
    from django.http import JsonResponse

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        return JsonResponse({"status": "ok", "database": "ok"})
    except Exception as e:
        return JsonResponse({"status": "error", "database": str(e)}, status=500)
