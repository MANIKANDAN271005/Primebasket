# PrimeBasket — Setup, MongoDB, and Updates

## What Was Upgraded

### ✅ Real Grocery Photos
- Replaced all cartoon/SVG product images with real high-quality photos from Unsplash & Wikimedia Commons.
- All 18 default products (avocados, milk, bread, tea, jam, rice, olive oil, shampoo, etc.) now show real photos.
- Photos auto-upgrade: if you seeded the database before this update, old external URLs automatically swap to local photos on first run.
- Admin can upload photos when adding/editing products.

### ✅ Premium Color Theme
**Dark Green • Cream • White • Gold**
- Primary: `#1B4332` (deep forest green)
- Accent: `#C9A227` (warm gold)
- Surface: `#FFFFFF` + `#FAF6EC` (cream background)
- All buttons, badges, and sections use the premium palette with careful contrast.

### ✅ Complete UI Redesign
- **Navbar**: Sticky, modern, collapses to burger below 1200px. Search bar on desktop. User menu for logged-in shoppers.
- **Hero Carousel**: Real photos, three rotating slides, on-brand badges, swipe controls.
- **Category Cards**: Real images, descriptions, "Explore" buttons that filter the product grid below.
- **Product Cards**: Consistent 4:3 aspect ratio, on-theme badges (discounts, stock status), aligned "Add to Cart" buttons. Hover lifts the card.
- **Footer**: Dark green with gold accent border. 4-column layout (Brand, Company, Support, Contact). Responsive at all breakpoints.
- **Testimonials**: Customer initials (AK, DO, GN) replace cartoon avatars. Clean, minimal.
- **Admin Panel**: Matching green sidebar, styled forms, category list with photos and product counts, edit/delete actions. Category rename moves all products to the new name.

### ✅ Fully Responsive Layout
- **Desktop (≥1200px)**: Full-width navbar with search, 4-column product grid, side-by-side hero and content.
- **Tablet (768–1199px)**: Collapsed navbar, 2-column product grid, centered hero and copy.
- **Mobile (<768px)**: Full-width single column, horizontal-scroll category filter, stacked hero (text above photo), touch-friendly buttons and spacing.
- **All buttons, cards, and forms** scale and reflow appropriately at every breakpoint.

### ✅ Separate Admin Panel
- **URL**: `/pb-admin/` (separate from Django's `/admin/`)
- **Features**:
  - Dashboard with stats (products, categories, out-of-stock count, orders, registered users)
  - Product CRUD (add, edit, delete) with image upload or URL paste
  - Category management: add, edit (rename + move products), delete
  - Photo support: each category and product stores an image
  - Admin must log in; session-based auth with MongoDB `admins_collection`
  - No default account—use the setup command below to create one

---

## How to Run the Project

### 1. Install MongoDB (Windows)

#### Option A: Download & Install
1. Go to https://www.mongodb.com/try/download/community
2. Select **Windows** → **MSI** → latest stable version (e.g., v8.0)
3. Run the installer (`mongodb-org-*.msi`)
4. Keep default install path (`C:\Program Files\MongoDB\Server\[version]`)
5. **Optionally** install "MongoDB Compass" for a visual DB browser (step in the installer)
6. MongoDB installs as a **Windows service** and auto-starts ✓

#### Option B: Use Docker (if Docker Desktop is running)
```powershell
docker run -d -p 27017:27017 --name primebasket-mongo mongo:7
```

### 2. Verify MongoDB is Running
```powershell
# Test the connection
& 'C:\Program Files\MongoDB\Server\[version]\bin\mongosh.exe' --version
```
If it works, MongoDB is listening on `localhost:27017`.

### 3. Start the PrimeBasket Project

#### Step 1: Navigate to the Project
```powershell
cd D:\Projects\PrimeBasket\PrimeBasket
```

#### Step 2: Activate the Virtual Environment
```powershell
..\venv312\Scripts\Activate.ps1
```

#### Step 3: Create an Admin Account
```powershell
python manage.py create_admin --username admin --password YourSecurePassword123
```
**Or** let it prompt you securely:
```powershell
python manage.py create_admin --username admin
# Then enter password when prompted (hidden input)
# Then confirm password when prompted
```

#### Step 4: Start the Development Server
```powershell
python manage.py runserver 127.0.0.1:8000
```

You should see:
```
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

### 4. Access the Website

**Customer Site**  
- Homepage: http://127.0.0.1:8000/  
- Products: http://127.0.0.1:8000/#products  
- Wishlist: http://127.0.0.1:8000/wishlist/  
- Cart: http://127.0.0.1:8000/cart/  

**Admin Panel**  
- Login: http://127.0.0.1:8000/pb-admin/login/  
  - Username: `admin` (or whatever you created)
  - Password: `YourSecurePassword123` (or whatever you set)
- Dashboard: http://127.0.0.1:8000/pb-admin/
- Products: http://127.0.0.1:8000/pb-admin/products/
- Categories: http://127.0.0.1:8000/pb-admin/categories/

---

## Database & Configuration

### MongoDB Collections
The project creates these collections automatically on first run:

| Collection | Purpose |
|-----------|---------|
| `products` | Product catalog (name, price, category, image, stock, etc.) |
| `categories` | Category list (name, description, image) |
| `users` | Customer accounts (email, password hash, profile) |
| `cart` | Shopping carts keyed by session/user |
| `wishlist` | Saved products per customer |
| `orders` | Placed orders with items and status |
| `reviews` | Product reviews and ratings |
| `admins` | Admin accounts (username, password hash) |
| `newsletter` | Email subscriptions |
| `messages` | Contact form submissions |

### Connection String (`.env`)
```
MONGODB_URI=mongodb://localhost:27017/
DATABASE_NAME=primebasket
MONGODB_MAX_POOL_SIZE=10
MONGODB_SERVER_SELECTION_TIMEOUT_MS=3000
```

To use a remote MongoDB Atlas cluster, replace `MONGODB_URI`:
```
MONGODB_URI=mongodb+srv://user:password@cluster.mongodb.net/
```

---

## Key Features

### For Customers
✓ Browse products by category or search  
✓ View detailed product pages with reviews  
✓ Add to cart, checkout, place orders  
✓ Save items to wishlist  
✓ Create account and view order history  
✓ Apply discount codes (SAVE10, FRESH20, FLAT50)  
✓ Leave product reviews and ratings  

### For Admins
✓ Dashboard with key metrics  
✓ Add new products (upload photo or paste URL)  
✓ Edit product details, price, stock, image  
✓ Delete products  
✓ Add new categories  
✓ Edit categories (rename + auto-moves all products)  
✓ Delete categories  

### Image Management
- **Seeded products**: Use real photos in `static/images/products/`
- **Admin uploads**: File stored in `media/products/[uuid].jpg`
- **Admin URLs**: Store external image URLs (on any server)
- **Fallback**: If image missing, uses `static/images/products/placeholder.jpg`

---

## Troubleshooting

### "MongoDB connection refused"
1. Verify MongoDB is running:  
   ```powershell
   tasklist | findstr mongod
   ```
   If no `mongod.exe`, MongoDB isn't running. Start it:
   ```powershell
   # Via Windows Service (if installed)
   Start-Service MongoDB
   
   # Or manually
   & 'C:\Program Files\MongoDB\Server\8.0\bin\mongod.exe'
   ```

2. Verify it's listening on port 27017:
   ```powershell
   netstat -tuln | findstr :27017
   ```

### "Admin login not working"
Ensure the admin account was created:
```powershell
python manage.py create_admin --username admin --password TestPass123
```

### "Photos not showing"
- Check `.env` → `MONGODB_URI` points to correct MongoDB
- Verify `static/images/` has the photo files
- Admin-uploaded photos go to `media/products/`; ensure `media/` is writable
- On first load, seeded products from `product_data.py` auto-sync to MongoDB

### "Navbar/hero looks broken on mobile"
This is expected in Edge headless (applies 1.27× device scale). In a real mobile browser, the layout is fully responsive and works correctly.

---

## Project Structure
```
D:\Projects\PrimeBasket\PrimeBasket\
├── manage.py                          # Django CLI
├── .env                               # Config (MongoDB URI, etc.)
├── PrimeBasket/                       # Django project
│   ├── settings.py                    # App config
│   ├── urls.py                        # URL router
│   ├── database/
│   │   └── mongodb.py                 # MongoDB client & collections
│   └── context_processors.py          # Template globals
├── Store/                             # Main app
│   ├── models.py                      # (MongoDB, no ORM models)
│   ├── views.py                       # Customer views
│   ├── admin_views.py                 # Admin panel views
│   ├── admin_urls.py                  # Admin routes
│   ├── catalog.py                     # Product/category CRUD
│   ├── product_data.py                # Seed data + legacy URLs
│   └── management/commands/
│       └── create_admin.py            # Create admin account
├── templates/                         # HTML (Jinja2)
│   ├── base.html                      # Layout skeleton
│   ├── navbar.html, footer.html       # Reusable sections
│   ├── index.html                     # Homepage
│   ├── login.html, register.html      # Auth
│   ├── cart.html, wishlist.html       # Shopping
│   ├── product_detail.html            # Product page
│   ├── admin_panel/                   # Admin templates
│   │   ├── login.html                 # Admin login
│   │   ├── dashboard.html             # Admin home
│   │   ├── product_list.html          # Product table
│   │   ├── product_form.html          # Add/edit product
│   │   ├── category_list.html         # Category table
│   │   └── category_form.html         # Add/edit category
│   └── ...other pages
├── static/                            # Assets (not version-controlled)
│   ├── css/
│   │   ├── style.css                  # Main styles (premium theme)
│   │   └── admin.css                  # Admin panel styles
│   ├── js/
│   │   └── script.js                  # Frontend logic
│   └── images/
│       ├── logo.svg                   # Brand logo
│       ├── hero/                      # Hero carousel (hero-1.jpg, etc.)
│       ├── products/                  # Product photos (auto-seeded)
│       ├── categories/                # Category images
│       └── misc/                      # Wishlist, etc.
└── media/                             # Admin-uploaded files (at runtime)
    └── products/                      # Uploaded product images
```

---

## Next Steps

1. **Run MongoDB** (see setup above)
2. **Start the server** (`python manage.py runserver`)
3. **Create an admin account** (`python manage.py create_admin`)
4. **Visit** http://127.0.0.1:8000/ and http://127.0.0.1:8000/pb-admin/

That's it! The database seeds with products on first visit, and you're ready to shop or manage.
