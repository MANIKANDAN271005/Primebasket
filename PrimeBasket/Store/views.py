import json
import uuid
from datetime import datetime, timezone

from django.contrib.auth.hashers import check_password, make_password
from django.http import Http404, JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods
from pymongo.errors import PyMongoError

from PrimeBasket.database.mongodb import (
    cart_collection,
    messages_collection,
    newsletter_collection,
    orders_collection,
    reviews_collection,
    users_collection,
    wishlist_collection,
)

from . import catalog
from .product_data import COUPONS

DELIVERY_FEE = 30
FREE_DELIVERY_THRESHOLD = 1000
TAX_RATE = 0.05
ADDRESS_FIELDS = ["full_name", "phone", "line1", "city", "state", "postal_code"]
ORDER_STATUS_STEPS = ["Placed", "Processing", "Out for Delivery", "Delivered"]
CANCELLABLE_STATUSES = ("Placed", "Processing")


def home(request):
    return render(
        request,
        "index.html",
        {
            "template_name": "home",
            "products": catalog.get_all_products(),
            "categories": catalog.get_all_categories(),
            "category_cards": catalog.get_category_docs(),
        },
    )


def product_detail(request, product_id):
    product = catalog.get_product(product_id)
    if not product:
        raise Http404("Product not found")

    try:
        product_reviews = list(
            reviews_collection.find({"product_id": product_id}, {"_id": 0}).sort("created_at", -1)
        )
    except PyMongoError:
        product_reviews = []

    return render(
        request,
        "product_detail.html",
        {
            "template_name": "product_detail",
            "product": product,
            "related_products": catalog.get_related_products(product_id),
            "product_reviews": product_reviews,
            "can_review": bool(request.session.get("user_email")),
        },
    )


@require_http_methods(["POST"])
def add_review(request, product_id):
    email = request.session.get("user_email")
    if not email:
        return JsonResponse({"success": False, "error": "Please log in first."}, status=401)

    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"success": False, "error": "Invalid request data."}, status=400)

    comment = (data.get("comment") or "").strip()

    try:
        rating = int(data.get("rating"))
    except (TypeError, ValueError):
        rating = 0

    if not catalog.get_product(product_id):
        return JsonResponse({"success": False, "error": "Product not found."}, status=404)
    if rating < 1 or rating > 5:
        return JsonResponse({"success": False, "error": "Please choose a rating between 1 and 5 stars."}, status=400)
    if len(comment) < 5:
        return JsonResponse({"success": False, "error": "Please share a few words about the product."}, status=400)

    try:
        user = users_collection.find_one({"email": email})
    except PyMongoError:
        user = None

    reviewer_name = (user or {}).get("fullname") or request.session.get("user_fullname") or "PrimeBasket Customer"

    try:
        reviews_collection.insert_one(
            {
                "product_id": product_id,
                "user_email": email,
                "reviewer_name": reviewer_name,
                "rating": rating,
                "comment": comment,
                "created_at": datetime.now(timezone.utc),
            }
        )
    except PyMongoError:
        return JsonResponse({"success": False, "error": "Unable to submit your review. Please try again."}, status=503)

    return JsonResponse({"success": True})


def contact(request):
    if request.method == "POST":
        return _handle_contact(request)

    return render(request, "contact.html", {"template_name": "contact"})


def _handle_contact(request):
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"success": False, "error": "Invalid request data."}, status=400)

    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    subject = (data.get("subject") or "").strip()
    message = (data.get("message") or "").strip()

    if len(name) < 2:
        return JsonResponse({"success": False, "error": "Please enter your name."}, status=400)
    if "@" not in email or "." not in email.split("@")[-1]:
        return JsonResponse({"success": False, "error": "Please enter a valid email address."}, status=400)
    if len(message) < 10:
        return JsonResponse({"success": False, "error": "Please enter a message of at least 10 characters."}, status=400)

    try:
        messages_collection.insert_one(
            {
                "name": name,
                "email": email,
                "subject": subject or "General enquiry",
                "message": message,
                "submitted_at": datetime.now(timezone.utc),
            }
        )
    except PyMongoError:
        return JsonResponse(
            {"success": False, "error": "Unable to send your message right now. Please try again."}, status=503
        )

    return JsonResponse({"success": True})


def faq(request):
    return render(request, "faq.html", {"template_name": "faq"})


def privacy(request):
    return render(request, "privacy.html", {"template_name": "privacy"})


def terms(request):
    return render(request, "terms.html", {"template_name": "terms"})


@require_http_methods(["POST"])
def newsletter_subscribe(request):
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"success": False, "error": "Invalid request data."}, status=400)

    email = (data.get("email") or "").strip().lower()
    if "@" not in email or "." not in email.split("@")[-1]:
        return JsonResponse({"success": False, "error": "Please enter a valid email address."}, status=400)

    try:
        if not newsletter_collection.find_one({"email": email}):
            newsletter_collection.insert_one({"email": email, "subscribed_at": datetime.now(timezone.utc)})
    except PyMongoError:
        return JsonResponse(
            {"success": False, "error": "Unable to subscribe right now. Please try again."}, status=503
        )

    return JsonResponse({"success": True})


def wishlist(request):
    return render(request, "wishlist.html", {"template_name": "wishlist"})


def wishlist_items(request):
    email = request.session.get("user_email")
    if not email:
        return JsonResponse({"success": False, "error": "Please log in first."}, status=401)

    try:
        # READ: get every wishlist document belonging to this user.
        items = list(wishlist_collection.find({"user_email": email}, {"_id": 0}))
    except PyMongoError:
        return JsonResponse({"success": False, "error": "Unable to load wishlist."}, status=503)

    return JsonResponse({"success": True, "items": items})


@require_http_methods(["POST"])
def wishlist_add(request):
    email = request.session.get("user_email")
    if not email:
        return JsonResponse({"success": False, "error": "Please log in first."}, status=401)

    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"success": False, "error": "Invalid request data."}, status=400)

    product_id = (data.get("product_id") or "").strip()
    if not product_id:
        return JsonResponse({"success": False, "error": "Missing product."}, status=400)

    try:
        # READ first: only insert if this user hasn't already saved this product.
        already_saved = wishlist_collection.find_one({"user_email": email, "product_id": product_id})
        if not already_saved:
            wishlist_collection.insert_one(
                {
                    "user_email": email,
                    "product_id": product_id,
                    "name": (data.get("name") or "").strip(),
                    "image": (data.get("image") or "").strip(),
                    "price": data.get("price") or 0,
                    "unit": (data.get("unit") or "").strip(),
                    "added_at": datetime.now(timezone.utc),
                }
            )
    except PyMongoError:
        return JsonResponse({"success": False, "error": "Unable to save to wishlist."}, status=503)

    return JsonResponse({"success": True})


@require_http_methods(["POST"])
def wishlist_remove(request):
    email = request.session.get("user_email")
    if not email:
        return JsonResponse({"success": False, "error": "Please log in first."}, status=401)

    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"success": False, "error": "Invalid request data."}, status=400)

    product_id = (data.get("product_id") or "").strip()
    if not product_id:
        return JsonResponse({"success": False, "error": "Missing product."}, status=400)

    try:
        wishlist_collection.delete_one({"user_email": email, "product_id": product_id})
    except PyMongoError:
        return JsonResponse({"success": False, "error": "Unable to remove from wishlist."}, status=503)

    return JsonResponse({"success": True})


def cart(request):
    return render(request, "cart.html", {"template_name": "cart"})


def _cart_items_for(email):
    try:
        return list(cart_collection.find({"user_email": email}, {"_id": 0}))
    except PyMongoError:
        return None


def cart_items(request):
    email = request.session.get("user_email")
    if not email:
        return JsonResponse({"success": False, "error": "Please log in first."}, status=401)

    items = _cart_items_for(email)
    if items is None:
        return JsonResponse({"success": False, "error": "Unable to load cart."}, status=503)

    return JsonResponse({"success": True, "items": items})


@require_http_methods(["POST"])
def cart_add(request):
    email = request.session.get("user_email")
    if not email:
        return JsonResponse({"success": False, "error": "Please log in first."}, status=401)

    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"success": False, "error": "Invalid request data."}, status=400)

    product_id = (data.get("product_id") or "").strip()
    if not product_id:
        return JsonResponse({"success": False, "error": "Missing product."}, status=400)

    try:
        quantity = int(data.get("quantity") or 1)
    except (TypeError, ValueError):
        quantity = 1
    quantity = max(1, quantity)

    try:
        # READ first: does this user already have this product in their cart?
        existing = cart_collection.find_one({"user_email": email, "product_id": product_id})
        if existing:
            # UPDATE: already in the cart, so bump the quantity on that line.
            new_quantity = existing.get("quantity", 1) + quantity
            cart_collection.update_one(
                {"user_email": email, "product_id": product_id},
                {"$set": {"quantity": new_quantity}},
            )
        else:
            new_quantity = quantity
            # CREATE: first time this product is added, insert a new cart line.
            cart_collection.insert_one(
                {
                    "user_email": email,
                    "product_id": product_id,
                    "name": (data.get("name") or "").strip(),
                    "image": (data.get("image") or "").strip(),
                    "price": data.get("price") or 0,
                    "unit": (data.get("unit") or "").strip(),
                    "quantity": new_quantity,
                    "added_at": datetime.now(timezone.utc),
                }
            )
    except PyMongoError:
        return JsonResponse({"success": False, "error": "Unable to add to cart."}, status=503)

    return JsonResponse({"success": True, "quantity": new_quantity})


@require_http_methods(["POST"])
def cart_update(request):
    email = request.session.get("user_email")
    if not email:
        return JsonResponse({"success": False, "error": "Please log in first."}, status=401)

    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"success": False, "error": "Invalid request data."}, status=400)

    product_id = (data.get("product_id") or "").strip()
    if not product_id:
        return JsonResponse({"success": False, "error": "Missing product."}, status=400)

    try:
        quantity = int(data.get("quantity"))
    except (TypeError, ValueError):
        return JsonResponse({"success": False, "error": "Invalid quantity."}, status=400)
    quantity = max(1, quantity)

    try:
        # UPDATE: set the quantity on this user's existing cart line.
        result = cart_collection.update_one(
            {"user_email": email, "product_id": product_id},
            {"$set": {"quantity": quantity}},
        )
    except PyMongoError:
        return JsonResponse({"success": False, "error": "Unable to update cart."}, status=503)

    if result.matched_count == 0:
        return JsonResponse({"success": False, "error": "Item not found in cart."}, status=404)

    return JsonResponse({"success": True, "quantity": quantity})


@require_http_methods(["POST"])
def cart_remove(request):
    email = request.session.get("user_email")
    if not email:
        return JsonResponse({"success": False, "error": "Please log in first."}, status=401)

    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"success": False, "error": "Invalid request data."}, status=400)

    product_id = (data.get("product_id") or "").strip()
    if not product_id:
        return JsonResponse({"success": False, "error": "Missing product."}, status=400)

    try:
        # DELETE: remove this user's cart line for the product.
        cart_collection.delete_one({"user_email": email, "product_id": product_id})
    except PyMongoError:
        return JsonResponse({"success": False, "error": "Unable to remove from cart."}, status=503)

    return JsonResponse({"success": True})


# ---------------------------------------------------------------------------
# Checkout / Orders
# ---------------------------------------------------------------------------


def _calculate_totals(items, coupon_code):
    """Always recompute money server-side from the live cart -- the client
    never gets to dictate a subtotal, discount, or total."""
    subtotal = sum(float(item.get("price") or 0) * int(item.get("quantity") or 1) for item in items)

    discount = 0.0
    coupon_error = None
    applied_code = None

    if coupon_code:
        coupon = COUPONS.get(coupon_code.strip().upper())
        if not coupon:
            coupon_error = "Invalid or expired coupon code."
        else:
            applied_code = coupon_code.strip().upper()
            if coupon["type"] == "percent":
                discount = subtotal * (coupon["value"] / 100)
            else:
                discount = coupon["value"]
            discount = min(discount, subtotal)

    discounted_subtotal = subtotal - discount
    delivery_charge = 0.0 if (subtotal == 0 or discounted_subtotal >= FREE_DELIVERY_THRESHOLD) else DELIVERY_FEE
    tax = round(discounted_subtotal * TAX_RATE, 2)
    total = round(discounted_subtotal + delivery_charge + tax, 2)

    return {
        "subtotal": round(subtotal, 2),
        "discount": round(discount, 2),
        "coupon_code": applied_code,
        "coupon_error": coupon_error,
        "delivery_charge": delivery_charge,
        "tax": tax,
        "total": total,
    }


@require_http_methods(["GET"])
def checkout(request):
    email = request.session.get("user_email")
    if not email:
        return redirect("login")

    try:
        user = users_collection.find_one({"email": email}, {"password": 0})
    except PyMongoError:
        user = None

    if not user:
        request.session.flush()
        return redirect("login")

    return render(
        request,
        "checkout.html",
        {"template_name": "checkout", "addresses": user.get("addresses", [])},
    )


@require_http_methods(["POST"])
def checkout_summary(request):
    email = request.session.get("user_email")
    if not email:
        return JsonResponse({"success": False, "error": "Please log in first."}, status=401)

    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"success": False, "error": "Invalid request data."}, status=400)

    coupon_code = (data.get("coupon_code") or "").strip()

    items = _cart_items_for(email)
    if items is None:
        return JsonResponse({"success": False, "error": "Unable to load cart."}, status=503)
    if not items:
        return JsonResponse({"success": False, "error": "Your cart is empty."}, status=400)

    totals = _calculate_totals(items, coupon_code)
    if coupon_code and totals["coupon_error"]:
        return JsonResponse({"success": False, "error": totals["coupon_error"]}, status=400)

    return JsonResponse({"success": True, **totals})


@require_http_methods(["POST"])
def place_order(request):
    email = request.session.get("user_email")
    if not email:
        return JsonResponse({"success": False, "error": "Please log in first."}, status=401)

    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"success": False, "error": "Invalid request data."}, status=400)

    address = data.get("address") or {}
    if not all((address.get(field) or "").strip() for field in ADDRESS_FIELDS):
        return JsonResponse({"success": False, "error": "Please provide a complete delivery address."}, status=400)

    payment_method = data.get("payment_method") or "cod"
    if payment_method not in ("cod", "card"):
        payment_method = "cod"

    coupon_code = (data.get("coupon_code") or "").strip()

    items = _cart_items_for(email)
    if items is None:
        return JsonResponse({"success": False, "error": "Unable to load cart."}, status=503)
    if not items:
        return JsonResponse({"success": False, "error": "Your cart is empty."}, status=400)

    totals = _calculate_totals(items, coupon_code)
    if coupon_code and totals["coupon_error"]:
        return JsonResponse({"success": False, "error": totals["coupon_error"]}, status=400)

    order_id = "PB" + uuid.uuid4().hex[:8].upper()
    now = datetime.now(timezone.utc)

    order_items = [
        {
            "product_id": item.get("product_id"),
            "name": item.get("name"),
            "image": item.get("image"),
            "price": item.get("price"),
            "unit": item.get("unit"),
            "quantity": item.get("quantity"),
        }
        for item in items
    ]

    try:
        orders_collection.insert_one(
            {
                "order_id": order_id,
                "user_email": email,
                "items": order_items,
                "subtotal": totals["subtotal"],
                "discount": totals["discount"],
                "coupon_code": totals["coupon_code"],
                "delivery_charge": totals["delivery_charge"],
                "tax": totals["tax"],
                "total": totals["total"],
                "address": {field: (address.get(field) or "").strip() for field in ADDRESS_FIELDS},
                "payment_method": payment_method,
                "status": "Placed",
                "placed_at": now,
                "updated_at": now,
            }
        )
        cart_collection.delete_many({"user_email": email})
    except PyMongoError:
        return JsonResponse({"success": False, "error": "Unable to place your order. Please try again."}, status=503)

    return JsonResponse({"success": True, "order_id": order_id, "redirect": f"/orders/{order_id}/confirmation/"})


@require_http_methods(["GET"])
def order_confirmation(request, order_id):
    email = request.session.get("user_email")
    if not email:
        return redirect("login")

    try:
        order = orders_collection.find_one({"order_id": order_id, "user_email": email}, {"_id": 0})
    except PyMongoError:
        order = None

    if not order:
        raise Http404("Order not found")

    return render(request, "order_confirmation.html", {"template_name": "order_confirmation", "order": order})


@require_http_methods(["GET"])
def orders(request):
    email = request.session.get("user_email")
    if not email:
        return redirect("login")

    try:
        order_list = list(orders_collection.find({"user_email": email}, {"_id": 0}).sort("placed_at", -1))
    except PyMongoError:
        order_list = []

    return render(request, "order_history.html", {"template_name": "orders", "orders": order_list})


@require_http_methods(["GET"])
def order_detail(request, order_id):
    email = request.session.get("user_email")
    if not email:
        return redirect("login")

    try:
        order = orders_collection.find_one({"order_id": order_id, "user_email": email}, {"_id": 0})
    except PyMongoError:
        order = None

    if not order:
        raise Http404("Order not found")

    current_index = (
        ORDER_STATUS_STEPS.index(order["status"]) if order["status"] in ORDER_STATUS_STEPS else -1
    )

    return render(
        request,
        "order_detail.html",
        {
            "template_name": "order_detail",
            "order": order,
            "status_steps": ORDER_STATUS_STEPS,
            "current_index": current_index,
            "can_cancel": order.get("status") in CANCELLABLE_STATUSES,
        },
    )


@require_http_methods(["POST"])
def cancel_order(request, order_id):
    email = request.session.get("user_email")
    if not email:
        return JsonResponse({"success": False, "error": "Please log in first."}, status=401)

    try:
        order = orders_collection.find_one({"order_id": order_id, "user_email": email})
    except PyMongoError:
        return JsonResponse({"success": False, "error": "Unable to cancel this order."}, status=503)

    if not order:
        return JsonResponse({"success": False, "error": "Order not found."}, status=404)

    if order.get("status") not in CANCELLABLE_STATUSES:
        return JsonResponse({"success": False, "error": "This order can no longer be cancelled."}, status=400)

    try:
        orders_collection.update_one(
            {"order_id": order_id, "user_email": email},
            {"$set": {"status": "Cancelled", "updated_at": datetime.now(timezone.utc)}},
        )
    except PyMongoError:
        return JsonResponse({"success": False, "error": "Unable to cancel this order."}, status=503)

    return JsonResponse({"success": True})


# ---------------------------------------------------------------------------
# Auth / account
# ---------------------------------------------------------------------------


@require_http_methods(["GET", "POST"])
def register(request):
    if request.method == "POST":
        return _handle_register(request)

    return render(request, "register.html", {"template_name": "register"})


def _handle_register(request):
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"success": False, "error": "Invalid request data."}, status=400)

    fullname = (data.get("fullname") or "").strip()
    email = (data.get("email") or "").strip().lower()
    phone = (data.get("phone") or "").strip()
    password = data.get("password") or ""

    # --- basic validation ---
    if len(fullname) < 3:
        return JsonResponse({"success": False, "error": "Please enter your full name."}, status=400)
    if "@" not in email or "." not in email.split("@")[-1]:
        return JsonResponse({"success": False, "error": "Please enter a valid email address."}, status=400)
    if not phone or not phone.replace("+", "").replace(" ", "").isdigit():
        return JsonResponse({"success": False, "error": "Please enter a valid phone number."}, status=400)
    if len(password) < 6:
        return JsonResponse({"success": False, "error": "Password must be at least 6 characters."}, status=400)

    try:
        if users_collection.find_one({"email": email}):
            return JsonResponse(
                {"success": False, "error": "An account with this email already exists."}, status=409
            )

        # Django's built-in password hasher (PBKDF2 by default) -- never store plaintext.
        hashed_password = make_password(password)

        users_collection.insert_one(
            {
                "fullname": fullname,
                "email": email,
                "phone": phone,
                "password": hashed_password,
                "addresses": [],
                "created_at": datetime.now(timezone.utc),
            }
        )
    except PyMongoError:
        return JsonResponse(
            {"success": False, "error": "Registration is temporarily unavailable. Please try again."}, status=503
        )

    return JsonResponse({"success": True, "redirect": "/login/"})


@require_http_methods(["GET", "POST"])
def login_view(request):
    if request.method == "POST":
        return _handle_login(request)

    return render(request, "login.html", {"template_name": "login"})


def _handle_login(request):
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"success": False, "error": "Invalid request data."}, status=400)

    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not email or not password:
        return JsonResponse(
            {"success": False, "error": "Please provide a valid email and password."}, status=400
        )

    try:
        user = users_collection.find_one({"email": email})
    except PyMongoError:
        return JsonResponse(
            {"success": False, "error": "Login is temporarily unavailable. Please try again."}, status=503
        )

    if not user or not check_password(password, user.get("password", "")):
        return JsonResponse({"success": False, "error": "Invalid email or password."}, status=401)

    request.session["user_email"] = user["email"]
    request.session["user_fullname"] = user.get("fullname", "")

    return JsonResponse({"success": True, "redirect": "/"})


def profile(request):
    email = request.session.get("user_email")
    if not email:
        return redirect("login")

    try:
        user = users_collection.find_one({"email": email}, {"password": 0})
    except PyMongoError:
        user = None

    if not user:
        request.session.flush()
        return redirect("login")

    return render(request, "profile.html", {"template_name": "profile", "profile_user": user})


@require_http_methods(["POST"])
def edit_profile(request):
    email = request.session.get("user_email")
    if not email:
        return JsonResponse({"success": False, "error": "Please log in first."}, status=401)

    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"success": False, "error": "Invalid request data."}, status=400)

    fullname = (data.get("fullname") or "").strip()
    phone = (data.get("phone") or "").strip()

    if len(fullname) < 3:
        return JsonResponse({"success": False, "error": "Please enter your full name."}, status=400)
    if not phone or not phone.replace("+", "").replace(" ", "").isdigit():
        return JsonResponse({"success": False, "error": "Please enter a valid phone number."}, status=400)

    try:
        users_collection.update_one(
            {"email": email},
            {"$set": {"fullname": fullname, "phone": phone}},
        )
    except PyMongoError:
        return JsonResponse(
            {"success": False, "error": "Update is temporarily unavailable. Please try again."}, status=503
        )

    request.session["user_fullname"] = fullname
    return JsonResponse({"success": True, "fullname": fullname, "phone": phone})


@require_http_methods(["POST"])
def change_password(request):
    email = request.session.get("user_email")
    if not email:
        return JsonResponse({"success": False, "error": "Please log in first."}, status=401)

    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"success": False, "error": "Invalid request data."}, status=400)

    current_password = data.get("current_password") or ""
    new_password = data.get("new_password") or ""

    if len(new_password) < 6:
        return JsonResponse({"success": False, "error": "New password must be at least 6 characters."}, status=400)

    try:
        user = users_collection.find_one({"email": email})
    except PyMongoError:
        user = None

    if not user or not check_password(current_password, user.get("password", "")):
        return JsonResponse({"success": False, "error": "Current password is incorrect."}, status=401)

    try:
        users_collection.update_one({"email": email}, {"$set": {"password": make_password(new_password)}})
    except PyMongoError:
        return JsonResponse(
            {"success": False, "error": "Unable to update password. Please try again."}, status=503
        )

    return JsonResponse({"success": True})


@require_http_methods(["POST"])
def add_address(request):
    email = request.session.get("user_email")
    if not email:
        return JsonResponse({"success": False, "error": "Please log in first."}, status=401)

    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"success": False, "error": "Invalid request data."}, status=400)

    address = {field: (data.get(field) or "").strip() for field in ADDRESS_FIELDS}
    if not all(address.values()):
        return JsonResponse({"success": False, "error": "Please fill in every address field."}, status=400)

    address["id"] = uuid.uuid4().hex[:10]

    try:
        users_collection.update_one({"email": email}, {"$push": {"addresses": address}})
    except PyMongoError:
        return JsonResponse({"success": False, "error": "Unable to save this address."}, status=503)

    return JsonResponse({"success": True, "address": address})


@require_http_methods(["POST"])
def delete_address(request, address_id):
    email = request.session.get("user_email")
    if not email:
        return JsonResponse({"success": False, "error": "Please log in first."}, status=401)

    try:
        users_collection.update_one({"email": email}, {"$pull": {"addresses": {"id": address_id}}})
    except PyMongoError:
        return JsonResponse({"success": False, "error": "Unable to delete this address."}, status=503)

    return JsonResponse({"success": True})


@require_http_methods(["POST"])
def delete_account(request):
    email = request.session.get("user_email")
    if not email:
        return JsonResponse({"success": False, "error": "Please log in first."}, status=401)

    try:
        users_collection.delete_one({"email": email})
    except PyMongoError:
        return JsonResponse(
            {"success": False, "error": "Delete is temporarily unavailable. Please try again."}, status=503
        )

    request.session.flush()
    return JsonResponse({"success": True, "redirect": "/"})


def logout_view(request):
    request.session.flush()
    return redirect("home")
