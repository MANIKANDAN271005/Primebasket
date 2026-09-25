"""Product/category catalog, backed by MongoDB so the admin panel can manage it live.

Read functions lazily seed `products_collection` / `categories_collection` from
`product_data.DEFAULT_PRODUCTS` / `DEFAULT_CATEGORIES` the first time they run against an empty
database, then MongoDB is the only source of truth from that point on -- an admin-added product shows
up on the customer site immediately because both sides read the same collection.
"""

import uuid

from django.core.files.storage import default_storage
from django.templatetags.static import static as static_url
from django.utils.text import slugify
from pymongo.errors import PyMongoError

from PrimeBasket.database.mongodb import categories_collection, products_collection

from .product_data import DEFAULT_CATEGORIES, DEFAULT_PRODUCTS, LEGACY_SEED_IMAGES

ALLOWED_IMAGE_EXTENSIONS = {"jpg", "jpeg", "png", "webp", "gif"}
FALLBACK_IMAGE = "images/products/placeholder.jpg"

_seed_images_upgraded = False


def resolve_image(image):
    """Turn a stored `image` value into something a browser can load directly."""
    if not image:
        return static_url(FALLBACK_IMAGE)
    if image.startswith("http://") or image.startswith("https://") or image.startswith("/"):
        return image
    return static_url(image)


def _with_image_url(product):
    if product is None:
        return None
    product = dict(product)
    product["image_url"] = resolve_image(product.get("image"))
    return product


def seed_if_empty():
    try:
        if products_collection.count_documents({}) == 0 and DEFAULT_PRODUCTS:
            products_collection.insert_many([dict(p) for p in DEFAULT_PRODUCTS])
        if categories_collection.count_documents({}) == 0 and DEFAULT_CATEGORIES:
            categories_collection.insert_many([dict(c) for c in DEFAULT_CATEGORIES])
    except PyMongoError:
        pass
    upgrade_seed_images()


def upgrade_seed_images():
    """Once per process: give databases seeded before the local-photo switch the new photos.

    Only touches seeded products whose image is still one of the old seed values, and seeded
    categories that have no image yet -- anything an admin set is left alone.
    """
    global _seed_images_upgraded
    if _seed_images_upgraded:
        return
    try:
        for product in DEFAULT_PRODUCTS:
            products_collection.update_one(
                {"id": product["id"], "image": {"$in": list(LEGACY_SEED_IMAGES)}},
                {"$set": {"image": product["image"]}},
            )
        for category in DEFAULT_CATEGORIES:
            categories_collection.update_one(
                {"name": category["name"], "image": {"$in": [None, ""]}},
                {"$set": {"image": category["image"], "description": category["description"]}},
            )
    except PyMongoError:
        return
    _seed_images_upgraded = True


def get_all_products(category=None):
    seed_if_empty()
    query = {}
    if category and category != "all":
        query["category"] = category
    try:
        docs = list(products_collection.find(query, {"_id": 0}))
    except PyMongoError:
        docs = []
    return [_with_image_url(d) for d in docs]


def get_product(product_id):
    seed_if_empty()
    try:
        doc = products_collection.find_one({"id": product_id}, {"_id": 0})
    except PyMongoError:
        doc = None
    return _with_image_url(doc)


def get_related_products(product_id, limit=4):
    current = get_product(product_id)
    try:
        docs = list(products_collection.find({"id": {"$ne": product_id}}, {"_id": 0}))
    except PyMongoError:
        docs = []

    if current:
        same_category = [d for d in docs if d.get("category") == current.get("category")]
        rest = [d for d in docs if d.get("category") != current.get("category")]
        docs = same_category + rest

    return [_with_image_url(d) for d in docs[:limit]]


def get_all_categories():
    seed_if_empty()
    try:
        docs = list(categories_collection.find({}, {"_id": 0}).sort("name", 1))
    except PyMongoError:
        docs = []
    return [d["name"] for d in docs]


def _category_with_image_url(doc):
    doc = dict(doc)
    doc["image_url"] = resolve_image(doc.get("image"))
    doc.setdefault("description", "")
    return doc


def get_category_docs(with_counts=False):
    """Full category documents (name, description, image_url), sorted by name."""
    seed_if_empty()
    try:
        docs = list(categories_collection.find({}, {"_id": 0}).sort("name", 1))
        if with_counts:
            counts = {
                row["_id"]: row["count"]
                for row in products_collection.aggregate([{"$group": {"_id": "$category", "count": {"$sum": 1}}}])
            }
            for doc in docs:
                doc["product_count"] = counts.get(doc["name"], 0)
    except PyMongoError:
        docs = []
    return [_category_with_image_url(d) for d in docs]


def get_category(name):
    seed_if_empty()
    try:
        doc = categories_collection.find_one({"name": name}, {"_id": 0})
    except PyMongoError:
        doc = None
    return _category_with_image_url(doc) if doc else None


def _category_image(image_file, image_url):
    if image_file:
        return _save_uploaded_image(image_file)
    if image_url and image_url.strip():
        return image_url.strip()
    return None


def create_category(name, description="", image_file=None, image_url=None):
    name = (name or "").strip()
    if not name:
        raise ValueError("Category name is required.")
    if categories_collection.find_one({"name": name}):
        raise ValueError("This category already exists.")
    categories_collection.insert_one(
        {
            "name": name,
            "description": (description or "").strip(),
            "image": _category_image(image_file, image_url) or "",
        }
    )
    return name


def update_category(old_name, name, description="", image_file=None, image_url=None):
    """Edit a category. Renaming it also moves every product in it to the new name."""
    name = (name or "").strip()
    if not name:
        raise ValueError("Category name is required.")
    if not categories_collection.find_one({"name": old_name}):
        raise ValueError("Category not found.")
    if name != old_name and categories_collection.find_one({"name": name}):
        raise ValueError("Another category already has this name.")

    update = {"name": name, "description": (description or "").strip()}
    image = _category_image(image_file, image_url)
    if image:
        update["image"] = image

    categories_collection.update_one({"name": old_name}, {"$set": update})
    if name != old_name:
        products_collection.update_many({"category": old_name}, {"$set": {"category": name}})
    return name


def delete_category(name):
    categories_collection.delete_one({"name": name})


def count_products():
    try:
        return products_collection.count_documents({})
    except PyMongoError:
        return 0


def count_out_of_stock():
    try:
        return products_collection.count_documents({"in_stock": False})
    except PyMongoError:
        return 0


def count_categories():
    try:
        return categories_collection.count_documents({})
    except PyMongoError:
        return 0


def _compute_discount_label(price, old_price):
    if old_price <= price or old_price <= 0:
        return ""
    percent_off = round((old_price - price) / old_price * 100)
    if percent_off <= 0:
        return ""
    return f"{percent_off}% Off"


def _unique_slug(name):
    base = slugify(name) or "product"
    slug = base
    counter = 2
    while products_collection.find_one({"id": slug}):
        slug = f"{base}-{counter}"
        counter += 1
    return slug


def _save_uploaded_image(image_file):
    ext = image_file.name.rsplit(".", 1)[-1].lower() if "." in image_file.name else ""
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        raise ValueError("Please upload a JPG, PNG, WEBP, or GIF image.")

    saved_path = default_storage.save(f"products/{uuid.uuid4().hex}.{ext}", image_file)
    return "/media/" + saved_path


def _build_product_fields(form_data):
    name = (form_data.get("name") or "").strip()
    category = (form_data.get("category") or "").strip()
    unit = (form_data.get("unit") or "EA").strip()
    description = (form_data.get("description") or "").strip()
    short_description = (form_data.get("short_description") or "").strip() or description[:120]
    highlights = [line.strip() for line in (form_data.get("highlights") or "").splitlines() if line.strip()]

    try:
        price = float(form_data.get("price") or 0)
    except (TypeError, ValueError):
        price = 0.0

    old_price_raw = form_data.get("old_price")
    try:
        old_price = float(old_price_raw) if old_price_raw else price
    except (TypeError, ValueError):
        old_price = price

    try:
        stock_qty = max(0, int(form_data.get("stock_qty") or 0))
    except (TypeError, ValueError):
        stock_qty = 0

    if not name:
        raise ValueError("Product name is required.")
    if not category:
        raise ValueError("Please choose a category.")
    if price <= 0:
        raise ValueError("Please enter a valid price.")

    return {
        "name": name,
        "category": category,
        "unit": unit,
        "short_description": short_description,
        "description": description or short_description,
        "highlights": highlights,
        "price": price,
        "old_price": old_price,
        "discount_label": _compute_discount_label(price, old_price),
        "stock_qty": stock_qty,
        "in_stock": stock_qty > 0,
    }


def create_product(form_data, image_file=None, image_url=None):
    fields = _build_product_fields(form_data)

    if image_file:
        image = _save_uploaded_image(image_file)
    elif image_url and image_url.strip():
        image = image_url.strip()
    else:
        raise ValueError("Please upload a product image or paste an image URL.")

    doc = {
        "id": _unique_slug(fields["name"]),
        "image": image,
        "rating": 0,
        "stars": [],
        "reviews": 0,
        **fields,
    }
    products_collection.insert_one(doc)
    return doc["id"]


def update_product(product_id, form_data, image_file=None, image_url=None):
    fields = _build_product_fields(form_data)
    update = dict(fields)

    if image_file:
        update["image"] = _save_uploaded_image(image_file)
    elif image_url and image_url.strip():
        update["image"] = image_url.strip()

    result = products_collection.update_one({"id": product_id}, {"$set": update})
    if result.matched_count == 0:
        raise ValueError("Product not found.")


def delete_product(product_id):
    products_collection.delete_one({"id": product_id})
