// this is an admin-only page for item creation

// wait for page to load
document.addEventListener('DOMContentLoaded', () =>
{
    const form = document.getElementById('admin-item-form');
    const result = document.getElementById('admin-item-result');
    const listContainer = document.getElementById('admin-items-list'); // fetch the list container from HTML -- will hold our items
    const submitButton = document.getElementById('admin-item-submit');
    let editId = null; // track if we are editing an item
    let items = []; // will hold fetched items
    

    async function fetchAndDisplayItems()
    {
        listContainer.textContent = 'Loading items...';
        try
        {
            const resp = await fetch('/admin/items/list', {credentials : 'same-origin'});
            const data = await resp.json();
            if(!resp.ok) // check for a bad response
            {
                listContainer.innerHTML = `<div class="alert alert-danger">${data.error || 'Failed to load items'}</div>`;
                return;
            }
            if(data.items.length === 0) // check if there are no items
            {
                listContainer.innerHTML = '<div class="alert alert-info">No items found.</div>';
                return;
            }
            // build the items list
            listContainer.innerHTML = '';
            renderItems(data.items);
        }
        catch(err)
        {
            listContainer.innerHTML = `<div class="alert alert-danger">Network error: ${err.message}</div>`;
            console.error(err);
        }
    } // end of fetchAndDisplayItems

    function renderItems(items)
    {
        if(!items || items.length === 0)
        {
            listContainer.innerHTML = '<div class="alert alert-info">No items found.</div>';
            return;
        }

        const tableRows = items.map(item => 
        {
            const imgHtml = (item.image_urls && item.image_urls.length > 0)
            ? (() => // if there IS an item image url, create an img element
                {
                    const img = document.createElement('img');
                    img.src = item.image_urls[0];
                    img.alt = item.name || '';
                    img.style.maxWidth = '50px';
                    img.style.maxHeight = '50px';
                    return img.outerHTML;
                })()
            : 'No Image'; // else, just say "No Image"

            // build an HTML table row for each item
            return `
                <tr data-item-id="${item._id}">
                    <td>${item._id}</td>
                    <td>${imgHtml}</td>
                    <td>${item.name || ''}</td>
                    <td>${(item.price_cents / 100).toFixed(2)}</td>
                    <td>${item.category || ''}</td>
                    <td>${item.stock || 0}</td>
                    <td>
                        <button class="btn btn-sm btn-primary admin-item-edit">Edit</button>
                        <button class="btn btn-sm btn-danger admin-item-delete">Delete</button>
                    </td>
                </tr>
            `;
        }).join('');

        // now put the rows into the list container
        listContainer.innerHTML = `
            <table class="table table-striped">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Image</th>
                        <th>Name</th>
                        <th>Price ($)</th>
                        <th>Category</th>
                        <th>Stock</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    ${tableRows}
                </tbody>
            </table>
        `;
        
        // add event listeners for edit and delete buttons
        // edit:
        listContainer.querySelectorAll('.admin-item-edit').forEach(button =>
        {
            button.addEventListener('click', (ev) =>
            {
                const itemId = button.closest('tr').getAttribute('data-item-id');
                const item = items.find(i => i._id === itemId);
                if(item)
                {
                    // call startEditMode function
                }
            });
        });

        // delete:
        listContainer.querySelectorAll('.admin-item-delete').forEach(button =>
        {
            button.addEventListener('click', async (ev) =>
            {
                const itemId = button.closest('tr').getAttribute('data-item-id');
                const itemName = items.find(i => i._id === itemId)?.name || 'this item';
                if(confirm(`Are you sure you want to delete "${itemName}"? This action cannot be undone.`))
                {
                    try
                    {
                        const resp = await fetch(`/admin/items/delete/${itemId}`,
                        {
                            method: 'POST',
                            credentials: 'same-origin'
                        });
                        const data = await resp.json();
                        if(!resp.ok)
                        {
                            alert(data.error || 'Failed to delete item');
                            return;
                        }
                        // remove item from local array and re-render
                        items = items.filter(i => i._id !== itemId);
                        fetchAndDisplayItems();
                    }
                    catch(err)
                    {
                        alert('Network error');
                        console.error(err);
                    }
                }
            });
        });
    } // end of renderItems

    function startEditMode(item)
    {
        editId = item._id;
        document.getElementById('name').value = item.name || '';
        document.getElementById('description').value = item.description || '';
        document.getElementById('price').value = (item.price_cents / 100).toFixed(2) || '0.00';
        document.getElementById('category').value = item.category || 'other';
        document.getElementById('stock').value = item.stock || '0';
        document.getElementById('image_urls').value = (item.image_urls || []).join(', ');
        document.getElementById('tags').value = (item.tags || []).join(', ');
        
        submitButton.textContent = 'Update Item';
        result.innerHTML = '';

        // cancel edit button
        if (!document.getElementById('cancel-edit-button'))
        {
            const cancelButton = document.createElement('button');
            cancelButton.type = 'button';
            cancelButton.id = 'cancel-edit-button';
            cancelButton.className = 'btn btn-secondary ml-2';
            cancelButton.textContent = 'Cancel Edit';
            cancelButton.addEventListener('click', stopEditMode); // call stopEditMode
            submitButton.insertAdjacentElement('afterend', cancelButton); // insert button after submit
        }

        // scroll up to the shiny new form!
        form.scrollIntoView({behavior: 'smooth', block: 'start'});
    } // end of startEditMode

    function stopEditMode()
    {
        editId = null;
        form.reset();
        submitButton.textContent = 'Create Item'; // reset button text
        const cancelButton = document.getElementById('cancel-edit-button');
        if (cancelButton) // remove the existing cancel button
        {
            cancelButton.remove();
        }
        result.innerHTML = '';
    } // end of stopEditMode

    form.addEventListener('submit', async (ev) =>
    {
        ev.preventDefault();
        result.textContent = '';
        const name = document.getElementById('name').value.trim();
        const description = document.getElementById('description').value.trim();
        const priceDollars = parseFloat(document.getElementById('price').value) || 0;
        const price_cents = Math.round(priceDollars * 100);
        const category = document.getElementById('category').value.trim() || 'other';
        const stock = parseInt(document.getElementById('stock').value || '0', 10);
        const image_urls = document.getElementById('image_urls').value.split(',').map(s => s.trim()).filter(Boolean);
        const tags = document.getElementById('tags').value.split(',').map(s => s.trim()).filter(Boolean);

        try
        {
            // const resp = await fetch('/admin/items/add',
            let resp, json; // define resp and json as variables; these will change based on add vs edit
            if(editId) // if we are editing an item...
            {
                // get the fields to update
                // this is in list form in case we want to update some stuff and not others
                const update_fields = {name, description, price_cents, category, stock, image_urls, tags};
                resp = await fetch('/admin/items/edit',
                {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    credentials: 'same-origin',
                    body: JSON.stringify({item_id: editId, update_fields})
                });
                json = await resp.json();
                if (!resp.ok)
                {
                    result.innerHTML = `<div class="alert alert-danger">${json.error || json.message || 'Failed to update item'}</div>`;
                    return;
                }
                result.innerHTML = `<div class="alert alert-success">Item updated</div>`;
                stopEditMode(); // exit edit mode
                fetchAndDisplayItems(); // refresh the items list
            }
            else
            {
                resp = await fetch('/admin/items/add',
                    {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    credentials: 'same-origin',
                    body: JSON.stringify({name, description, price_cents, category, stock, image_urls, tags})
                    });
                
                json = await resp.json();
                if (!resp.ok)
                {
                    result.innerHTML = `<div class="alert alert-danger">${json.error || json.message || 'Failed to add item'}</div>`;
                    return;
                }
                result.innerHTML = `<div class="alert alert-success">Item added with ID: ${json.item_id}</div>`;
                form.reset();
                fetchAndDisplayItems(); // refresh the items list
            }
        } 
        catch (err)
        {
            result.innerHTML = `<div class="alert alert-danger">Network error: ${err.message}</div>`;
            console.error(err);
        }
    });

    // initial fetch of items
    fetchAndDisplayItems();
});