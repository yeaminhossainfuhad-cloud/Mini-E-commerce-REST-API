from rest_framework import serializers

from .models import Category, Order, Product


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "description", "created_at"]


class ProductSerializer(serializers.ModelSerializer):
    # Read-friendly extra field showing the category name alongside its id.
    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "description",
            "price",
            "stock",
            "category",
            "category_name",
            "created_date",
        ]
        read_only_fields = ["created_date"]

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than zero.")
        return value

    def validate_stock(self, value):
        if value < 0:
            raise serializers.ValidationError("Stock cannot be negative.")
        return value


class OrderSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source="user.username")
    total_price = serializers.ReadOnlyField()
    product_name = serializers.ReadOnlyField(source="product.name")

    class Meta:
        model = Order
        fields = [
            "id",
            "user",
            "product",
            "product_name",
            "quantity",
            "total_price",
            "order_date",
        ]
        read_only_fields = ["total_price", "order_date", "user"]

    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError("Quantity must be at least 1.")
        return value

    def validate(self, attrs):
        # Optional bonus feature: basic stock validation.
        product = attrs.get("product") or getattr(self.instance, "product", None)
        quantity = attrs.get("quantity") or getattr(self.instance, "quantity", None)
        if product and quantity and quantity > product.stock:
            raise serializers.ValidationError(
                {"quantity": f"Only {product.stock} unit(s) of '{product.name}' left in stock."}
            )
        return attrs

    def create(self, validated_data):
        # Deduct stock when an order is placed.
        product = validated_data["product"]
        quantity = validated_data["quantity"]
        product.stock -= quantity
        product.save(update_fields=["stock"])
        return super().create(validated_data)
