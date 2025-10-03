```markdown
# 🛒 Online Shopping Site (Phase 2 — Placeholder)

This project is a **Flask web app** that simulates a basic H-E-B–style online shopping site.  
Right now, it’s in **Phase 2** of development: placeholder templates to show the structure and page flow.  
Later phases will add CSS styling, JavaScript interactions, and a MongoDB backend.

---

## 📂 Project Structure
```

online-shopping-site/
├─ app/
│  ├─ **init**.py         # Flask app factory + routes
│  ├─ templates/          # HTML templates
│  │  ├─ base.html
│  │  ├─ shop/index.html
│  │  ├─ cart/cart.html
│  │  └─ auth/{login,signup}.html
│  └─ static/             # CSS / JS / images
│     ├─ css/main.css
│     ├─ js/{search.js,cart.js}
│     └─ img/
├─ run.py                 # Entry point
├─ requirements.txt       # Python dependencies
└─ README.md

````

---

## 🚀 Getting Started (for teammates)

Follow these steps to run the project on your machine.

### 1. Clone the repo
```bash
git clone https://github.com/<your-username>/online-shopping-site.git
cd online-shopping-site
````

### 2. Create a virtual environment (venv)

This keeps project packages separate from your system Python.

```bash
python3 -m venv .venv
```

### 3. Activate the venv

* On **Mac/Linux**:

  ```bash
  source .venv/bin/activate
  ```
* On **Windows (PowerShell)**:

  ```powershell
  .venv\Scripts\Activate.ps1
  ```

After activation, your prompt will look like:

```
(.venv) yourname@computer %
```

### 4. Install dependencies

This project uses `requirements.txt` to list all needed Python packages.

```bash
pip install -r requirements.txt
```

Dependencies include:

* **Flask** (the web framework)
* **python-dotenv** (load environment variables)

### 5. Run the Flask app

```bash
export FLASK_DEBUG=1        # (Mac/Linux)
# set FLASK_DEBUG=1         # (Windows PowerShell)

flask --app run run
```

You should see:

```
* Running on http://127.0.0.1:5000
```

---

## 🌐 Pages Available Now

* `/` → Catalog (placeholder product list)
* `/cart` → Cart (placeholder table)
* `/login` → Login form (placeholder)
* `/signup` → Signup form (placeholder)

Each page is just a simple stub so you can see the **flow**.
Later phases will add styling, search/sort, a real cart, and database connections.

---

## 🛠 Next Steps

* **Phase 2**: Add CSS/JS placeholders → style the navbar, catalog grid, cart demo.
* **Phase 3**: Connect MongoDB + Flask → real products, user accounts, carts.
* **Phase 4**: Core features → auth, cart logic, tax/discounts, checkout.

---

## 💡 Notes

* Don’t commit your `.venv/` folder — it’s in `.gitignore`.
* Always run `pip install -r requirements.txt` when new dependencies are added.
* If you mess up your venv, delete `.venv/` and recreate it with step 2.

---

👥 **IMPORTANT:** Everyone should clone this repo, set up a venv, install requirements, and confirm they can load the placeholder pages before diving into CSS/JS.