/**
 * app/static/js/cart.js
 *
 * This file handles all shopping cart interactions:
 * 1. Listening for "Add to Cart" clicks on the main page.
 * 2. Showing a "Toast" notification.
 * 3. Updating the cart count badge in the navbar.
 * 4. Dynamically building the table on the cart page.
 * 5. Applying discount codes on the cart page.
 */

// Wait for the full page to load before running our code
document.addEventListener("DOMContentLoaded", () => {
  // --- Global Toast Setup ---
  // Find the toast element (we will add this to base.html)
  const toastEl = document.getElementById("notification-toast");
  // Create a reusable Bootstrap Toast instance
  const notificationToast = toastEl ? new bootstrap.Toast(toastEl, { delay: 3000 }) : null;

  // --- Global "Add to Cart" Listener ---
  // Instead of adding a listener to each button, we listen on the whole page.
  // This is more efficient and works even if buttons are added dynamically.
  document.body.addEventListener("click", (event) => {
    // Check if the clicked element has the class 'add-to-cart-btn'
    const button = event.target.closest(".add-to-cart-btn");
    if (button) {
      event.preventDefault(); // Stop any default button behavior
      handleAddToCartClick(button, notificationToast);
    }
  });

  // --- Cart Page Specific Logic ---
  // We only run this code if we are on the cart page.
  const cartTableBody = document.getElementById("cart-tbody");
  if (cartTableBody) {
    // We are on the cart page, so load the cart contents right away.
    loadCartTable(cartTableBody);

    // Listen for clicks on the dynamic buttons (update, remove)
    cartTableBody.addEventListener("click", (event) => {
      const target = event.target.closest("button"); // Get the button that was clicked
      if (!target) return;

      const action = target.dataset.action;
      const productId = target.dataset.productId;

      if (action === "update-quantity") {
        // Find the input field in the same table row
        const newQuantity = parseInt(
          target.closest("tr").querySelector(".cart-quantity-input").value
        );
        updateCartItem(productId, newQuantity, cartTableBody, notificationToast);
      } else if (action === "remove-item") {
        removeCartItem(productId, cartTableBody);
      }
    });
  }

  const applyDiscountBtn = document.getElementById("apply-discount-btn");
  if (applyDiscountBtn) {
    const codeInput = document.getElementById("discount-code-input");
    const messageEl = document.getElementById("discount-message");

    const subtotalEl = document.getElementById("cart-subtotal");
    const discountEl = document.getElementById("cart-discount");
    const taxEl = document.getElementById("cart-tax");
    const totalEl = document.getElementById("cart-total");

    applyDiscountBtn.addEventListener("click", async () => {
      const code = codeInput.value.trim();

      if (!code) {
        messageEl.textContent = "Please enter a discount code.";
        messageEl.className = "d-block mt-2 text-danger";
        return;
      }

      try {
        const res = await fetch("/api/cart/apply-discount", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ code }),
        });

        const data = await res.json();

        if (!data.ok) {
          messageEl.textContent = data.message || "Could not apply code.";
          messageEl.className = "d-block mt-2 text-danger";
          if (discountEl) {
            discountEl.textContent = "- $0.00";
          }
          return;
        }

        const cart = data.cart;

        if (subtotalEl) {
          subtotalEl.textContent = `$${(cart.subtotal_cents / 100).toFixed(2)}`;
        }
        if (discountEl) {
          discountEl.textContent = `- $${(cart.discount_cents / 100).toFixed(2)}`;
        }
        if (taxEl) {
          taxEl.textContent = `$${(cart.tax_cents / 100).toFixed(2)}`;
        }
        if (totalEl) {
          totalEl.textContent = `$${(cart.total_cents / 100).toFixed(2)}`;
        }

        messageEl.textContent = data.message;
        messageEl.className = "d-block mt-2 text-success";
      } catch (err) {
        console.error("Error applying discount:", err);
        messageEl.textContent = "Error applying code. Please try again.";
        messageEl.className = "d-block mt-2 text-danger";
      }
    });
  }

  // --- Initial Cart Count Load ---
  // On *every* page load (shop, cart, login, etc.),
  // we need to ask the server how many items are in the cart.
  updateCartCountBadge();
});

  // --- Checkout Logic (cart page only) ---
  const checkoutBtn = document.getElementById("checkout-btn");
  if (checkoutBtn) {
    checkoutBtn.addEventListener("click", async () => {
      checkoutBtn.disabled = true;
      checkoutBtn.textContent = "Placing order...";

      try {
        const res = await fetch("/api/cart/checkout", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({}),  // nothing to send for now
        });

        const data = await res.json();

        if (!data.ok) {
          alert(data.message || "Could not place order.");
          return;
        }

        window.location.href = `/orders/${data.order_id}`;
      } catch (err) {
        console.error("Error during checkout:", err);
        alert("Error placing order. Please try again.");
      } finally {
        checkoutBtn.disabled = false;
        checkoutBtn.textContent = "Proceed to Checkout";
      }
    });
  }


/**
 * 1. Handles the "Add to Cart" button click
 */
async function handleAddToCartClick(button, toast) {
  const productId = button.dataset.productId; // Get product ID from 'data-product-id'
  const originalHtml = button.innerHTML; // Save the original text (e.g., "Add to Cart")

  // Show a loading spinner on the button
  button.innerHTML = `
      <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
    `;
  button.disabled = true;

  try {
    // This is the API call to our backend
    const response = await fetch("/api/cart/add", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ product_id: productId, quantity: 1 }),
    });

    const data = await response.json();
    if (!response.ok) throw new Error(data.message || "Could not add item.");

    // Show notification and update badge
    showNotification(toast, data.message || "Item added to cart!", "success");
    updateCartCountBadge(data.cart_item_count);
  } catch (error) {
    console.error("Error adding to cart:", error);
    showNotification(toast, error.message, "danger");
  } finally {
    // Restore the button to its original state
    button.innerHTML = originalHtml;
    button.disabled = false;
  }
}

/**
 * 2. Fetches cart data and builds the cart page table
 */
async function loadCartTable(cartTableBody) {
  // Show a loading spinner in the table
  cartTableBody.innerHTML = `<tr><td colspan="5" class="text-center p-4">
      <div class="spinner-border text-danger" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="mt-2 mb-0">Loading your cart...</p>
    </td></tr>`;

  try {
    // Get the cart data from API
    const response = await fetch("/api/cart");
    const data = await response.json();

    if (!response.ok) {
      throw new Error("Could not load cart.");
    }

    if (!data.items || data.items.length === 0) {
      // Show empty cart message
      cartTableBody.innerHTML = `<tr><td colspan="5" class="text-center p-4">Your cart is empty.</td></tr>`;
    } else {
      // Build the table rows from the data
      cartTableBody.innerHTML = data.items
        .map(
          (item) => `
          <tr>
            <td>
              <div class="d-flex align-items-center">
                <img src="${item.image_url || "https://placehold.co/60x60/EFEFEF/333333?text=Item"}" alt="${item.name}" class="img-thumbnail me-3" style="width: 60px;">
                <div>
                  <strong class="d-block">${item.name}</strong>
                  <small class="text-muted">SKU: ${item.product_id}</small>
                </div>
              </div>
            </td>
            <td class="text-center" style="min-width: 150px;">
              <div class="input-group input-group-sm" style="width: 150px; margin: auto;">
                <input type="number" class="form-control cart-quantity-input" value="${item.quantity}" min="1" aria-label="Quantity">
                <button class="btn btn-outline-primary" type="button" data-action="update-quantity" data-product-id="${item.product_id}">
                  <i class="bi bi-check-lg"></i>
                </button>
              </div>
            </td>
            <td class="text-end">$${(item.price_cents / 100).toFixed(2)}</td>
            <td class="text-end fw-bold">$${(item.total_price_cents / 100).toFixed(2)}</td>
            <td class="text-center">
              <button class="btn btn-outline-danger btn-sm" data-action="remove-item" data-product-id="${item.product_id}">
                <i class="bi bi-trash-fill"></i>
              </button>
            </td>
          </tr>
        `
        )
        .join("");
    }

    // Update the total fields (including discount if present)
    const subtotal = (data.subtotal_cents || 0) / 100;
    const discount = (data.discount_cents || 0) / 100;
    const tax = (data.tax_cents || 0) / 100;
    const total = (data.total_cents || 0) / 100;

    const subtotalEl = document.getElementById("cart-subtotal");
    const discountEl = document.getElementById("cart-discount");
    const taxEl = document.getElementById("cart-tax");
    const totalEl = document.getElementById("cart-total");

    if (subtotalEl) subtotalEl.textContent = `$${subtotal.toFixed(2)}`;
    if (discountEl) discountEl.textContent = `- $${discount.toFixed(2)}`;
    if (taxEl) taxEl.textContent = `$${tax.toFixed(2)}`;
    if (totalEl) totalEl.textContent = `$${total.toFixed(2)}`;
  } catch (error) {
    console.error("Error loading cart:", error);
    cartTableBody.innerHTML = `<tr><td colspan="5" class="text-center text-danger p-4">Could not load cart. Please try again.</td></tr>`;
  }
}

/**
 * 3. Updates an item's quantity in the cart
 */
async function updateCartItem(productId, quantity, cartTableBody, toast) {
  try {
    const response = await fetch("/api/cart/update", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ product_id: productId, quantity: quantity }),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.message || "Could not update item");

    loadCartTable(cartTableBody); // Reload the table (will also recalc discount/tax/total)
    updateCartCountBadge(data.item_count); // Update badge
  } catch (error) {
    console.error("Error updating cart:", error);
    showNotification(toast, error.message, "danger");
  }
}

/**
 * 4. Removes an item from the cart
 */
async function removeCartItem(productId, cartTableBody) {
  try {
    const response = await fetch("/api/cart/remove", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ product_id: productId }),
    });
    if (!response.ok) throw new Error("Could not remove item");

    const data = await response.json();
    loadCartTable(cartTableBody); // Reload the table
    updateCartCountBadge(data.item_count); // Update badge
  } catch (error) {
    console.error("Error removing item:", error);
  }
}

/**
 * 5. Updates the cart count badge in the navbar
 */
async function updateCartCountBadge(count) {
  const cartCountElement = document.getElementById("cart-count");
  if (!cartCountElement) return;

  let totalItems = count;

  if (totalItems === undefined) {
    // If count wasn't provided, fetch it from the API
    try {
      const response = await fetch("/api/cart");
      if (!response.ok) return;
      const data = await response.json();
      totalItems = data.item_count || 0;
    } catch (error) {
      console.error("Error fetching cart count:", error);
      totalItems = 0;
    }
  }

  cartCountElement.textContent = totalItems;
  if (totalItems > 0) {
    cartCountElement.classList.remove("d-none"); // Show badge
  } else {
    cartCountElement.classList.add("d-none"); // Hide badge
  }
}

/**
 * 6. Shows a Bootstrap toast notification
 */
function showNotification(toast, message, type = "success") {
  if (!toast) {
    console.warn("Toast element not found. Cannot show notification.");
    return;
  }

  const toastBody = toast._element.querySelector(".toast-body");
  const toastHeader = toast._element.querySelector(".toast-header");

  toastBody.textContent = message;
  // change title
  toastTitle = toast._element.querySelector("#toast-title");
  toastTitle.textContent = type === "success" ? "Success" : "Error";
  // Set color based on success/error
  toastHeader.classList.remove("bg-success", "bg-danger", "text-white");
  toastHeader.classList.remove("toast-success", "toast-error");


  toastHeader.classList.add(
    type === "success" ? "bg-success" : "bg-danger",
    "text-white"
  );
  toastHeader.classList.add(type === "success" ? "toast-success" : "toast-error");
  

  toast.show();
}