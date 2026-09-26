from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class Category(models.Model):
    """A product category, e.g. Electronics, Clothing, Books."""

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Product(models.Model):
    """A product that belongs to a Category and can be ordered."""

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    stock = models.PositiveIntegerField(default=0)
    category = models.ForeignKey(
        Category, related_name="products", on_delete=models.CASCADE
    )
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_date"]

    def __str__(self):
        return self.name


class Order(models.Model):
    """An order placed by a logged-in user for a single product."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="orders", on_delete=models.CASCADE
    )
    product = models.ForeignKey(
        Product, related_name="orders", on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=12, decimal_places=2, editable=False)
    order_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-order_date"]

    def save(self, *args, **kwargs):
        # Always (re)compute total_price server-side so it can never be spoofed.
        self.total_price = self.product.price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order #{self.pk} - {self.user} - {self.product}"
