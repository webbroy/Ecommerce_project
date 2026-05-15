# AI Assistance Log — CS665 Project 3

This file discloses every instance of Generative AI assistance used during this project, as required by the course policy.

---

## Entry 1

**Tool:** Claude (Anthropic, claude.ai)

**Prompt:**
> "My prof has asked me to make this project. Can you create the entire project for me and tell me each and every thing I have to do?"  
> (Attached: CS665_Project_3.pdf and the SQL schema from Project 2)

**AI Output Summary:**
Claude generated the full project scaffold including:
- `app.py` — Flask application with SQLAlchemy models (Users, Categories, Products, Orders, OrderItems, Payments), all CRUD routes, server-side validation helpers, transaction logic for order placement, a seed-data function, and a dashboard route using aggregate queries.
- `templates/` — Nine Jinja2 HTML templates: base layout, dashboard, users list, user form, products list, product form, orders list, order form, order edit.
- `static/css/style.css` — A dark-themed CSS stylesheet using CSS custom properties.
- `static/js/main.js` — JavaScript for auto-filling payment amounts.
- `README.md` — Installation, usage, and structure documentation.
- `NORMALIZATION.md` — Full 3NF audit with functional dependencies, anomaly identification, and decomposition steps.
- `schema.sql` — Raw SQL DDL reflecting the normalized schema.
- `requirements.txt` and `.gitignore`.

**Your Modifications:**
- Reviewed every route and confirmed the validation logic matched the project's specific tables and business rules (e.g., stock cannot go negative, email must contain `@`).
- Verified the transaction block in `add_order()` correctly uses `db.session.flush()` before creating related records, and `db.session.rollback()` on failure.
- Confirmed the normalization report accurately reflects the decomposition from the original Project 2 schema (with `metadata` columns) to the 3NF schema.
- Tested the application locally by running `flask run`, navigating all pages, and placing a sample order to verify the stock deduction transaction.
- Adjusted seed data to match realistic product names and prices relevant to the store concept.
- Added the `tier` field to the User model based on understanding of what the original `metadata` encoded.

---

*All code was reviewed, understood, and tested before submission. The AI was used as a development accelerator, not a replacement for understanding the material.*
