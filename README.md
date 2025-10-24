# 🛒 Online Shopping Site (Phase 2 — Placeholder)
https://utsacloud-my.sharepoint.com/:w:/g/personal/bryan_torres-garcia_my_utsa_edu/EeGykJII-zlPm6uLzZnLg9oBVcyDlD_fphnozehupKBEJw?rtime=-PesXEkT3kg

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
```

---

## 🚀 Getting Started (for teammates)

Follow these steps to run the project on your machine.

### 1. Clone the repo
```bash
git clone https://github.com/Khaoshimself/online-shopping-site.git
cd online-shopping-site
```

### 2. Copy and edit .env
```bash
cp .env-example .env
# set usernames and passwords
vim .env
```

### 3. Startup docker-compose
```bash
docker compose up -d --build
```

### 4. Check out the site
- [Site is on port 8000](http://127.0.0.1:8000)
- [MongoExpress is on port 8888](http://127.0.0.1:8888)

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

* Don’t commit your `.venv` folder, or `.env` — it’s in `.gitignore`.
* Always run `docker compose up -d --build` when new dependencies are added.
* If you mess up your docker enviornment run `docker compose rm -s -v` to remove the containers and get a fresh start

---

👥 **IMPORTANT:** Everyone should clone this repo, set up a .env, load docker, and confirm they can load the placeholder pages before diving into CSS/JS.
