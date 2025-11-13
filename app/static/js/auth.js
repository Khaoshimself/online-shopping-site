/**
 * app/static/js/auth.js
 *
 * This file "hijacks" the default login AND signup forms.
 * It uses fetch() to submit the data in the background, preventing page reloads.
 */

// Wait for the full page to load before running our code
document.addEventListener("DOMContentLoaded", () => {
    // Find the forms by the IDs we will add in the HTML
    const loginForm = document.getElementById("login-form");
    const signupForm = document.getElementById("signup-form");
  
    // Add listener for the login form
    if (loginForm) {
      loginForm.addEventListener("submit", (e) =>
        handleAuthFormSubmit(e, "/login")
      );
    }
  
    // Add listener for the signup form
    if (signupForm) {
      signupForm.addEventListener("submit", (e) =>
        handleAuthFormSubmit(e, "/signup")
      );
    }
  });
  
  /**
   * A single, reusable function to handle all our auth forms.
   * @param {Event} event - The form's "submit" event.
   * @param {string} endpoint - The Flask route to send the data to (e.g., "/login").
   */
  async function handleAuthFormSubmit(event, endpoint) {
    event.preventDefault(); // Stop the browser's default page reload!
  
    const form = event.currentTarget;
    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries()); // Convert form data to a plain object
  
    const submitButton = form.querySelector('input[type="submit"]');
    const originalButtonHtml = submitButton.innerHTML;
  
    // Show a loading state on the button
    submitButton.innerHTML = `
      <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
      Loading...
    `;
    submitButton.disabled = true;
  
    // Clear any old error messages
    const messageEl = document.getElementById("auth-message");
    if (messageEl) {
      messageEl.textContent = "";
      messageEl.classList.add("d-none"); // Hide it
    }
  
    try {
      // Use fetch() to talk to the backend
      const response = await fetch(endpoint, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Accept": "application/json", // Tell Flask we want JSON back
        },
        body: JSON.stringify(data), // Send the form data as a JSON string
      });
  
      const result = await response.json(); // Get the JSON response from Flask
  
      if (!response.ok) {
        // If the server sent an error (like 400 or 401)
        showAuthMessage(result.message || "An error occurred.", "danger");
      } else {
        // Success!
        showAuthMessage(result.message || "Success!", "success");
  
        // If the server tells us to redirect, do it after a short delay
        if (result.redirect) {
          setTimeout(() => {
            window.location.href = result.redirect;
          }, 1000); // 1 second delay to read the message
        }
      }
    } catch (error) {
      console.error("Auth form error:", error);
      showAuthMessage("An unexpected network error occurred.", "danger");
    } finally {
      // Restore the button to its original state
      submitButton.innerHTML = originalButtonHtml;
      submitButton.disabled = false;
    }
  }
  
  /**
   * Shows a message in the auth form's message area.
   * @param {string} message - The message to display.
   * @param {'success'|'danger'} type - The Bootstrap alert type.
   */
  function showAuthMessage(message, type = "success") {
    const messageEl = document.getElementById("auth-message");
    if (messageEl) {
      messageEl.textContent = message;
      // Use Bootstrap alert classes
      messageEl.className = `alert alert-${type} mt-3`;
    }
  }