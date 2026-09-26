import django_filters

from .models import Product


class ProductFilter(django_filters.FilterSet):
    """
    Enables:
        /products/?category=1
        /products/?price=99.99
        /products/?price_min=10&price_max=100
    """

    price_min = django_filters.NumberFilter(field_name="price", lookup_expr="gte")
    price_max = django_filters.NumberFilter(field_name="price", lookup_expr="lte")

    class Meta:
        model = Product
        fields = ["category", "price"]
