// this is an admin-only page for item creation

// wait for page to load
document.addEventListener("DOMContentLoaded", () =>
    {
    const itemForm = document.getElementById("item-form");
    if (itemForm)
        {
        itemForm.addEventListener("submit", async (e) => 
            {
            e.preventDefault();

            const formData = new FormData(itemForm);
            const data = Object.fromEntries(formData.entries());
            try
            {
                const response = await fetch("/admin/create-item",
                {
                    method: "POST",
                    headers:
                    {
                        "Content-Type": "application/json",
                        "Accept": "application/json",
                    },
                    body: JSON.stringify(data), // Send the form data as a JSON string
                });
                const result = await response.json();
                const messageEl = document.getElementById("item-message");
                if (response.ok)
                {
                    messageEl.textContent = "Item created successfully!";
                    messageEl.classList.remove("d-none", "text-danger");
                    messageEl.classList.add("text-success");
                    itemForm.reset();
                }
                else
                {
                    messageEl.textContent = result.error || "An error occurred.";
                    messageEl.classList.remove("d-none", "text-success");
                    messageEl.classList.add("text-danger");
                }
            }
            catch (error)
            {
                console.error("Error creating item:", error);
            }
        });
    }
});