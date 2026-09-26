"""
URL configuration for ecommerce_project.
"""

from django.contrib import admin
from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("store.urls")),
    # Built-in DRF endpoint that returns a token given username/password
    path("api/login/", obtain_auth_token, name="api-login"),
]
