# StoreDB — CS665 Project 

A full-stack inventory & order management system built with Python (Flask), SQLAlchemy, and SQLite, featuring a dark-themed Bootstrap 5 UI.

---

## Project Description

StoreDB lets store administrators manage **Users**, **Products**, **Orders**, and **Payments** through a clean browser interface.  
It demonstrates multi-table CRUD, relationship management (One-to-Many), atomic SQL transactions, server-side validation, and an aggregate summary dashboard.

---

## Tech Stack

| Language  Python 3.14
 Backend  Flask 3.x 
 ORM  Flask-SQLAlchemy 
 Database  SQLite (swap to PostgreSQL/MySQL via `DATABASE_URL`) 
 Frontend | HTML5, CSS3, Bootstrap 5.3, Jinja2 
 Version Control  Git 

---

## Installation Instructions

### 1. Clone the repository
```bash
git clone <your-repo-url>
cd Ecommerce_project
```

### 2. Create and activate a virtual environment
```bash
python -m venv venv

# macOS / Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

---

## Database Setup

The application **auto-creates** all tables and inserts seed data on first launch.  
If you prefer to apply the raw SQL schema manually, run the provided script:

```bash
# SQLite
sqlite3 instance/store.db < schema.sql

# PostgreSQL (set DATABASE_URL first)
psql $DATABASE_URL < schema.sql
```

To use PostgreSQL or MySQL instead of SQLite, set the environment variable:

```bash
export DATABASE_URL="postgresql://user:password@localhost/storedb"
```

---

## Usage

### Launch the development server
```bash
flask run
# OR
python app.py
```

Then open **http://127.0.0.1:5000** in your browser.

### Main Features

| Page | URL | Description |
|---|---|---|
| Dashboard | `/` | KPI cards, top users, recent orders, order status breakdown |
| Users | `/users` | List, add, edit, delete users |
| Products | `/products` | List, add, edit, delete products with stock & category |
| Orders | `/orders` | List, place, edit status, delete orders |
| Place Order | `/orders/add` | Atomic transaction: order + item + stock deduction + payment |

---

## Project Structure

```
Ecommerce_project/
├── app.py                  # Flask app, models, routes
├── requirements.txt
├── schema.sql              # Raw SQL schema (3NF)
├── README.md
├── NORMALIZATION.md        # 3NF audit documentation
├── AI_LOG.md               # AI assistance disclosure
├── .gitignore
├── static/
│   ├── css/style.css
│   └── js/main.js
└── templates/
    ├── base.html
    ├── dashboard.html
    ├── users.html
    ├── user_form.html
    ├── products.html
    ├── product_form.html
    ├── orders.html
    ├── order_form.html
    └── order_edit.html
```
