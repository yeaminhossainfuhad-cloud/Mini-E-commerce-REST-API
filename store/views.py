from rest_framework import filters, permissions, viewsets
from rest_framework.exceptions import PermissionDenied

from django_filters.rest_framework import DjangoFilterBackend

from .filters import ProductFilter
from .models import Category, Order, Product
from .serializers import CategorySerializer, OrderSerializer, ProductSerializer


class IsAuthenticatedOrReadOnly(permissions.IsAuthenticatedOrReadOnly):
    """Anyone can read (GET/HEAD/OPTIONS); only logged-in users can write."""


class CategoryViewSet(viewsets.ModelViewSet):
    """
    Full CRUD for categories.
        GET    /api/categories/        - list all categories
        POST   /api/categories/        - create a category
        GET    /api/categories/{id}/   - retrieve a single category
        PUT    /api/categories/{id}/   - update a category
        PATCH  /api/categories/{id}/   - partial update
        DELETE /api/categories/{id}/   - delete a category
    """

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name"]
    ordering_fields = ["name", "created_at"]


class ProductViewSet(viewsets.ModelViewSet):
    """
    Full CRUD for products, with search, filtering, ordering and pagination.

        GET /api/products/?search=phone
        GET /api/products/?category=1
        GET /api/products/?price=199.99
        GET /api/products/?price_min=50&price_max=500
        GET /api/products/?ordering=price       (ascending)
        GET /api/products/?ordering=-price      (descending)
        GET /api/products/?page=2
    """

    queryset = Product.objects.select_related("category").all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ["name", "description"]
    ordering_fields = ["price", "created_date", "name", "stock"]
    ordering = ["-created_date"]


class OrderViewSet(viewsets.ModelViewSet):
    """
    A logged-in user can create orders and view only their own orders.

        GET    /api/orders/        - list the current user's orders
        POST   /api/orders/        - create a new order
        GET    /api/orders/{id}/   - view a single order (only if it's yours)
    """

    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["order_date", "total_price"]
    ordering = ["-order_date"]

    def get_queryset(self):
        # Users may only ever see their own orders.
        return Order.objects.select_related("product", "user").filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        if serializer.instance.user != self.request.user:
            raise PermissionDenied("You cannot modify another user's order.")
        serializer.save()

    def perform_destroy(self, instance):
        if instance.user != self.request.user:
            raise PermissionDenied("You cannot delete another user's order.")
        instance.delete()
