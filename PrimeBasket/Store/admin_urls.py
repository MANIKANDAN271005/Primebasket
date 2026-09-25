from django.urls import path

from . import admin_views

urlpatterns = [
    path("login/", admin_views.admin_login, name="admin_login"),
    path("logout/", admin_views.admin_logout, name="admin_logout"),
    path("", admin_views.admin_dashboard, name="admin_dashboard"),
    path("products/", admin_views.admin_products, name="admin_products"),
    path("products/add/", admin_views.admin_product_add, name="admin_product_add"),
    path("products/<slug:product_id>/edit/", admin_views.admin_product_edit, name="admin_product_edit"),
    path("products/<slug:product_id>/delete/", admin_views.admin_product_delete, name="admin_product_delete"),
    path("categories/", admin_views.admin_categories, name="admin_categories"),
    path("categories/<str:name>/edit/", admin_views.admin_category_edit, name="admin_category_edit"),
    path("categories/<str:name>/delete/", admin_views.admin_category_delete, name="admin_category_delete"),
]
