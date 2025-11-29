// this is an admin-only page for managing discounts on items

document.addEventListener('DOMContentLoaded', () =>
{
    const form = document.getElementById('discount-form');
    const result = document.getElementById('discount-result');
    const listContainer = document.getElementById('discount-list-container');
    
    let submitButton = document.getElementById('discount-submit-button');
    if (!submitButton && form) submitButton = form.querySelector('input[type="submit"]');
    let editId = null; // Track if we're editing an existing discount
    let discounts = []; // Store current discounts

    // Load existing discounts and display them
    async function fetchAndDisplayDiscounts()
    {
        listContainer.textContent = 'Loading discounts...';
        try
        {
            const response = await fetch('/admin/discounts/list', {credentials : 'same-origin'});
            const data = await response.json();
            if(!response.ok)
            {
                listContainer.innerHTML= `<div class="alert alert-danger">${data.error || 'Failed to load discounts.'}</div>`;
                return;
            }
            discounts = data.discounts || [];
            renderDiscounts(discounts);
        }
        catch (err)
        {
            listContainer.innerHTML = `<div class="alert alert-danger">Network error: ${err.message}</div>`;
            console.error(err);
        } // end fetchAndisplayDiscounts()
    }

    
    function renderDiscounts(discountsList)
    {
        if(!discountsList || discountsList.length === 0)
        {
            listContainer.innerHTML = '<div class="alert alert-info">No discounts found.</div>';
            return;
        }

        const tableRows = discountsList.map(discount =>
        {
            // no images, so just return text
            return `
                <tr>
                    <td>${discount.code}</td>
                    <td>${discount.percentage}%</td>
                    <td>
                        <button class="btn btn-sm btn-primary edit-discount-btn" data-id="${discount._id}">Edit</button>
                        <button class="btn btn-sm btn-danger delete-discount-btn" data-id="${discount._id}">Delete</button>
                    </td>
                </tr>
            `;
        }).join('');

        // now put the rows into the list container
        listContainer.innerHTML = `
            <table class="table table-striped">
                <thead>
                    <tr>
                        <th>Code</th>
                        <th>Percentage</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    ${tableRows}
                </tbody>
            </table>
        `;

        // Attach event listeners for edit and delete buttons
        listContainer.querySelectorAll('.edit-discount-btn').forEach(button =>
        {
            button.addEventListener('click', () =>
            {
                const discountId = button.getAttribute('data-id');
                const discount = discounts.find(d => d._id === discountId);
                if(discount)
                {   
                    startEditDiscount(discount);
                }
            });
        });

        // delete...
        listContainer.querySelectorAll('.delete-discount-btn').forEach(button =>
        {
            button.addEventListener('click', async (ev) =>
            {
                const discountId = button.getAttribute('data-id');
                const discountCode = discounts.find(d => d._id === discountId)?.code || 'this discount';
                if(confirm(`Are you sure you want to delete discount "${discountCode}"? This action cannot be undone.`))
                {
                    try
                    {
                        const response = await fetch(`/admin/discounts/delete/${discountId}`,
                        {
                            method: 'POST',
                            credentials: 'same-origin'
                        });
                        const data = await response.json();
                        if(!response.ok)
                        {
                            alert(data.error || 'Failed to delete discount.');
                            return;
                        }
                        // remove discount from array and re-render
                        discounts = discounts.filter(d => d._id !== discountId);
                        fetchAndDisplayDiscounts();
                    }
                    catch(err)
                    {
                        alert(`Network error: ${err.message}`);
                        console.error(err);
                    }
                }
            });
        });
    } // end renderDiscounts

    function startEditDiscount(discount)
    {
        editId = discount._id;
        document.getElementById('discount-code').value = discount.code;
        document.getElementById('discount-percentage').value = discount.percentage;

        submitButton.value = 'Update Discount';
        result.innerHTML = '';

        // cancel edit button
        if(!document.getElementById('cancel-edit-button'))
        {
            const cancelButton = document.createElement('button');
            cancelButton.type = 'button';
            cancelButton.id = 'cancel-edit-button';
            cancelButton.className = 'btn btn-secondary ml-2';
            cancelButton.textContent = 'Cancel Edit';
            cancelButton.addEventListener('click', stopEditDiscount); // call stopEditDiscount on click
            submitButton.insertAdjacentElement('afterend', cancelButton); // button right next to submit
        }

        // scroll to form
        form.scrollIntoView({behavior: 'smooth', block: 'start'});
    } // end startEditDiscount

    function stopEditDiscount()
    {
        editId = null;
        form.reset();
        submitButton.value = 'Add Discount';
        const cancelButton = document.getElementById('cancel-edit-button');
        if(cancelButton) // remove the existing cancel button
        {
            cancelButton.remove();
        }
        result.innerHTML = '';
    } // end stopEditDiscount

    form.addEventListener('submit', async (ev) =>
    {
        ev.preventDefault();
        const code = document.getElementById('discount-code').value.trim();
        const percentage = parseFloat(document.getElementById('discount-percentage').value);
        if(!code || isNaN(percentage) || percentage <= 0 || percentage > 100)
        {
            result.innerHTML = '<div class="alert alert-danger">Please provide a valid discount code and percentage (1-100).</div>';
            return;
        }

        // Prepare data
        try
        {
            let resp, json;
            if(editId)
            {
                // get the fields we're changing
                const update_fields = {code, percentage};
                resp = await fetch('/admin/discounts/edit/',
                {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    credentials: 'same-origin',
                    body: JSON.stringify({id: editId, update_fields})
                });
                json = await resp.json();
                if(!resp.ok)
                {
                    result.innerHTML = `<div class="alert alert-danger">${json.error || 'Failed to update discount.'}</div>`;
                    return;
                }
                result.innerHTML = `<div class="alert alert-success">Discount updated successfully.</div>`;
                stopEditDiscount(); // exit edit mode
                fetchAndDisplayDiscounts(); // refresh items
            }
            else
            {
                resp = await fetch('/admin/discounts/add/',
                {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    credentials: 'same-origin',
                    body: JSON.stringify({code, percentage})
                });

                json = await resp.json();
                if(!resp.ok)
                {
                    result.innerHTML = `<div class="alert alert-danger">${json.error || 'Failed to add discount.'}</div>`;
                    return;
                }
                result.innerHTML = `<div class="alert alert-success">Discount added successfully.</div>`;
                form.reset();
                fetchAndDisplayDiscounts(); // refresh items
            }
        }
        catch(err)
        {
            result.innerHTML = `<div class="alert alert-danger">Network error: ${err.message}</div>`;
            console.error(err);
        }
    });

    // Initial load
    fetchAndDisplayDiscounts();
});