// this is an admin-only page for item creation

// wait for page to load
document.addEventListener('DOMContentLoaded', () =>
{
    const form = document.getElementById('admin-item-form');
    const result = document.getElementById('admin-item-result');
    const listContainer = document.getElementById('admin-items-list'); // fetch the list container from HTML -- will hold our items
    const submitButton = document.getElementById('admin-item-submit');
    let editId = null; // track if we are editing an item
    

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
            // dummy printing for now
            listContainer.innerHTML = '';
            // FUNCTION CALL HERE
        }
        catch(err)
        {
            listContainer.innerHTML = `<div class="alert alert-danger">Network error</div>`;
            console.error(err);
        }
    }

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
            const resp = await fetch('/admin/items/add',
            {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'same-origin',
                body: JSON.stringify({name, description, price_cents, category, stock, image_urls, tags})
            });
            const json = await resp.json();
            if (!resp.ok)
            {
                result.innerHTML = `<div class="alert alert-danger">${json.error || json.message || 'Failed to add item'}</div>`;
                return;
            }

            result.innerHTML = `<div class="alert alert-success">Item created${json.inserted_id ? ': ' + json.inserted_id : ''}</div>`;
            form.reset();
        } 
        catch (err)
        {
            result.innerHTML = `<div class="alert alert-danger">Network error</div>`;
            console.error(err);
        }
    });
});