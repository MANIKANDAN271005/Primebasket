"""Views for the separate PrimeBasket Admin Panel (mounted at /pb-admin/).

Deliberately separate from the customer-facing auth in views.py: admins live in their own MongoDB
collection (`admins_collection`), authenticate with their own session key
(`request.session["admin_username"]`), and every view below except the login page itself is guarded
by the `admin_required` decorator. There is no default account -- see
`Store/management/commands/create_admin.py`.
"""

import functools
import json
from datetime import datetime, timezone

from django.contrib import messages
from django.contrib.auth.hashers import check_password
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods
from pymongo.errors import PyMongoError

from PrimeBasket.database.mongodb import admins_collection, orders_collection, users_collection

from . import catalog


def admin_required(view_func):
    @functools.wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get("admin_username"):
            return redirect("admin_login")
        return view_func(request, *args, **kwargs)

    return wrapper


@require_http_methods(["GET", "POST"])
def admin_login(request):
    if request.session.get("admin_username"):
        return redirect("admin_dashboard")

    if request.method == "GET":
        return render(request, "admin_panel/login.html")

    username = (request.POST.get("username") or "").strip()
    password = request.POST.get("password") or ""

    if not username or not password:
        messages.error(request, "Please enter your admin username and password.")
        return render(request, "admin_panel/login.html")

    try:
        admin = admins_collection.find_one({"username": username})
    except PyMongoError:
        messages.error(request, "Unable to reach the database. Please try again.")
        return render(request, "admin_panel/login.html")

    if not admin or not check_password(password, admin.get("password", "")):
        messages.error(request, "Invalid admin username or password.")
        return render(request, "admin_panel/login.html")

    request.session["admin_username"] = admin["username"]
    return redirect("admin_dashboard")


def admin_logout(request):
    request.session.pop("admin_username", None)
    return redirect("admin_login")


@admin_required
def admin_dashboard(request):
    try:
        order_count = orders_collection.count_documents({})
    except PyMongoError:
        order_count = 0
    try:
        user_count = users_collection.count_documents({})
    except PyMongoError:
        user_count = 0

    context = {
        "admin_username": request.session.get("admin_username"),
        "product_count": catalog.count_products(),
        "category_count": catalog.count_categories(),
        "out_of_stock_count": catalog.count_out_of_stock(),
        "order_count": order_count,
        "user_count": user_count,
    }
    return render(request, "admin_panel/dashboard.html", context)


@admin_required
def admin_products(request):
    products = sorted(catalog.get_all_products(), key=lambda p: p.get("name", ""))
    return render(
        request,
        "admin_panel/product_list.html",
        {"admin_username": request.session.get("admin_username"), "products": products},
    )


@admin_required
@require_http_methods(["GET", "POST"])
def admin_product_add(request):
    categories = catalog.get_all_categories()

    if request.method == "GET":
        return render(
            request,
            "admin_panel/product_form.html",
            {"admin_username": request.session.get("admin_username"), "categories": categories, "product": None},
        )

    try:
        product_id = catalog.create_product(
            request.POST,
            image_file=request.FILES.get("image_file"),
            image_url=request.POST.get("image_url"),
        )
    except ValueError as exc:
        messages.error(request, str(exc))
        return render(
            request,
            "admin_panel/product_form.html",
            {
                "admin_username": request.session.get("admin_username"),
                "categories": categories,
                "product": request.POST,
            },
        )

    messages.success(request, f'Product "{request.POST.get("name")}" was added and is now live on the site.')
    return redirect("admin_products")


@admin_required
@require_http_methods(["GET", "POST"])
def admin_product_edit(request, product_id):
    product = catalog.get_product(product_id)
    if not product:
        messages.error(request, "Product not found.")
        return redirect("admin_products")

    categories = catalog.get_all_categories()

    if request.method == "GET":
        # The form expects highlights as newline-separated text, not a list.
        product = dict(product)
        product["highlights"] = "\n".join(product.get("highlights") or [])
        return render(
            request,
            "admin_panel/product_form.html",
            {"admin_username": request.session.get("admin_username"), "categories": categories, "product": product},
        )

    try:
        catalog.update_product(
            product_id,
            request.POST,
            image_file=request.FILES.get("image_file"),
            image_url=request.POST.get("image_url"),
        )
    except ValueError as exc:
        messages.error(request, str(exc))
        form_product = dict(request.POST)
        form_product["id"] = product_id
        return render(
            request,
            "admin_panel/product_form.html",
            {"admin_username": request.session.get("admin_username"), "categories": categories, "product": form_product},
        )

    messages.success(request, f'Product "{request.POST.get("name")}" was updated.')
    return redirect("admin_products")


@admin_required
@require_http_methods(["POST"])
def admin_product_delete(request, product_id):
    catalog.delete_product(product_id)
    messages.success(request, "Product deleted.")
    return redirect("admin_products")


@admin_required
@require_http_methods(["GET", "POST"])
def admin_categories(request):
    if request.method == "POST":
        try:
            catalog.create_category(
                request.POST.get("name"),
                description=request.POST.get("description"),
                image_file=request.FILES.get("image_file"),
                image_url=request.POST.get("image_url"),
            )
            messages.success(request, "Category added.")
        except ValueError as exc:
            messages.error(request, str(exc))
        return redirect("admin_categories")

    return render(
        request,
        "admin_panel/category_list.html",
        {
            "admin_username": request.session.get("admin_username"),
            "categories": catalog.get_category_docs(with_counts=True),
        },
    )


@admin_required
@require_http_methods(["GET", "POST"])
def admin_category_edit(request, name):
    category = catalog.get_category(name)
    if not category:
        messages.error(request, "Category not found.")
        return redirect("admin_categories")

    if request.method == "POST":
        try:
            new_name = catalog.update_category(
                name,
                request.POST.get("name"),
                description=request.POST.get("description"),
                image_file=request.FILES.get("image_file"),
                image_url=request.POST.get("image_url"),
            )
        except ValueError as exc:
            messages.error(request, str(exc))
        else:
            messages.success(request, f'Category "{new_name}" was updated.')
            return redirect("admin_categories")

    return render(
        request,
        "admin_panel/category_form.html",
        {"admin_username": request.session.get("admin_username"), "category": category},
    )


@admin_required
@require_http_methods(["POST"])
def admin_category_delete(request, name):
    catalog.delete_category(name)
    messages.success(request, "Category deleted.")
    return redirect("admin_categories")
