from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),

    path("products/<slug:product_id>/", views.product_detail, name="product_detail"),
    path("products/<slug:product_id>/reviews/add/", views.add_review, name="add_review"),

    path("contact/", views.contact, name="contact"),
    path("faq/", views.faq, name="faq"),
    path("privacy/", views.privacy, name="privacy"),
    path("terms/", views.terms, name="terms"),
    path("newsletter/subscribe/", views.newsletter_subscribe, name="newsletter_subscribe"),

    path("wishlist/", views.wishlist, name="wishlist"),
    path("wishlist/items/", views.wishlist_items, name="wishlist_items"),
    path("wishlist/add/", views.wishlist_add, name="wishlist_add"),
    path("wishlist/remove/", views.wishlist_remove, name="wishlist_remove"),

    path("cart/", views.cart, name="cart"),
    path("cart/items/", views.cart_items, name="cart_items"),
    path("cart/add/", views.cart_add, name="cart_add"),
    path("cart/update/", views.cart_update, name="cart_update"),
    path("cart/remove/", views.cart_remove, name="cart_remove"),

    path("checkout/", views.checkout, name="checkout"),
    path("checkout/summary/", views.checkout_summary, name="checkout_summary"),
    path("checkout/place-order/", views.place_order, name="place_order"),

    path("orders/", views.orders, name="orders"),
    path("orders/<str:order_id>/", views.order_detail, name="order_detail"),
    path("orders/<str:order_id>/confirmation/", views.order_confirmation, name="order_confirmation"),
    path("orders/<str:order_id>/cancel/", views.cancel_order, name="cancel_order"),

    path("login/", views.login_view, name="login"),
    path("register/", views.register, name="register"),
    path("profile/", views.profile, name="profile"),
    path("profile/edit/", views.edit_profile, name="edit_profile"),
    path("profile/change-password/", views.change_password, name="change_password"),
    path("profile/addresses/add/", views.add_address, name="add_address"),
    path("profile/addresses/<str:address_id>/delete/", views.delete_address, name="delete_address"),
    path("profile/delete/", views.delete_account, name="delete_account"),
    path("logout/", views.logout_view, name="logout"),
]
