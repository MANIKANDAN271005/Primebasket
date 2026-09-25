document.addEventListener('DOMContentLoaded', () => {
  const navbar = document.querySelector('.navbar');
  const scrollTopBtn = document.getElementById('scrollTopBtn');
  const navLinks = document.querySelectorAll('.navbar .nav-link');
  const sections = document.querySelectorAll('section[id]');
  const heroCarousel = document.getElementById('heroCarousel');
  const testimonialCarousel = document.getElementById('testimonialCarousel');
  const searchForm = document.getElementById('searchForm');
  const searchInput = document.getElementById('productSearch');
  const productCards = document.querySelectorAll('.product-card');
  const categoryFilterButtons = document.querySelectorAll('.category-filter-btn');
  const noProductsMessage = document.getElementById('noProductsMessage');
  const wishlistButtons = document.querySelectorAll('.wishlist-btn');
  const qtyButtons = document.querySelectorAll('.qty-btn');
  const addToCartButtons = document.querySelectorAll('.add-to-cart');
  const newsletterForm = document.getElementById('newsletterForm');
  const newsletterEmail = document.getElementById('newsletterEmail');
  const newsletterMessage = document.getElementById('newsletterMessage');
  const cartCounter = document.getElementById('cartCounter') || document.getElementById('cartCount');
  const wishlistCounter = document.getElementById('wishlistCount');

  const loginForm = document.getElementById('loginForm');
  const loginEmail = document.getElementById('email');
  const loginPassword = document.getElementById('password');
  const loginMessage = document.getElementById('loginMessage');
  const loginToggle = document.getElementById('togglePassword');
  const registerForm = document.getElementById('registerForm');
  const fullName = document.getElementById('fullname');
  const registerEmail = document.getElementById('email');
  const phone = document.getElementById('phone');
  const registerPassword = document.getElementById('password');
  const confirmPassword = document.getElementById('confirmPassword');
  const terms = document.getElementById('terms');
  const registerMessage = document.getElementById('registerMessage');
  const registerToggle = document.getElementById('togglePassword');
  const confirmToggle = document.getElementById('toggleConfirmPassword');

  // Wishlist now lives in MongoDB, tied to the logged-in user's session email,
  // instead of localStorage. This array is a local cache of what the server returned.
  let wishlistItems = [];

  // Cart also lives in MongoDB, tied to the logged-in user's session email.
  // This array is a local cache of what the server returned.
  let cartItems = [];
  let cartRequiresLogin = false;
  const cartPendingProductIds = new Set();

  const getCsrfToken = () => document.querySelector('input[name=csrfmiddlewaretoken]')?.value || '';

  const formatCurrency = (value) => `$${Number(value || 0).toFixed(2)}`;

  // READ: load the logged-in user's cart from MongoDB via GET /cart/items/
  const fetchCart = () => {
    return fetch('/cart/items/')
      .then((response) => {
        cartRequiresLogin = response.status === 401;
        return response.ok ? response.json() : { success: false, items: [] };
      })
      .then((data) => {
        cartItems = data.items || [];
      })
      .catch(() => {
        cartItems = [];
      });
  };

  // CREATE: POST /cart/add/ -> cart_collection.insert_one() on the server
  // (or update_one() to bump the quantity if the product is already in the cart)
  const addToCartServer = (product, quantity = 1) => {
    fetch('/cart/add/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCsrfToken(),
      },
      body: JSON.stringify({
        product_id: product.id,
        name: product.name,
        image: product.image,
        price: product.price,
        unit: product.unit,
        quantity,
      }),
    })
      .then((response) => response.json().then((data) => ({ ok: response.ok, data })))
      .then(({ ok, data }) => {
        if (!ok || !data.success) {
          alert(data.error || 'Unable to add to cart.');
          return;
        }
        const existing = cartItems.find((item) => item.product_id === product.id);
        if (existing) {
          existing.quantity = data.quantity;
        } else {
          cartItems.push({
            product_id: product.id,
            name: product.name,
            image: product.image,
            price: product.price,
            unit: product.unit,
            quantity: data.quantity,
          });
        }
        updateCounters();
        renderCartPage();
      });
  };

  // UPDATE: POST /cart/update/ -> cart_collection.update_one() on the server
  const updateCartQtyServer = (productId, quantity) => {
    return fetch('/cart/update/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCsrfToken(),
      },
      body: JSON.stringify({ product_id: productId, quantity }),
    })
      .then((response) => response.json().then((data) => ({ ok: response.ok, data })))
      .then(({ ok, data }) => {
        if (ok && data.success) {
          const target = cartItems.find((item) => item.product_id === productId);
          if (target) target.quantity = data.quantity;
        } else {
          alert(data.error || 'Unable to update cart.');
        }
        updateCounters();
        renderCartPage();
      });
  };

  // DELETE: POST /cart/remove/ -> cart_collection.delete_one() on the server
  const removeFromCartServer = (productId) => {
    return fetch('/cart/remove/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCsrfToken(),
      },
      body: JSON.stringify({ product_id: productId }),
    })
      .then((response) => response.json().then((data) => ({ ok: response.ok, data })))
      .then(({ ok, data }) => {
        if (ok && data.success) {
          cartItems = cartItems.filter((item) => item.product_id !== productId);
        }
        updateCounters();
        renderCartPage();
      });
  };

  const clearCart = () => {
    cartItems.map((item) => item.product_id).forEach((id) => removeFromCartServer(id));
  };

  // READ: load the logged-in user's wishlist from MongoDB via GET /wishlist/items/
  const fetchWishlist = () => {
    return fetch('/wishlist/items/')
      .then((response) => (response.ok ? response.json() : { success: false, items: [] }))
      .then((data) => {
        wishlistItems = data.items || [];
      })
      .catch(() => {
        wishlistItems = [];
      });
  };

  // CREATE: POST /wishlist/add/ -> wishlist_collection.insert_one() on the server
  const addToWishlistServer = (product) => {
    fetch('/wishlist/add/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCsrfToken(),
      },
      body: JSON.stringify({
        product_id: product.id,
        name: product.name,
        image: product.image,
        price: product.price,
        unit: product.unit,
      }),
    })
      .then((response) => response.json().then((data) => ({ ok: response.ok, data })))
      .then(({ ok, data }) => {
        if (!ok || !data.success) {
          alert(data.error || 'Unable to save to wishlist.');
          syncWishlistButtons();
          return;
        }
        if (!wishlistItems.some((item) => item.product_id === product.id)) {
          wishlistItems.push({
            product_id: product.id,
            name: product.name,
            image: product.image,
            price: product.price,
            unit: product.unit,
          });
        }
        updateCounters();
        syncWishlistButtons();
        renderWishlistPage();
      })
      .catch(() => {
        syncWishlistButtons();
      });
  };

  // DELETE: POST /wishlist/remove/ -> wishlist_collection.delete_one() on the server
  const removeFromWishlistServer = (productId) => {
    fetch('/wishlist/remove/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCsrfToken(),
      },
      body: JSON.stringify({ product_id: productId }),
    })
      .then((response) => response.json().then((data) => ({ ok: response.ok, data })))
      .then(({ ok, data }) => {
        if (ok && data.success) {
          wishlistItems = wishlistItems.filter((item) => item.product_id !== productId);
        }
        updateCounters();
        syncWishlistButtons();
        renderWishlistPage();
      });
  };

  const clearWishlist = () => {
    wishlistItems.map((item) => item.product_id).forEach((id) => removeFromWishlistServer(id));
  };

  const moveAllWishlistToCart = () => {
    if (!wishlistItems.length) return;

    wishlistItems.forEach((item) => {
      addToCart({ id: item.product_id, name: item.name, image: item.image, price: item.price, unit: item.unit }, 1);
    });
    clearWishlist();
  };

  const getProductId = (card) => {
    const explicitId = card.getAttribute('data-product-id');
    if (explicitId) return explicitId;
    return card.getAttribute('data-product-name')?.trim() || 'product';
  };

  const getProductData = (card) => {
    const name = card.getAttribute('data-product-name')?.trim() || card.querySelector('h5')?.textContent?.trim() || 'PrimeBasket Product';
    const image = card.querySelector('img')?.getAttribute('src') || '';
    const priceEl = card.querySelector('.price');
    const oldPriceEl = card.querySelector('.old-price');
    const price = Number((priceEl?.textContent || '').replace(/[^\d.]/g, '')) || 0;
    const oldPrice = Number((oldPriceEl?.textContent || '').replace(/[^\d.]/g, '')) || price;
    const unit = card.querySelector('.unit-label')?.textContent?.trim() || '';

    return {
      id: getProductId(card),
      name,
      image,
      price,
      oldPrice,
      unit,
      quantity: 1,
    };
  };

  const updateCounters = () => {
    const totalWishlist = wishlistItems.length;
    const totalCart = cartItems.reduce((sum, item) => sum + Number(item.quantity || 1), 0);

    if (wishlistCounter) {
      wishlistCounter.textContent = totalWishlist;
    }

    if (cartCounter) {
      cartCounter.textContent = totalCart;
    }
  };

  const setWishlistButtonState = (button, isActive) => {
    button.classList.toggle('active', isActive);
    const icon = button.querySelector('i');
    if (!icon) return;
    icon.classList.toggle('bi-heart-fill', isActive);
    icon.classList.toggle('bi-heart', !isActive);
  };

  const syncWishlistButtons = () => {
    const ids = new Set(wishlistItems.map((item) => item.product_id));

    wishlistButtons.forEach((button) => {
      const card = button.closest('.product-card');
      const productId = card ? getProductId(card) : null;
      setWishlistButtonState(button, productId ? ids.has(productId) : false);
    });
  };

  const addToCart = (product, quantity = 1) => {
    addToCartServer(product, quantity);
  };

  const removeFromCart = (productId) => {
    if (cartPendingProductIds.has(productId)) return;
    cartPendingProductIds.add(productId);
    removeFromCartServer(productId).finally(() => cartPendingProductIds.delete(productId));
  };

  const updateQtyInCart = (productId, delta) => {
    if (cartPendingProductIds.has(productId)) return;

    const target = cartItems.find((item) => item.product_id === productId);
    if (!target) return;

    const quantity = Math.max(1, Number(target.quantity || 1) + delta);
    if (quantity === Number(target.quantity || 1)) return;

    cartPendingProductIds.add(productId);
    updateCartQtyServer(productId, quantity).finally(() => cartPendingProductIds.delete(productId));
  };

  const renderCartPage = () => {
    const cartContainer = document.getElementById('cartContainer');
    const emptyCart = document.getElementById('emptyCart');
    const cartLoginPrompt = document.getElementById('cartLoginPrompt');
    const itemCount = document.getElementById('itemCount');
    const subtotal = document.getElementById('subtotal');
    const total = document.getElementById('total');

    if (!cartContainer || !emptyCart || !itemCount || !subtotal || !total) return;

    const totalQuantity = cartItems.reduce((sum, item) => sum + Number(item.quantity || 1), 0);
    const subtotalValue = cartItems.reduce((sum, item) => sum + Number(item.price || 0) * Number(item.quantity || 1), 0);

    itemCount.textContent = totalQuantity;
    subtotal.textContent = subtotalValue.toFixed(2);
    total.textContent = subtotalValue.toFixed(2);

    if (cartRequiresLogin && cartLoginPrompt) {
      cartContainer.classList.add('d-none');
      emptyCart.classList.add('d-none');
      cartLoginPrompt.classList.remove('d-none');
      return;
    }
    if (cartLoginPrompt) cartLoginPrompt.classList.add('d-none');

    if (cartItems.length === 0) {
      cartContainer.classList.add('d-none');
      emptyCart.classList.remove('d-none');
      return;
    }

    emptyCart.classList.add('d-none');
    cartContainer.classList.remove('d-none');
    cartContainer.innerHTML = cartItems.map((item) => `
      <div class="col-12">
        <div class="card border-0 shadow-sm h-100">
          <div class="row g-3 align-items-center p-3">
            <div class="col-md-3">
              <img src="${item.image || ''}" alt="${item.name}" class="img-fluid rounded-3" style="max-height:120px; object-fit:cover;" />
            </div>
            <div class="col-md-6">
              <h5 class="fw-bold mb-2">${item.name}</h5>
              <p class="text-muted mb-3">${item.unit ? `${item.unit}` : ''}</p>
              <div class="d-flex align-items-center gap-2">
                <button class="btn btn-outline-secondary btn-sm" data-action="decrease" data-product-id="${item.product_id}" ${item.quantity <= 1 ? 'disabled' : ''}>-</button>
                <span class="px-2 fw-semibold">${item.quantity}</span>
                <button class="btn btn-outline-secondary btn-sm" data-action="increase" data-product-id="${item.product_id}">+</button>
              </div>
            </div>
            <div class="col-md-3 text-md-end">
              <div class="fw-bold text-success">${formatCurrency(Number(item.price || 0) * Number(item.quantity || 1))}</div>
              <div class="text-muted small">${formatCurrency(item.price || 0)} each</div>
              <button class="btn btn-outline-danger btn-sm mt-3" data-action="remove" data-product-id="${item.product_id}">Remove</button>
            </div>
          </div>
        </div>
      </div>
    `).join('');
  };

  const renderWishlistPage = () => {
    const wishlistTable = document.getElementById('wishlistItems');
    const emptyWishlist = document.getElementById('emptyWishlist');
    const wishlistTableContainer = document.getElementById('wishlistTableContainer');
    const wishlistSummary = document.getElementById('wishlistSummary');
    const totalWishlistItems = document.getElementById('totalWishlistItems');

    if (!wishlistTable || !emptyWishlist || !wishlistTableContainer || !wishlistSummary || !totalWishlistItems) return;

    totalWishlistItems.textContent = wishlistItems.length;

    if (wishlistItems.length === 0) {
      emptyWishlist.style.display = 'block';
      wishlistTableContainer.style.display = 'none';
      wishlistSummary.style.display = 'none';
      return;
    }

    emptyWishlist.style.display = 'none';
    wishlistTableContainer.style.display = 'block';
    wishlistSummary.style.display = 'flex';
    wishlistTable.innerHTML = wishlistItems.map((item) => `
      <tr>
        <td><img src="${item.image || ''}" alt="${item.name}" style="width:70px; height:70px; object-fit:cover; border-radius:12px;" /></td>
        <td>${item.name}</td>
        <td>${formatCurrency(item.price || 0)}</td>
        <td><span class="badge bg-success-subtle text-success">Saved</span></td>
        <td class="text-center">
          <button class="btn btn-outline-success btn-sm me-2" data-action="move-to-cart" data-product-id="${item.product_id}">Add to Cart</button>
          <button class="btn btn-outline-danger btn-sm" data-action="remove-from-wishlist" data-product-id="${item.product_id}">Remove</button>
        </td>
      </tr>
    `).join('');
  };

  const updateNavbar = () => {
    if (!navbar) return;
    navbar.classList.toggle('navbar-scrolled', window.scrollY > 20);
  };

  const updateActiveLink = () => {
    let current = '';
    const currentPath = window.location.pathname;
    const isHomePage = currentPath === '/' || currentPath === '/home/' || currentPath === '';

    sections.forEach((section) => {
      const top = section.offsetTop - 120;
      const bottom = top + section.offsetHeight;
      if (window.scrollY >= top && window.scrollY < bottom) {
        current = section.id;
      }
    });

    navLinks.forEach((link) => {
      const href = link.getAttribute('href') || '';
      const isSectionLink = href.startsWith('#');
      const isWishlistLink = href.includes('wishlist');
      const isCartLink = href.includes('cart');
      const isHomeLink = href.includes('home') || href === '/';

      let isActive = false;
      if (isSectionLink) {
        isActive = href === `#${current}` && isHomePage;
      } else if (isWishlistLink) {
        isActive = currentPath.includes('wishlist');
      } else if (isCartLink) {
        isActive = currentPath.includes('cart');
      } else if (isHomeLink) {
        isActive = isHomePage;
      }

      link.classList.toggle('active', isActive);
      if (isActive) {
        link.setAttribute('aria-current', 'page');
      } else {
        link.removeAttribute('aria-current');
      }
    });
  };

  const updateScrollTop = () => {
    if (!scrollTopBtn) return;
    scrollTopBtn.style.display = window.scrollY > 450 ? 'grid' : 'none';
  };

  if (scrollTopBtn) {
    scrollTopBtn.addEventListener('click', () => {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }

  document.querySelectorAll('a[href^="#"]').forEach((link) => {
    link.addEventListener('click', (event) => {
      const target = document.querySelector(link.getAttribute('href'));
      if (!target) return;
      event.preventDefault();
      target.scrollIntoView({ behavior: 'smooth' });
    });
  });

  if (heroCarousel) {
    new bootstrap.Carousel(heroCarousel, {
      interval: 5000,
      ride: 'carousel',
      pause: false,
      touch: true,
    });
  }

  if (testimonialCarousel) {
    new bootstrap.Carousel(testimonialCarousel, {
      interval: 6000,
      ride: 'carousel',
      pause: false,
      touch: true,
    });
  }

  let activeCategory = 'all';

  const filterProducts = (query) => {
    let visibleCount = 0;

    productCards.forEach((card) => {
      const name = card.getAttribute('data-product-name')?.toLowerCase() || '';
      const category = card.getAttribute('data-category') || '';
      const matchesSearch = name.includes(query);
      const matchesCategory = activeCategory === 'all' || category === activeCategory;
      const isVisible = matchesSearch && matchesCategory;
      const column = card.parentElement;

      if (column) column.style.display = isVisible ? '' : 'none';
      if (isVisible) visibleCount += 1;
    });

    if (noProductsMessage) {
      noProductsMessage.classList.toggle('d-none', visibleCount !== 0);
    }
  };

  if (searchInput) {
    searchInput.addEventListener('input', (event) => {
      filterProducts(event.target.value.trim().toLowerCase());
    });
  }

  if (searchForm) {
    searchForm.addEventListener('submit', (event) => {
      event.preventDefault();
      filterProducts(searchInput?.value.trim().toLowerCase() || '');
    });
  }

  if (categoryFilterButtons.length) {
    categoryFilterButtons.forEach((button) => {
      button.addEventListener('click', () => {
        activeCategory = button.getAttribute('data-category') || 'all';
        categoryFilterButtons.forEach((btn) => {
          const isActive = btn === button;
          btn.classList.toggle('active', isActive);
          btn.classList.toggle('btn-success', isActive);
          btn.classList.toggle('btn-outline-success', !isActive);
        });
        filterProducts(searchInput?.value.trim().toLowerCase() || '');
      });
    });
  }

  // "Shop by category" cards jump to the product grid with that category's filter applied.
  document.querySelectorAll('[data-explore-category]').forEach((link) => {
    link.addEventListener('click', () => {
      const name = link.getAttribute('data-explore-category');
      const match = Array.from(categoryFilterButtons).find((btn) => btn.getAttribute('data-category') === name);
      match?.click();
    });
  });

  wishlistButtons.forEach((button) => {
    const card = button.closest('.product-card');
    if (!card) return;

    button.addEventListener('click', () => {
      const product = getProductData(card);
      const isActive = button.classList.contains('active');

      if (isActive) {
        removeFromWishlistServer(product.id);
      } else {
        addToWishlistServer(product);
      }
    });
  });

  qtyButtons.forEach((button) => {
    button.addEventListener('click', () => {
      const valueSpan = button.parentElement?.querySelector('.qty-value');
      if (!valueSpan) return;
      let value = Number(valueSpan.textContent || 1);
      if (button.textContent === '+') {
        value += 1;
      } else if (value > 1) {
        value -= 1;
      }
      valueSpan.textContent = value;
    });
  });

  addToCartButtons.forEach((button) => {
    button.addEventListener('click', () => {
      const card = button.closest('.product-card');
      if (!card) return;
      const product = getProductData(card);
      const quantityValue = Number(card.querySelector('.qty-value')?.textContent || 1);
      addToCart(product, quantityValue);

      button.textContent = 'Added';
      button.classList.remove('btn-success');
      button.classList.add('btn-outline-success');
      setTimeout(() => {
        button.textContent = 'Add to Cart';
        button.classList.remove('btn-outline-success');
        button.classList.add('btn-success');
      }, 1100);
    });
  });

  if (newsletterForm && newsletterEmail && newsletterMessage) {
    newsletterForm.addEventListener('submit', (event) => {
      event.preventDefault();
      const email = newsletterEmail.value.trim();
      const isValid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);

      if (!isValid) {
        newsletterMessage.textContent = 'Please enter a valid email address.';
        newsletterMessage.className = 'form-text text-danger mt-2';
        return;
      }

      fetch('/newsletter/subscribe/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCsrfToken(),
        },
        body: JSON.stringify({ email }),
      })
        .then((response) => response.json().then((data) => ({ ok: response.ok, data })))
        .then(({ ok, data }) => {
          if (ok && data.success) {
            newsletterMessage.textContent = 'Thanks for subscribing! Fresh deals are on the way.';
            newsletterMessage.className = 'form-text text-success mt-2';
            newsletterForm.reset();
          } else {
            newsletterMessage.textContent = data.error || 'Unable to subscribe right now.';
            newsletterMessage.className = 'form-text text-danger mt-2';
          }
        })
        .catch(() => {
          newsletterMessage.textContent = 'Unable to reach the server. Please try again.';
          newsletterMessage.className = 'form-text text-danger mt-2';
        });
    });
  }

  const revealElements = document.querySelectorAll('.reveal');
  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
      }
    });
  }, { threshold: 0.15 });

  revealElements.forEach((element) => observer.observe(element));

  const countdownDate = new Date();
  countdownDate.setDate(countdownDate.getDate() + 3);
  countdownDate.setHours(12, 45, 20, 0);

  const updateCountdown = () => {
    const now = new Date();
    const distance = countdownDate - now;

    const elements = {
      days: document.getElementById('days'),
      hours: document.getElementById('hours'),
      minutes: document.getElementById('minutes'),
      seconds: document.getElementById('seconds'),
    };

    if (!elements.days || !elements.hours || !elements.minutes || !elements.seconds) return;

    if (distance < 0) {
      elements.days.textContent = '00';
      elements.hours.textContent = '00';
      elements.minutes.textContent = '00';
      elements.seconds.textContent = '00';
      return;
    }

    const days = Math.floor(distance / (1000 * 60 * 60 * 24));
    const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
    const seconds = Math.floor((distance % (1000 * 60)) / 1000);

    elements.days.textContent = String(days).padStart(2, '0');
    elements.hours.textContent = String(hours).padStart(2, '0');
    elements.minutes.textContent = String(minutes).padStart(2, '0');
    elements.seconds.textContent = String(seconds).padStart(2, '0');
  };

  updateCountdown();
  setInterval(updateCountdown, 1000);

  const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
  tooltipTriggerList.forEach((tooltipTriggerEl) => new bootstrap.Tooltip(tooltipTriggerEl));

  if (loginForm && loginEmail && loginPassword && loginMessage) {
    loginForm.addEventListener('submit', (event) => {
      event.preventDefault();
      const email = loginEmail.value.trim();
      const password = loginPassword.value.trim();
      const rememberMe = document.getElementById('remember');
      const validEmail = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
      const validPassword = password.length >= 6;

      loginEmail.classList.toggle('is-invalid', !validEmail);
      loginPassword.classList.toggle('is-invalid', !validPassword);

      if (!validEmail || !validPassword) {
        loginMessage.textContent = 'Please provide a valid email and a password with at least 6 characters.';
        loginMessage.className = 'form-text text-danger mt-3';
        return;
      }

      if (rememberMe && rememberMe.checked) {
        localStorage.setItem('primebasket-remember-me', 'true');
      } else {
        localStorage.removeItem('primebasket-remember-me');
      }

      const csrfToken = loginForm.querySelector('input[name=csrfmiddlewaretoken]')?.value || '';

      fetch('/login/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken,
        },
        body: JSON.stringify({ email, password }),
      })
        .then((response) => response.json().then((data) => ({ ok: response.ok, data })))
        .then(({ ok, data }) => {
          if (ok && data.success) {
            loginMessage.textContent = 'Login successful! Redirecting...';
            loginMessage.className = 'form-text text-success mt-3';
            loginForm.reset();
            setTimeout(() => {
              window.location.href = data.redirect || '/';
            }, 650);
          } else {
            loginMessage.textContent = data.error || 'Invalid email or password.';
            loginMessage.className = 'form-text text-danger mt-3';
          }
        })
        .catch(() => {
          loginMessage.textContent = 'Unable to reach the server. Please try again.';
          loginMessage.className = 'form-text text-danger mt-3';
        });
    });

    if (loginToggle) {
      loginToggle.addEventListener('click', () => {
        const icon = loginToggle.querySelector('i');
        const isPassword = loginPassword.type === 'password';
        loginPassword.type = isPassword ? 'text' : 'password';
        icon.className = isPassword ? 'bi bi-eye-slash-fill' : 'bi bi-eye-fill';
      });
    }
  }

  if (registerForm && fullName && registerEmail && phone && registerPassword && confirmPassword && terms && registerMessage) {
    registerForm.addEventListener('submit', (event) => {
      event.preventDefault();
      const validName = fullName.value.trim().length >= 3;
      const validEmail = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(registerEmail.value.trim());
      const validPhone = /^[0-9]{10,12}$/.test(phone.value.trim());
      const validPassword = registerPassword.value.trim().length >= 6;
      const passwordsMatch = registerPassword.value === confirmPassword.value;
      const agreed = terms.checked;

      fullName.classList.toggle('is-invalid', !validName);
      registerEmail.classList.toggle('is-invalid', !validEmail);
      phone.classList.toggle('is-invalid', !validPhone);
      registerPassword.classList.toggle('is-invalid', !validPassword);
      confirmPassword.classList.toggle('is-invalid', !passwordsMatch);
      terms.classList.toggle('is-invalid', !agreed);

      if (!validName || !validEmail || !validPhone || !validPassword || !passwordsMatch || !agreed) {
        registerMessage.textContent = 'Please fix the highlighted fields before continuing.';
        registerMessage.className = 'form-text text-danger mt-3';
        return;
      }

      const csrfToken = registerForm.querySelector('input[name=csrfmiddlewaretoken]')?.value || '';

      fetch('/register/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken,
        },
        body: JSON.stringify({
          fullname: fullName.value.trim(),
          email: registerEmail.value.trim(),
          phone: phone.value.trim(),
          password: registerPassword.value,
        }),
      })
        .then((response) => response.json().then((data) => ({ ok: response.ok, data })))
        .then(({ ok, data }) => {
          if (ok && data.success) {
            registerMessage.textContent = 'Account created successfully! Redirecting to login...';
            registerMessage.className = 'form-text text-success mt-3';
            registerForm.reset();
            setTimeout(() => {
              window.location.href = data.redirect || '/login/';
            }, 750);
          } else {
            registerMessage.textContent = data.error || 'Something went wrong. Please try again.';
            registerMessage.className = 'form-text text-danger mt-3';
          }
        })
        .catch(() => {
          registerMessage.textContent = 'Unable to reach the server. Please try again.';
          registerMessage.className = 'form-text text-danger mt-3';
        });
    });

    if (registerToggle) {
      registerToggle.addEventListener('click', () => {
        const icon = registerToggle.querySelector('i');
        const isPassword = registerPassword.type === 'password';
        registerPassword.type = isPassword ? 'text' : 'password';
        icon.className = isPassword ? 'bi bi-eye-slash-fill' : 'bi bi-eye-fill';
      });
    }

    if (confirmToggle) {
      confirmToggle.addEventListener('click', () => {
        const icon = confirmToggle.querySelector('i');
        const isPassword = confirmPassword.type === 'password';
        confirmPassword.type = isPassword ? 'text' : 'password';
        icon.className = isPassword ? 'bi bi-eye-slash-fill' : 'bi bi-eye-fill';
      });
    }
  }

  document.addEventListener('click', (event) => {
    const button = event.target.closest('[data-action]');
    if (!button) return;

    const action = button.getAttribute('data-action');
    const productId = button.getAttribute('data-product-id');

    if (action === 'decrease') {
      updateQtyInCart(productId, -1);
    } else if (action === 'increase') {
      updateQtyInCart(productId, 1);
    } else if (action === 'remove') {
      removeFromCart(productId);
    } else if (action === 'move-to-cart') {
      const target = wishlistItems.find((item) => item.product_id === productId);
      if (target) {
        addToCart({ id: target.product_id, name: target.name, image: target.image, price: target.price, unit: target.unit }, 1);
        removeFromWishlistServer(productId);
      }
    } else if (action === 'remove-from-wishlist') {
      removeFromWishlistServer(productId);
    }
  });

  const clearCartButton = document.getElementById('clearCart');
  if (clearCartButton) {
    clearCartButton.addEventListener('click', clearCart);
  }

  const clearWishlistButton = document.getElementById('clearWishlist');
  if (clearWishlistButton) {
    clearWishlistButton.addEventListener('click', clearWishlist);
  }

  const moveAllToCartButton = document.getElementById('moveAllToCart');
  if (moveAllToCartButton) {
    moveAllToCartButton.addEventListener('click', moveAllWishlistToCart);
  }

  const editProfileForm = document.getElementById('editProfileForm');
  const profileView = document.getElementById('profileView');
  const showEditProfileBtn = document.getElementById('showEditProfile');
  const cancelEditProfileBtn = document.getElementById('cancelEditProfile');
  const editProfileMessage = document.getElementById('editProfileMessage');
  const viewFullname = document.getElementById('viewFullname');
  const viewPhone = document.getElementById('viewPhone');
  const deleteAccountBtn = document.getElementById('deleteAccountBtn');
  const deleteAccountMessage = document.getElementById('deleteAccountMessage');

  if (showEditProfileBtn && cancelEditProfileBtn && editProfileForm && profileView) {
    showEditProfileBtn.addEventListener('click', () => {
      profileView.classList.add('d-none');
      showEditProfileBtn.classList.add('d-none');
      editProfileForm.classList.remove('d-none');
    });

    cancelEditProfileBtn.addEventListener('click', () => {
      editProfileForm.classList.add('d-none');
      profileView.classList.remove('d-none');
      showEditProfileBtn.classList.remove('d-none');
      editProfileMessage.textContent = '';
    });
  }

  if (editProfileForm && editProfileMessage && viewFullname && viewPhone) {
    editProfileForm.addEventListener('submit', (event) => {
      event.preventDefault();
      const fullname = document.getElementById('editFullname').value.trim();
      const phone = document.getElementById('editPhone').value.trim();
      const csrfToken = editProfileForm.querySelector('input[name=csrfmiddlewaretoken]')?.value || '';

      fetch('/profile/edit/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken,
        },
        body: JSON.stringify({ fullname, phone }),
      })
        .then((response) => response.json().then((data) => ({ ok: response.ok, data })))
        .then(({ ok, data }) => {
          if (ok && data.success) {
            viewFullname.textContent = data.fullname;
            viewPhone.textContent = data.phone;
            editProfileMessage.textContent = '';
            editProfileForm.classList.add('d-none');
            profileView.classList.remove('d-none');
            showEditProfileBtn.classList.remove('d-none');
          } else {
            editProfileMessage.textContent = data.error || 'Unable to update profile.';
            editProfileMessage.className = 'form-text text-danger mt-2';
          }
        })
        .catch(() => {
          editProfileMessage.textContent = 'Unable to reach the server. Please try again.';
          editProfileMessage.className = 'form-text text-danger mt-2';
        });
    });
  }

  if (deleteAccountBtn && deleteAccountMessage) {
    deleteAccountBtn.addEventListener('click', () => {
      if (!window.confirm('Delete your account permanently? This cannot be undone.')) {
        return;
      }

      const csrfToken = document.querySelector('#editProfileForm input[name=csrfmiddlewaretoken]')?.value || '';

      fetch('/profile/delete/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken,
        },
      })
        .then((response) => response.json().then((data) => ({ ok: response.ok, data })))
        .then(({ ok, data }) => {
          if (ok && data.success) {
            window.location.href = data.redirect || '/';
          } else {
            deleteAccountMessage.textContent = data.error || 'Unable to delete account.';
            deleteAccountMessage.className = 'form-text text-danger mt-2';
          }
        })
        .catch(() => {
          deleteAccountMessage.textContent = 'Unable to reach the server. Please try again.';
          deleteAccountMessage.className = 'form-text text-danger mt-2';
        });
    });
  }

  // ---------------------------------------------------------------------
  // Product sorting (homepage)
  // ---------------------------------------------------------------------
  const sortSelect = document.getElementById('sortProducts');
  const productsGrid = document.getElementById('productsGrid');

  if (sortSelect && productsGrid) {
    sortSelect.addEventListener('change', () => {
      const columns = Array.from(productsGrid.querySelectorAll(':scope > div'));
      const sortValue = sortSelect.value;

      columns.sort((a, b) => {
        const cardA = a.querySelector('.product-card');
        const cardB = b.querySelector('.product-card');
        if (!cardA || !cardB) return 0;

        if (sortValue === 'price-asc' || sortValue === 'price-desc') {
          const priceA = Number(cardA.getAttribute('data-price') || 0);
          const priceB = Number(cardB.getAttribute('data-price') || 0);
          return sortValue === 'price-asc' ? priceA - priceB : priceB - priceA;
        }
        if (sortValue === 'rating-desc') {
          const ratingA = Number(cardA.getAttribute('data-rating') || 0);
          const ratingB = Number(cardB.getAttribute('data-rating') || 0);
          return ratingB - ratingA;
        }
        return 0;
      });

      if (sortValue === 'default') {
        return;
      }

      columns.forEach((column) => productsGrid.appendChild(column));
    });
  }

  // ---------------------------------------------------------------------
  // Search suggestions dropdown
  // ---------------------------------------------------------------------
  const searchSuggestions = document.getElementById('searchSuggestions');

  const closeSearchSuggestions = () => {
    if (searchSuggestions) {
      searchSuggestions.classList.add('d-none');
      searchSuggestions.innerHTML = '';
    }
  };

  if (searchInput && searchSuggestions) {
    searchInput.addEventListener('input', () => {
      const query = searchInput.value.trim().toLowerCase();
      if (!query) {
        closeSearchSuggestions();
        return;
      }

      const matches = Array.from(productCards)
        .filter((card) => (card.getAttribute('data-product-name') || '').toLowerCase().includes(query))
        .slice(0, 5);

      if (!matches.length) {
        closeSearchSuggestions();
        return;
      }

      searchSuggestions.innerHTML = matches
        .map((card) => {
          const link = card.querySelector('a[href]');
          const img = card.querySelector('img');
          const name = card.getAttribute('data-product-name') || '';
          const price = card.querySelector('.price')?.textContent || '';
          const href = link ? link.getAttribute('href') : '#';
          return `<a href="${href}"><img src="${img ? img.getAttribute('src') : ''}" alt="${name}" /><span>${name}<br /><small class="text-muted">${price}</small></span></a>`;
        })
        .join('');
      searchSuggestions.classList.remove('d-none');
    });

    document.addEventListener('click', (event) => {
      if (!searchSuggestions.contains(event.target) && event.target !== searchInput) {
        closeSearchSuggestions();
      }
    });

    if (searchForm) {
      searchForm.addEventListener('submit', closeSearchSuggestions);
    }
  }

  // ---------------------------------------------------------------------
  // Recently viewed products (client-side only, by design)
  // ---------------------------------------------------------------------
  const RECENTLY_VIEWED_KEY = 'primebasket-recently-viewed';
  const detailCard = document.querySelector('.product-card--detail');

  const readRecentlyViewed = () => {
    try {
      const parsed = JSON.parse(localStorage.getItem(RECENTLY_VIEWED_KEY) || '[]');
      return Array.isArray(parsed) ? parsed : [];
    } catch (error) {
      return [];
    }
  };

  if (detailCard) {
    const productId = detailCard.getAttribute('data-recently-viewed-id');
    const productName = detailCard.getAttribute('data-product-name');

    if (productId && productName) {
      const img = detailCard.querySelector('.pd-frame img');
      const price = detailCard.querySelector('.price')?.textContent || '';
      const current = {
        id: productId,
        name: productName,
        image: img ? img.getAttribute('src') : '',
        price,
      };

      let viewed = readRecentlyViewed().filter((item) => item.id !== productId);
      viewed.unshift(current);
      viewed = viewed.slice(0, 6);
      try {
        localStorage.setItem(RECENTLY_VIEWED_KEY, JSON.stringify(viewed));
      } catch (error) {
        /* localStorage unavailable -- recently viewed just won't persist */
      }

      const others = viewed.filter((item) => item.id !== productId).slice(0, 4);
      const section = document.getElementById('recentlyViewedSection');
      const grid = document.getElementById('recentlyViewedGrid');

      if (section && grid && others.length) {
        grid.innerHTML = others
          .map(
            (item) => `
            <div class="col-lg-3 col-md-6">
              <a href="/products/${item.id}/" class="text-decoration-none text-reset">
                <div class="card product-card h-100 border-0 shadow-sm">
                  <div class="card-img-top"><img src="${item.image}" alt="${item.name}" /></div>
                  <div class="card-body">
                    <h6 class="fw-bold mb-1">${item.name}</h6>
                    <span class="price">${item.price}</span>
                  </div>
                </div>
              </a>
            </div>`
          )
          .join('');
        section.classList.remove('d-none');
      }
    }
  }

  // ---------------------------------------------------------------------
  // Product reviews
  // ---------------------------------------------------------------------
  const reviewForm = document.getElementById('reviewForm');
  const starInput = document.getElementById('starInput');
  const reviewRatingInput = document.getElementById('reviewRating');
  const reviewComment = document.getElementById('reviewComment');
  const reviewMessage = document.getElementById('reviewMessage');
  const reviewsList = document.getElementById('reviewsList');

  if (starInput && reviewRatingInput) {
    const stars = Array.from(starInput.querySelectorAll('i'));
    const paintStars = (value) => {
      stars.forEach((star) => {
        const starValue = Number(star.getAttribute('data-value'));
        star.classList.toggle('bi-star-fill', starValue <= value);
        star.classList.toggle('bi-star', starValue > value);
      });
    };
    stars.forEach((star) => {
      star.addEventListener('click', () => {
        const value = Number(star.getAttribute('data-value'));
        reviewRatingInput.value = value;
        paintStars(value);
      });
    });
  }

  if (reviewForm && reviewRatingInput && reviewComment && reviewMessage) {
    reviewForm.addEventListener('submit', (event) => {
      event.preventDefault();
      const productId = reviewForm.getAttribute('data-product-id');
      const rating = Number(reviewRatingInput.value || 0);
      const comment = reviewComment.value.trim();

      if (!rating) {
        reviewMessage.textContent = 'Please select a star rating.';
        reviewMessage.className = 'form-text text-danger mt-2';
        return;
      }
      if (comment.length < 5) {
        reviewMessage.textContent = 'Please write a few words about the product.';
        reviewMessage.className = 'form-text text-danger mt-2';
        return;
      }

      fetch(`/products/${productId}/reviews/add/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCsrfToken(),
        },
        body: JSON.stringify({ product_id: productId, rating, comment }),
      })
        .then((response) => response.json().then((data) => ({ ok: response.ok, data })))
        .then(({ ok, data }) => {
          if (ok && data.success) {
            reviewMessage.textContent = 'Thanks for your review!';
            reviewMessage.className = 'form-text text-success mt-2';
            reviewForm.reset();
            reviewRatingInput.value = '0';
            if (starInput) {
              starInput.querySelectorAll('i').forEach((star) => {
                star.classList.remove('bi-star-fill');
                star.classList.add('bi-star');
              });
            }
            if (reviewsList) {
              const emptyMessage = reviewsList.querySelector('p');
              if (emptyMessage) emptyMessage.remove();
              const stars = '★'.repeat(rating) + '☆'.repeat(5 - rating);
              const card = document.createElement('div');
              card.className = 'review-card';
              card.innerHTML = `<div class="d-flex justify-content-between align-items-center mb-2"><strong>You</strong><div class="rating-stars small">${stars}</div></div><p class="text-muted mb-0"></p>`;
              card.querySelector('p').textContent = comment;
              reviewsList.prepend(card);
            }
          } else {
            reviewMessage.textContent = data.error || 'Unable to submit your review.';
            reviewMessage.className = 'form-text text-danger mt-2';
          }
        })
        .catch(() => {
          reviewMessage.textContent = 'Unable to reach the server. Please try again.';
          reviewMessage.className = 'form-text text-danger mt-2';
        });
    });
  }

  // ---------------------------------------------------------------------
  // Contact form
  // ---------------------------------------------------------------------
  const contactForm = document.getElementById('contactForm');
  const contactStatus = document.getElementById('contactMessageStatus');

  if (contactForm && contactStatus) {
    contactForm.addEventListener('submit', (event) => {
      event.preventDefault();
      const name = document.getElementById('contactName').value.trim();
      const email = document.getElementById('contactEmail').value.trim();
      const subject = document.getElementById('contactSubject').value.trim();
      const message = document.getElementById('contactMessage').value.trim();

      fetch('/contact/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCsrfToken(),
        },
        body: JSON.stringify({ name, email, subject, message }),
      })
        .then((response) => response.json().then((data) => ({ ok: response.ok, data })))
        .then(({ ok, data }) => {
          if (ok && data.success) {
            contactStatus.textContent = 'Thanks for reaching out! We will get back to you soon.';
            contactStatus.className = 'form-text text-success mt-2';
            contactForm.reset();
          } else {
            contactStatus.textContent = data.error || 'Unable to send your message.';
            contactStatus.className = 'form-text text-danger mt-2';
          }
        })
        .catch(() => {
          contactStatus.textContent = 'Unable to reach the server. Please try again.';
          contactStatus.className = 'form-text text-danger mt-2';
        });
    });
  }

  // ---------------------------------------------------------------------
  // Change password (profile page)
  // ---------------------------------------------------------------------
  const changePasswordForm = document.getElementById('changePasswordForm');
  const changePasswordMessage = document.getElementById('changePasswordMessage');

  if (changePasswordForm && changePasswordMessage) {
    changePasswordForm.addEventListener('submit', (event) => {
      event.preventDefault();
      const currentPassword = document.getElementById('currentPassword').value;
      const newPassword = document.getElementById('newPassword').value;
      const confirmNewPassword = document.getElementById('confirmNewPassword').value;

      if (newPassword.length < 6) {
        changePasswordMessage.textContent = 'New password must be at least 6 characters.';
        changePasswordMessage.className = 'form-text text-danger mt-2';
        return;
      }
      if (newPassword !== confirmNewPassword) {
        changePasswordMessage.textContent = 'New passwords do not match.';
        changePasswordMessage.className = 'form-text text-danger mt-2';
        return;
      }

      fetch('/profile/change-password/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCsrfToken(),
        },
        body: JSON.stringify({ current_password: currentPassword, new_password: newPassword }),
      })
        .then((response) => response.json().then((data) => ({ ok: response.ok, data })))
        .then(({ ok, data }) => {
          if (ok && data.success) {
            changePasswordMessage.textContent = 'Password updated successfully.';
            changePasswordMessage.className = 'form-text text-success mt-2';
            changePasswordForm.reset();
          } else {
            changePasswordMessage.textContent = data.error || 'Unable to update password.';
            changePasswordMessage.className = 'form-text text-danger mt-2';
          }
        })
        .catch(() => {
          changePasswordMessage.textContent = 'Unable to reach the server. Please try again.';
          changePasswordMessage.className = 'form-text text-danger mt-2';
        });
    });
  }

  // ---------------------------------------------------------------------
  // Address management (profile page)
  // ---------------------------------------------------------------------
  const showAddAddressBtn = document.getElementById('showAddAddress');
  const addAddressForm = document.getElementById('addAddressForm');
  const addAddressMessage = document.getElementById('addAddressMessage');
  const addressList = document.getElementById('addressList');

  if (showAddAddressBtn && addAddressForm) {
    showAddAddressBtn.addEventListener('click', () => {
      addAddressForm.classList.toggle('d-none');
    });
  }

  if (addAddressForm && addAddressMessage && addressList) {
    addAddressForm.addEventListener('submit', (event) => {
      event.preventDefault();
      const payload = {
        full_name: document.getElementById('newAddrFullName').value.trim(),
        phone: document.getElementById('newAddrPhone').value.trim(),
        line1: document.getElementById('newAddrLine1').value.trim(),
        city: document.getElementById('newAddrCity').value.trim(),
        state: document.getElementById('newAddrState').value.trim(),
        postal_code: document.getElementById('newAddrPostalCode').value.trim(),
      };

      fetch('/profile/addresses/add/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCsrfToken(),
        },
        body: JSON.stringify(payload),
      })
        .then((response) => response.json().then((data) => ({ ok: response.ok, data })))
        .then(({ ok, data }) => {
          if (ok && data.success) {
            const emptyMessage = document.getElementById('noAddressesMessage');
            if (emptyMessage) emptyMessage.remove();
            const addr = data.address;
            const row = document.createElement('div');
            row.className = 'border rounded-4 p-3 d-flex justify-content-between align-items-start gap-2';
            row.innerHTML = `<div><strong></strong> &middot; <span class="phone"></span><br /><span class="text-muted small addr-line"></span></div><button type="button" class="btn btn-sm btn-outline-danger delete-address-btn" data-address-id="${addr.id}"><i class="bi bi-trash"></i></button>`;
            row.querySelector('strong').textContent = addr.full_name;
            row.querySelector('.phone').textContent = addr.phone;
            row.querySelector('.addr-line').textContent = `${addr.line1}, ${addr.city}, ${addr.state} ${addr.postal_code}`;
            addressList.appendChild(row);
            addAddressForm.reset();
            addAddressForm.classList.add('d-none');
            addAddressMessage.textContent = '';
          } else {
            addAddressMessage.textContent = data.error || 'Unable to save this address.';
            addAddressMessage.className = 'form-text text-danger';
          }
        })
        .catch(() => {
          addAddressMessage.textContent = 'Unable to reach the server. Please try again.';
          addAddressMessage.className = 'form-text text-danger';
        });
    });
  }

  if (addressList) {
    addressList.addEventListener('click', (event) => {
      const button = event.target.closest('.delete-address-btn');
      if (!button) return;
      const addressId = button.getAttribute('data-address-id');

      fetch(`/profile/addresses/${addressId}/delete/`, {
        method: 'POST',
        headers: { 'X-CSRFToken': getCsrfToken() },
      })
        .then((response) => response.json().then((data) => ({ ok: response.ok, data })))
        .then(({ ok, data }) => {
          if (ok && data.success) {
            button.closest('div.border').remove();
          }
        });
    });
  }

  // ---------------------------------------------------------------------
  // Checkout page
  // ---------------------------------------------------------------------
  const checkoutForm = document.getElementById('checkoutForm');

  const renderCheckoutSummary = (coupon) => {
    const checkoutItemsList = document.getElementById('checkoutItemsList');
    const checkoutEmpty = document.getElementById('checkoutEmpty');
    if (!checkoutForm || !checkoutItemsList) return;

    if (!cartItems.length) {
      checkoutForm.classList.add('d-none');
      if (checkoutEmpty) checkoutEmpty.classList.remove('d-none');
      return;
    }
    checkoutForm.classList.remove('d-none');
    if (checkoutEmpty) checkoutEmpty.classList.add('d-none');

    checkoutItemsList.innerHTML = cartItems
      .map(
        (item) => `
        <div class="d-flex justify-content-between align-items-center small">
          <span>${item.name} <span class="text-muted">x${item.quantity}</span></span>
          <span>${formatCurrency(Number(item.price || 0) * Number(item.quantity || 1))}</span>
        </div>`
      )
      .join('');

    fetch('/checkout/summary/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCsrfToken(),
      },
      body: JSON.stringify({ coupon_code: coupon || '' }),
    })
      .then((response) => response.json().then((data) => ({ ok: response.ok, data })))
      .then(({ ok, data }) => {
        const couponMessage = document.getElementById('couponMessage');
        if (!ok || !data.success) {
          if (coupon && couponMessage) {
            couponMessage.textContent = data.error || 'Invalid coupon code.';
            couponMessage.className = 'form-text text-danger mb-2';
          }
          return;
        }

        document.getElementById('checkoutSubtotal').textContent = data.subtotal.toFixed(2);
        document.getElementById('checkoutDelivery').textContent = data.delivery_charge.toFixed(2);
        document.getElementById('checkoutDeliveryLabel').textContent = data.delivery_charge > 0 ? `$${data.delivery_charge.toFixed(2)}` : 'Free';
        document.getElementById('checkoutTax').textContent = data.tax.toFixed(2);
        document.getElementById('checkoutTotal').textContent = data.total.toFixed(2);

        const discountRow = document.getElementById('checkoutDiscountRow');
        if (data.discount > 0) {
          document.getElementById('checkoutDiscount').textContent = data.discount.toFixed(2);
          if (discountRow) discountRow.classList.remove('d-none');
        } else if (discountRow) {
          discountRow.classList.add('d-none');
        }

        if (coupon && couponMessage) {
          couponMessage.textContent = data.coupon_code ? `Coupon "${data.coupon_code}" applied!` : '';
          couponMessage.className = 'form-text text-success mb-2';
        }

        checkoutForm.dataset.appliedCoupon = data.coupon_code || '';
      });
  };

  if (checkoutForm) {
    const applyCouponBtn = document.getElementById('applyCouponBtn');
    const couponCodeInput = document.getElementById('couponCodeInput');

    if (applyCouponBtn && couponCodeInput) {
      applyCouponBtn.addEventListener('click', () => {
        renderCheckoutSummary(couponCodeInput.value.trim());
      });
    }

    document.querySelectorAll('input[name="addressChoice"]').forEach((radio) => {
      radio.addEventListener('change', () => {
        const newAddressForm = document.getElementById('newAddressForm');
        if (!newAddressForm) return;
        newAddressForm.classList.toggle('d-none', radio.value !== 'new');
      });
    });

    checkoutForm.addEventListener('submit', (event) => {
      event.preventDefault();
      const placeOrderBtn = document.getElementById('placeOrderBtn');
      const placeOrderMessage = document.getElementById('placeOrderMessage');
      const selectedAddress = document.querySelector('input[name="addressChoice"]:checked');
      const paymentMethod = document.querySelector('input[name="paymentMethod"]:checked')?.value || 'cod';
      const couponCodeInput = document.getElementById('couponCodeInput');

      let address;
      if (selectedAddress && selectedAddress.value !== 'new') {
        address = {
          full_name: selectedAddress.getAttribute('data-full-name'),
          phone: selectedAddress.getAttribute('data-phone'),
          line1: selectedAddress.getAttribute('data-line1'),
          city: selectedAddress.getAttribute('data-city'),
          state: selectedAddress.getAttribute('data-state'),
          postal_code: selectedAddress.getAttribute('data-postal-code'),
        };
      } else {
        address = {
          full_name: document.getElementById('addrFullName').value.trim(),
          phone: document.getElementById('addrPhone').value.trim(),
          line1: document.getElementById('addrLine1').value.trim(),
          city: document.getElementById('addrCity').value.trim(),
          state: document.getElementById('addrState').value.trim(),
          postal_code: document.getElementById('addrPostalCode').value.trim(),
        };

        const saveNewAddress = document.getElementById('saveNewAddress');
        if (saveNewAddress && saveNewAddress.checked && Object.values(address).every((value) => value)) {
          fetch('/profile/addresses/add/', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'X-CSRFToken': getCsrfToken(),
            },
            body: JSON.stringify(address),
          }).catch(() => {});
        }
      }

      if (!address.full_name || !address.phone || !address.line1 || !address.city || !address.state || !address.postal_code) {
        if (placeOrderMessage) {
          placeOrderMessage.textContent = 'Please provide a complete delivery address.';
          placeOrderMessage.className = 'form-text text-danger mt-2';
        }
        return;
      }

      if (placeOrderBtn) placeOrderBtn.disabled = true;

      fetch('/checkout/place-order/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCsrfToken(),
        },
        body: JSON.stringify({
          address,
          payment_method: paymentMethod,
          coupon_code: checkoutForm.dataset.appliedCoupon || (couponCodeInput ? couponCodeInput.value.trim() : ''),
        }),
      })
        .then((response) => response.json().then((data) => ({ ok: response.ok, data })))
        .then(({ ok, data }) => {
          if (ok && data.success) {
            window.location.href = data.redirect;
          } else {
            if (placeOrderBtn) placeOrderBtn.disabled = false;
            if (placeOrderMessage) {
              placeOrderMessage.textContent = data.error || 'Unable to place your order. Please try again.';
              placeOrderMessage.className = 'form-text text-danger mt-2';
            }
          }
        })
        .catch(() => {
          if (placeOrderBtn) placeOrderBtn.disabled = false;
          if (placeOrderMessage) {
            placeOrderMessage.textContent = 'Unable to reach the server. Please try again.';
            placeOrderMessage.className = 'form-text text-danger mt-2';
          }
        });
    });
  }

  // ---------------------------------------------------------------------
  // Cancel order (order detail page)
  // ---------------------------------------------------------------------
  const cancelOrderBtn = document.getElementById('cancelOrderBtn');
  const cancelOrderMessage = document.getElementById('cancelOrderMessage');

  if (cancelOrderBtn && cancelOrderMessage) {
    cancelOrderBtn.addEventListener('click', () => {
      if (!window.confirm('Cancel this order? This cannot be undone.')) return;

      const orderId = cancelOrderBtn.getAttribute('data-order-id');
      cancelOrderBtn.disabled = true;

      fetch(`/orders/${orderId}/cancel/`, {
        method: 'POST',
        headers: { 'X-CSRFToken': getCsrfToken() },
      })
        .then((response) => response.json().then((data) => ({ ok: response.ok, data })))
        .then(({ ok, data }) => {
          if (ok && data.success) {
            window.location.reload();
          } else {
            cancelOrderBtn.disabled = false;
            cancelOrderMessage.textContent = data.error || 'Unable to cancel this order.';
            cancelOrderMessage.className = 'form-text text-danger mt-2';
          }
        })
        .catch(() => {
          cancelOrderBtn.disabled = false;
          cancelOrderMessage.textContent = 'Unable to reach the server. Please try again.';
          cancelOrderMessage.className = 'form-text text-danger mt-2';
        });
    });
  }

  updateCounters();
  fetchWishlist().then(() => {
    updateCounters();
    syncWishlistButtons();
    renderWishlistPage();
  });
  fetchCart().then(() => {
    updateCounters();
    renderCartPage();
    renderCheckoutSummary();
  });

  window.addEventListener('scroll', () => {
    updateNavbar();
    updateActiveLink();
    updateScrollTop();
  });

  window.addEventListener('load', () => {
    updateNavbar();
    updateActiveLink();
    updateScrollTop();
    updateCounters();
    syncWishlistButtons();
  });
});
