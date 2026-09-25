"""Seed data for the PrimeBasket catalog.

Products and categories live in MongoDB (`products_collection` / `categories_collection`, see
`Store/catalog.py`) so the admin panel can manage them. `DEFAULT_PRODUCTS` / `DEFAULT_CATEGORIES` here
are only used once, to seed those collections the first time the app runs against an empty database --
after that, MongoDB is the single source of truth and this file is never read again.

The `name` of every entry matches the `data-product-name` used on the homepage product cards exactly --
that string doubles as the product_id stored in the cart/wishlist/order collections, so keep them in
sync if either side changes.
"""

# Product/category photos are real photos stored under static/images/ (no hotlinking, so they can't
# break when a third-party URL changes).
DEFAULT_CATEGORIES = [
    {"name": "Fruits", "image": "images/categories/fruits.jpg", "description": "Sweet, juicy options for every season."},
    {"name": "Vegetables", "image": "images/categories/vegetables.jpg", "description": "Fresh veggies sourced from local farms."},
    {"name": "Dairy", "image": "images/products/fresh-milk.jpg", "description": "Premium milk, cheese, yogurt, and more."},
    {"name": "Bakery", "image": "images/products/sourdough-bread.jpg", "description": "Freshly baked loaves and pastries daily."},
    {"name": "Beverages", "image": "images/products/fresh-orange-juice.jpg", "description": "Refreshing juices, tea, coffee, and water."},
    {"name": "Snacks", "image": "images/categories/snacks.jpg", "description": "Crunchy, tasty, and perfect for every craving."},
    {"name": "Rice & Grains", "image": "images/products/basmati-rice.jpg", "description": "Everyday staples like rice, flour, and grains."},
    {"name": "Cooking Essentials", "image": "images/products/extra-virgin-olive-oil.jpg", "description": "Oils, salts, and pantry basics for every kitchen."},
    {"name": "Household", "image": "images/products/multi-surface-cleaner.jpg", "description": "Cleaning supplies to keep your home fresh."},
    {"name": "Personal Care", "image": "images/products/herbal-shampoo.jpg", "description": "Everyday essentials for you and your family."},
]

# Image values the seed data used before the switch to local photos. Databases seeded earlier still
# hold these; catalog.upgrade_seed_images() swaps them for the new local photo (admin-set images are
# never touched because they won't match this list).
LEGACY_SEED_IMAGES = {
    "https://images.unsplash.com/photo-1523049673857-eb18f1d7b578?auto=format&fit=crop&w=1000&q=80",
    "https://images.unsplash.com/photo-1560806887-1e4cd0b6cbd6?auto=format&fit=crop&w=1000&q=80",
    "https://commons.wikimedia.org/wiki/Special:FilePath/Tomatoes.JPG?width=1000",
    "https://images.unsplash.com/photo-1550583724-b2692b85b150?auto=format&fit=crop&w=1000&q=80",
    "https://images.unsplash.com/photo-1517686469429-8bdb88b9f907?auto=format&fit=crop&w=1000&q=80",
    "https://images.unsplash.com/photo-1600271886742-f049cd451bba?auto=format&fit=crop&w=1000&q=80",
    "https://images.unsplash.com/photo-1571748982800-fa51082c2224?auto=format&fit=crop&w=1000&q=80",
    "https://images.unsplash.com/photo-1564890369478-c89ca6d9cde9?auto=format&fit=crop&w=1000&q=80",
    "https://upload.wikimedia.org/wikipedia/commons/0/0c/Jam_and_toast.jpg",
    "https://commons.wikimedia.org/wiki/Special:FilePath/A_bowl_of_rice.jpg?width=1000",
    "https://commons.wikimedia.org/wiki/Special:FilePath/Wheat_flour_01.jpg?width=1000",
    "https://commons.wikimedia.org/wiki/Special:FilePath/Bottle_of_olive_oil.jpg?width=1000",
    "https://commons.wikimedia.org/wiki/Special:FilePath/Fine_sea_salt.JPG?width=1000",
    "https://commons.wikimedia.org/wiki/Special:FilePath/Bouteille_savon_vaisselle_Mir.jpg?width=1000",
    "https://commons.wikimedia.org/wiki/Special:FilePath/Spray_bottle.jpg?width=1000",
    "https://commons.wikimedia.org/wiki/Special:FilePath/Dove_Shampoo.jpg?width=1000",
    "https://commons.wikimedia.org/wiki/Special:FilePath/Shower_gel_bottles.jpg?width=1000",
    "images/products/product-1.svg",
}

DEFAULT_PRODUCTS = [
    {
        "id": "organic-avocados",
        "name": "Organic Avocados",
        "category": "Fruits",
        "image": "images/products/organic-avocados.jpg",
        "price": 240,
        "old_price": 300,
        "discount_label": "20% Off",
        "unit": "KG",
        "rating": 4.8,
        "stars": ["bi-star-fill", "bi-star-fill", "bi-star-fill", "bi-star-fill", "bi-star-half"],
        "reviews": 186,
        "in_stock": True,
        "stock_qty": 64,
        "short_description": "Creamy, nutrient-rich avocados for salads and toast.",
        "description": (
            "Hand-picked, farm-fresh avocados with a rich, buttery texture. Perfectly ripened "
            "and ready for guacamole, salads, or your morning avocado toast."
        ),
        "highlights": [
            "Sourced from local organic farms",
            "Rich in healthy fats and fiber",
            "Hand-selected for ripeness",
        ],
    },
    {
        "id": "crisp-apples",
        "name": "Crisp Apples",
        "category": "Fruits",
        "image": "images/products/crisp-apples.jpg",
        "price": 180,
        "old_price": 210,
        "discount_label": "15% Off",
        "unit": "KG",
        "rating": 4.7,
        "stars": ["bi-star-fill", "bi-star-fill", "bi-star-fill", "bi-star-fill", "bi-star"],
        "reviews": 154,
        "in_stock": True,
        "stock_qty": 92,
        "short_description": "Sweet and crunchy fruit perfect for lunchboxes.",
        "description": (
            "Juicy, crisp apples picked at peak freshness. A naturally sweet, versatile snack "
            "that's great in lunchboxes, salads, or baked into your favorite desserts."
        ),
        "highlights": [
            "Naturally sweet and crunchy",
            "No added wax or preservatives",
            "Great source of dietary fiber",
        ],
    },
    {
        "id": "fresh-tomatoes",
        "name": "Fresh Tomatoes",
        "category": "Vegetables",
        "image": "images/products/fresh-tomatoes.jpg",
        "price": 120,
        "old_price": 140,
        "discount_label": "14% Off",
        "unit": "KG",
        "rating": 4.6,
        "stars": ["bi-star-fill", "bi-star-fill", "bi-star-fill", "bi-star-fill", "bi-star"],
        "reviews": 102,
        "in_stock": True,
        "stock_qty": 80,
        "short_description": "Vine-ripened tomatoes, juicy and full of flavor.",
        "description": (
            "Vine-ripened tomatoes picked at peak season for a naturally sweet, juicy flavor. "
            "Great for salads, sauces, and everyday cooking."
        ),
        "highlights": [
            "Vine-ripened for natural sweetness",
            "Rich in vitamin C and antioxidants",
            "Locally sourced from partner farms",
        ],
    },
    {
        "id": "fresh-milk",
        "name": "Fresh Milk",
        "category": "Dairy",
        "image": "images/products/fresh-milk.jpg",
        "price": 140,
        "old_price": 155,
        "discount_label": "10% Off",
        "unit": "L",
        "rating": 5.0,
        "stars": ["bi-star-fill", "bi-star-fill", "bi-star-fill", "bi-star-fill", "bi-star-fill"],
        "reviews": 231,
        "in_stock": True,
        "stock_qty": 120,
        "short_description": "Creamy dairy goodness with a rich, wholesome taste.",
        "description": (
            "Pasteurized whole milk delivered fresh from trusted local dairies. Rich, creamy, "
            "and wholesome -- perfect for your morning coffee, cereal, or baking."
        ),
        "highlights": [
            "Sourced from grass-fed cows",
            "Pasteurized for safety and freshness",
            "No added hormones",
        ],
    },
    {
        "id": "sourdough-bread",
        "name": "Sourdough Bread",
        "category": "Bakery",
        "image": "images/products/sourdough-bread.jpg",
        "price": 220,
        "old_price": 250,
        "discount_label": "12% Off",
        "unit": "EA",
        "rating": 4.9,
        "stars": ["bi-star-fill", "bi-star-fill", "bi-star-fill", "bi-star-fill", "bi-star-half"],
        "reviews": 142,
        "in_stock": True,
        "stock_qty": 38,
        "short_description": "Crisp crust and a soft, airy crumb for every meal.",
        "description": (
            "Slow-fermented, hand-kneaded sourdough baked fresh daily. A crisp golden crust "
            "gives way to a soft, airy crumb with a naturally tangy flavor."
        ),
        "highlights": [
            "Naturally leavened, no commercial yeast",
            "Baked fresh in small batches",
            "No preservatives or additives",
        ],
    },
    {
        "id": "fresh-orange-juice",
        "name": "Fresh Orange Juice",
        "category": "Beverages",
        "image": "images/products/fresh-orange-juice.jpg",
        "price": 320,
        "old_price": 390,
        "discount_label": "18% Off",
        "unit": "L",
        "rating": 4.6,
        "stars": ["bi-star-fill", "bi-star-fill", "bi-star-fill", "bi-star-fill", "bi-star"],
        "reviews": 98,
        "in_stock": True,
        "stock_qty": 55,
        "short_description": "A bright, refreshing citrus pour for every morning.",
        "description": (
            "Cold-pressed from sun-ripened oranges with no added sugar or preservatives. A "
            "bright, refreshing pour that's perfect for breakfast or an afternoon pick-me-up."
        ),
        "highlights": [
            "100% cold-pressed, no added sugar",
            "Packed with vitamin C",
            "Bottled fresh, never from concentrate",
        ],
    },
    {
        "id": "classic-granola",
        "name": "Classic Granola",
        "category": "Snacks",
        "image": "images/products/classic-granola.jpg",
        "price": 260,
        "old_price": 280,
        "discount_label": "8% Off",
        "unit": "KG",
        "rating": 4.8,
        "stars": ["bi-star-fill", "bi-star-fill", "bi-star-fill", "bi-star-fill", "bi-star-half"],
        "reviews": 121,
        "in_stock": True,
        "stock_qty": 47,
        "short_description": "A crunchy blend of oats, nuts, and honey.",
        "description": (
            "A wholesome, oven-toasted blend of rolled oats, mixed nuts, and golden honey. "
            "Perfect over yogurt, with milk, or straight out of the bag as a snack."
        ),
        "highlights": [
            "Oven-toasted rolled oats and nuts",
            "Naturally sweetened with honey",
            "Great source of whole grains",
        ],
    },
    {
        "id": "herbal-tea-pack",
        "name": "Herbal Tea Pack",
        "category": "Beverages",
        "image": "images/products/herbal-tea-pack.jpg",
        "price": 195,
        "old_price": 260,
        "discount_label": "25% Off",
        "unit": "PK",
        "rating": 4.5,
        "stars": ["bi-star-fill", "bi-star-fill", "bi-star-fill", "bi-star-fill", "bi-star"],
        "reviews": 76,
        "in_stock": True,
        "stock_qty": 5,
        "short_description": "Calming blends for mindful mornings and evenings.",
        "description": (
            "A soothing pack of herbal infusions blended from chamomile, mint, and lemongrass. "
            "Caffeine-free and calming, ideal for mindful mornings or a relaxed evening wind-down."
        ),
        "highlights": [
            "Caffeine-free herbal blend",
            "Whole-leaf ingredients, no dust or fannings",
            "Resealable pack for lasting freshness",
        ],
    },
    {
        "id": "artisan-jam",
        "name": "Artisan Jam",
        "category": "Bakery",
        "image": "images/products/artisan-jam.jpg",
        "price": 150,
        "old_price": 180,
        "discount_label": "16% Off",
        "unit": "JR",
        "rating": 4.7,
        "stars": ["bi-star-fill", "bi-star-fill", "bi-star-fill", "bi-star-fill", "bi-star-half"],
        "reviews": 89,
        "in_stock": True,
        "stock_qty": 73,
        "short_description": "A delightful spread for toast, pastries, and desserts.",
        "description": (
            "Small-batch fruit preserves simmered slowly for a rich, spoonable spread. Delicious "
            "on toast, swirled into yogurt, or spooned over warm pastries."
        ),
        "highlights": [
            "Small-batch, slow-simmered",
            "Made with real fruit, no corn syrup",
            "No artificial colors or flavors",
        ],
    },
    {
        "id": "basmati-rice",
        "name": "Basmati Rice",
        "category": "Rice & Grains",
        "image": "images/products/basmati-rice.jpg",
        "price": 350,
        "old_price": 400,
        "discount_label": "12% Off",
        "unit": "KG",
        "rating": 4.9,
        "stars": ["bi-star-fill", "bi-star-fill", "bi-star-fill", "bi-star-fill", "bi-star-fill"],
        "reviews": 210,
        "in_stock": True,
        "stock_qty": 88,
        "short_description": "Long-grain aromatic rice for fluffy, fragrant meals.",
        "description": (
            "Aged, extra-long-grain basmati rice with a naturally fragrant aroma. Cooks up light "
            "and fluffy every time -- perfect for biryani, pilaf, or a simple side."
        ),
        "highlights": [
            "Naturally aromatic, extra-long grain",
            "Aged for better texture and flavor",
            "Low in fat, easy to digest",
        ],
    },
    {
        "id": "whole-wheat-flour",
        "name": "Whole Wheat Flour",
        "category": "Rice & Grains",
        "image": "images/products/whole-wheat-flour.jpg",
        "price": 180,
        "old_price": 200,
        "discount_label": "10% Off",
        "unit": "KG",
        "rating": 4.6,
        "stars": ["bi-star-fill", "bi-star-fill", "bi-star-fill", "bi-star-fill", "bi-star"],
        "reviews": 64,
        "in_stock": False,
        "stock_qty": 0,
        "short_description": "Stone-ground flour for soft rotis and home baking.",
        "description": (
            "Finely stone-ground from whole wheat grain, keeping the natural bran and germ intact. "
            "Great for soft rotis, chapatis, and everyday home baking."
        ),
        "highlights": [
            "Stone-ground, 100% whole grain",
            "No bleaching agents or additives",
            "Rich in fiber and natural nutrients",
        ],
    },
    {
        "id": "extra-virgin-olive-oil",
        "name": "Extra Virgin Olive Oil",
        "category": "Cooking Essentials",
        "image": "images/products/extra-virgin-olive-oil.jpg",
        "price": 480,
        "old_price": 550,
        "discount_label": "13% Off",
        "unit": "L",
        "rating": 4.8,
        "stars": ["bi-star-fill", "bi-star-fill", "bi-star-fill", "bi-star-fill", "bi-star-half"],
        "reviews": 132,
        "in_stock": True,
        "stock_qty": 41,
        "short_description": "Cold-pressed olive oil with a smooth, fruity finish.",
        "description": (
            "Cold-pressed from the first harvest for a smooth, fruity flavor with a peppery "
            "finish. Ideal for dressings, marinades, and everyday cooking."
        ),
        "highlights": [
            "Cold-pressed, first extraction",
            "Rich in heart-healthy monounsaturated fats",
            "Bottled to protect flavor and freshness",
        ],
    },
    {
        "id": "sea-salt",
        "name": "Sea Salt",
        "category": "Cooking Essentials",
        "image": "images/products/sea-salt.jpg",
        "price": 90,
        "old_price": 110,
        "discount_label": "18% Off",
        "unit": "KG",
        "rating": 4.7,
        "stars": ["bi-star-fill", "bi-star-fill", "bi-star-fill", "bi-star-fill", "bi-star"],
        "reviews": 58,
        "in_stock": True,
        "stock_qty": 130,
        "short_description": "Naturally harvested, unrefined sea salt.",
        "description": (
            "Naturally harvested and sun-dried sea salt with a clean, mineral-rich taste. "
            "Unrefined and additive-free, perfect for everyday seasoning."
        ),
        "highlights": [
            "Naturally sun-dried and unrefined",
            "No anti-caking agents or additives",
            "Rich in natural trace minerals",
        ],
    },
    {
        "id": "dish-wash-liquid",
        "name": "Dish Wash Liquid",
        "category": "Household",
        "image": "images/products/dish-wash-liquid.jpg",
        "price": 150,
        "old_price": 175,
        "discount_label": "14% Off",
        "unit": "EA",
        "rating": 4.5,
        "stars": ["bi-star-fill", "bi-star-fill", "bi-star-fill", "bi-star-fill", "bi-star"],
        "reviews": 47,
        "in_stock": True,
        "stock_qty": 60,
        "short_description": "Grease-cutting formula that's gentle on hands.",
        "description": (
            "A concentrated, grease-cutting dish wash liquid that rinses clean and leaves no "
            "residue -- tough on grease, gentle on your hands."
        ),
        "highlights": [
            "Cuts grease fast, rinses clean",
            "Gentle, dermatologically tested formula",
            "Concentrated -- a little goes a long way",
        ],
    },
    {
        "id": "multi-surface-cleaner",
        "name": "Multi-Surface Cleaner",
        "category": "Household",
        "image": "images/products/multi-surface-cleaner.jpg",
        "price": 210,
        "old_price": 240,
        "discount_label": "12% Off",
        "unit": "EA",
        "rating": 4.6,
        "stars": ["bi-star-fill", "bi-star-fill", "bi-star-fill", "bi-star-fill", "bi-star"],
        "reviews": 39,
        "in_stock": True,
        "stock_qty": 54,
        "short_description": "One spray for counters, glass, and more.",
        "description": (
            "A streak-free, all-purpose cleaning spray safe for counters, glass, and most "
            "household surfaces. Freshens as it cleans."
        ),
        "highlights": [
            "Streak-free on glass and counters",
            "Fresh scent, no harsh fumes",
            "One bottle for multiple surfaces",
        ],
    },
    {
        "id": "herbal-shampoo",
        "name": "Herbal Shampoo",
        "category": "Personal Care",
        "image": "images/products/herbal-shampoo.jpg",
        "price": 260,
        "old_price": 300,
        "discount_label": "13% Off",
        "unit": "EA",
        "rating": 4.7,
        "stars": ["bi-star-fill", "bi-star-fill", "bi-star-fill", "bi-star-fill", "bi-star-half"],
        "reviews": 91,
        "in_stock": True,
        "stock_qty": 72,
        "short_description": "A gentle herbal blend for everyday hair care.",
        "description": (
            "A sulfate-free herbal shampoo blended with natural extracts to cleanse gently while "
            "leaving hair soft and refreshed."
        ),
        "highlights": [
            "Sulfate-free, gentle daily formula",
            "Blended with natural herbal extracts",
            "Dermatologically tested",
        ],
    },
    {
        "id": "aloe-vera-body-wash",
        "name": "Aloe Vera Body Wash",
        "category": "Personal Care",
        "image": "images/products/aloe-vera-body-wash.jpg",
        "price": 220,
        "old_price": 250,
        "discount_label": "12% Off",
        "unit": "EA",
        "rating": 4.8,
        "stars": ["bi-star-fill", "bi-star-fill", "bi-star-fill", "bi-star-fill", "bi-star-half"],
        "reviews": 68,
        "in_stock": True,
        "stock_qty": 49,
        "short_description": "Soothing aloe vera wash for soft, hydrated skin.",
        "description": (
            "A soap-free body wash infused with soothing aloe vera to cleanse without stripping "
            "moisture, leaving skin soft and refreshed."
        ),
        "highlights": [
            "Soap-free, moisture-friendly formula",
            "Infused with soothing aloe vera",
            "Suitable for daily use",
        ],
    },
]

# Simple, server-validated coupon codes. Discount amounts are always recomputed
# from the live cart total on the server -- the client never gets to say how
# much a coupon is worth.
COUPONS = {
    "SAVE10": {"type": "percent", "value": 10, "description": "10% off your order"},
    "FRESH20": {"type": "percent", "value": 20, "description": "20% off your order"},
    "FLAT50": {"type": "flat", "value": 50, "description": "$50 off your order"},
}
