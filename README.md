# Mini E-commerce REST API

A simple e-commerce REST API built with **Django** and **Django REST Framework (DRF)**.
It supports categories, products, token-based authentication, and orders, with
searching, filtering, ordering, and pagination on the product list.

## Features

- **Category API** — full CRUD (Create, Read, Update, Delete)
- **Product API** — full CRUD, each product has name, description, price, stock,
  category (FK), and created date
- **Search** — search products by name (`?search=`)
- **Filter** — filter products by category and price (`?category=`, `?price=`,
  `?price_min=`, `?price_max=`)
- **Ordering** — order products by price, name, stock, or created date
  (`?ordering=`)
- **Pagination** — page-number pagination, 10 items per page by default
- **Token Authentication** — login to receive a token, then use it to access
  protected endpoints
- **Order API** — logged-in users can create orders and view only their own
  orders; total price and stock are computed/validated server-side

### Bonus features included

- Stock validation: an order cannot be placed for more units than are in stock,
  and placing an order deducts stock automatically
- `price_min` / `price_max` range filtering on products
- Django admin registered for all models
- Automated test suite (`store/tests.py`)
- Postman collection (`postman_collection.json`) for manual testing

## Project structure

```
ecommerce_project/
├── manage.py
├── requirements.txt
├── README.md
├── postman_collection.json
├── .gitignore
├── ecommerce_project/       # Project settings & root URL config
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
└── store/                   # Main app: models, serializers, views, urls
    ├── __init__.py
    ├── admin.py
    ├── apps.py
    ├── filters.py
    ├── models.py
    ├── serializers.py
    ├── tests.py
    ├── urls.py
    ├── views.py
    └── migrations/
        └── __init__.py
```

## Setup instructions

### 1. Clone the repository and create a virtual environment

```bash
git clone https://github.com/yeaminhossainfuhad-cloud/Mini-E-commerce-REST-API.git
cd ecommerce_project
python -m venv venv
source venv/bin/activate      # On Windows: venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Apply migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Create a superuser (needed to log in and get a token)

```bash
python manage.py createsuperuser
```

### 5. Run the development server

```bash
python manage.py runserver
```

The API is now available at `http://127.0.0.1:8000/api/`.

### 6. Run the test suite (optional but recommended)

```bash
python manage.py test
```

## Authentication

This project uses DRF's **Token Authentication**.

### Get a token

```
POST /api/login/
Content-Type: application/json

{
  "username": "your_username",
  "password": "your_password"
}
```

Response:

```json
{ "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4" }
```

### Use the token

Add this header to any authenticated request:

```
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4
```

> Reading data (GET requests) on categories and products is open to everyone.
> Creating, updating, or deleting categories/products, and everything on the
> Order API, requires a valid token.

## API Endpoints

### Categories

| Method | Endpoint                  | Description             | Auth required |
|--------|----------------------------|--------------------------|----------------|
| GET    | `/api/categories/`         | List all categories      | No             |
| POST   | `/api/categories/`         | Create a category        | Yes            |
| GET    | `/api/categories/{id}/`    | Retrieve a category      | No             |
| PUT    | `/api/categories/{id}/`    | Update a category (full) | Yes            |
| PATCH  | `/api/categories/{id}/`    | Update a category (part) | Yes            |
| DELETE | `/api/categories/{id}/`    | Delete a category        | Yes            |

Example body:
```json
{ "name": "Electronics", "description": "Gadgets and devices" }
```

### Products

| Method | Endpoint                | Description         | Auth required |
|--------|---------------------------|----------------------|----------------|
| GET    | `/api/products/`           | List products        | No             |
| POST   | `/api/products/`           | Create a product      | Yes            |
| GET    | `/api/products/{id}/`      | Retrieve a product    | No             |
| PUT    | `/api/products/{id}/`      | Update a product (full) | Yes          |
| PATCH  | `/api/products/{id}/`      | Update a product (part) | Yes          |
| DELETE | `/api/products/{id}/`      | Delete a product      | Yes            |

Example body:
```json
{
  "name": "Smartphone",
  "description": "A great phone",
  "price": "299.99",
  "stock": 25,
  "category": 1
}
```

#### Search, filter, order, paginate

```
GET /api/products/?search=phone
GET /api/products/?category=1
GET /api/products/?price=299.99
GET /api/products/?price_min=50&price_max=500
GET /api/products/?ordering=price       (ascending)
GET /api/products/?ordering=-price      (descending)
GET /api/products/?page=2
```

These can be combined, e.g.:
```
GET /api/products/?category=1&search=phone&ordering=-price&page=1
```

### Orders

| Method | Endpoint            | Description                          | Auth required |
|--------|-----------------------|----------------------------------------|----------------|
| GET    | `/api/orders/`         | List the current user's orders         | Yes            |
| POST   | `/api/orders/`         | Create a new order                     | Yes            |
| GET    | `/api/orders/{id}/`    | Retrieve a single order (only your own) | Yes           |

Example body (only `product` and `quantity` are supplied by the client):
```json
{ "product": 1, "quantity": 2 }
```

Example response:
```json
{
  "id": 1,
  "user": "alice",
  "product": 1,
  "product_name": "Smartphone",
  "quantity": 2,
  "total_price": "599.98",
  "order_date": "2026-09-26T10:00:00Z"
}
```

`total_price` is always computed on the server (`product.price * quantity`) and
can't be spoofed by the client. Placing an order also validates that enough
stock is available and deducts the ordered quantity from stock.

Users can only ever see, update, or delete their **own** orders — the
`user` field is set automatically from the authenticated request and is
never taken from client input.

## Testing with Postman

A ready-made Postman collection is included: `postman_collection.json`.

1. Open Postman → **Import** → select `postman_collection.json`.
2. Run "Auth - Login (get token)" with valid credentials to get a token.
3. Set the collection variable `token` to the value returned.
4. Run any of the other requests — they'll automatically use
   `Authorization: Token {{token}}`.

## Project Screenshots

### Categories
![Categories](screenshot/categories.png)

### Products
![Products](screenshot/products.png)

### Orders
![Orders](screenshot/orders.png)

### Administration
![Admin](screenshot/admin.png)

## Tech stack

- Python 3
- Django
- Django REST Framework
- django-filter
- SQLite (default; swap `DATABASES` in `settings.py` for Postgres/MySQL in production)

## Author

**Md Yeamin Hossain Fuhad**

- Diploma in Engineering in Computer Science & Technology
- B.Sc. in Computer Science & Engineering 
- Interested in **SQA, Python/Django Development, and IT Support**

