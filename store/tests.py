from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token

from .models import Category, Order, Product


class CategoryAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="tester", password="pass12345")
        self.token = Token.objects.create(user=self.user)
        self.auth_header = {"HTTP_AUTHORIZATION": f"Token {self.token.key}"}

    def test_anyone_can_list_categories(self):
        Category.objects.create(name="Electronics")
        response = self.client.get("/api/categories/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_category_requires_authentication(self):
        response = self.client.post("/api/categories/", {"name": "Books"})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_user_can_create_category(self):
        response = self.client.post(
            "/api/categories/", {"name": "Books"}, **self.auth_header
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Category.objects.count(), 1)


class ProductAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="tester", password="pass12345")
        self.token = Token.objects.create(user=self.user)
        self.auth_header = {"HTTP_AUTHORIZATION": f"Token {self.token.key}"}
        self.category = Category.objects.create(name="Electronics")
        self.phone = Product.objects.create(
            name="Smartphone", description="A phone", price=299.99, stock=10,
            category=self.category,
        )
        self.laptop = Product.objects.create(
            name="Laptop", description="A laptop", price=999.99, stock=5,
            category=self.category,
        )

    def test_search_by_name(self):
        response = self.client.get("/api/products/?search=phone")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        names = [p["name"] for p in response.data["results"]]
        self.assertIn("Smartphone", names)
        self.assertNotIn("Laptop", names)

    def test_filter_by_category(self):
        response = self.client.get(f"/api/products/?category={self.category.id}")
        self.assertEqual(response.data["count"], 2)

    def test_ordering_by_price(self):
        response = self.client.get("/api/products/?ordering=price")
        prices = [float(p["price"]) for p in response.data["results"]]
        self.assertEqual(prices, sorted(prices))

    def test_pagination_default_page_size(self):
        for i in range(15):
            Product.objects.create(
                name=f"Extra {i}", price=10, stock=1, category=self.category
            )
        response = self.client.get("/api/products/")
        self.assertIn("next", response.data)
        self.assertEqual(len(response.data["results"]), 10)

    def test_create_product_requires_authentication(self):
        response = self.client.post(
            "/api/products/",
            {"name": "Tablet", "price": 199, "stock": 3, "category": self.category.id},
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_create_product(self):
        response = self.client.post(
            "/api/products/",
            {"name": "Tablet", "price": 199, "stock": 3, "category": self.category.id},
            **self.auth_header,
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class OrderAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="alice", password="pass12345")
        self.other_user = User.objects.create_user(username="bob", password="pass12345")
        self.token = Token.objects.create(user=self.user)
        self.auth_header = {"HTTP_AUTHORIZATION": f"Token {self.token.key}"}
        self.category = Category.objects.create(name="Electronics")
        self.product = Product.objects.create(
            name="Smartphone", price=100, stock=10, category=self.category
        )

    def test_order_requires_authentication(self):
        response = self.client.post(
            "/api/orders/", {"product": self.product.id, "quantity": 2}
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_order_computes_total_price_and_deducts_stock(self):
        response = self.client.post(
            "/api/orders/",
            {"product": self.product.id, "quantity": 2},
            **self.auth_header,
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["total_price"], "200.00")
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 8)

    def test_order_quantity_cannot_exceed_stock(self):
        response = self.client.post(
            "/api/orders/",
            {"product": self.product.id, "quantity": 999},
            **self.auth_header,
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_only_sees_own_orders(self):
        Order.objects.create(user=self.user, product=self.product, quantity=1)
        Order.objects.create(user=self.other_user, product=self.product, quantity=1)
        response = self.client.get("/api/orders/", **self.auth_header)
        self.assertEqual(response.data["count"], 1)

    def test_login_endpoint_returns_token(self):
        response = self.client.post(
            "/api/login/", {"username": "alice", "password": "pass12345"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("token", response.data)
