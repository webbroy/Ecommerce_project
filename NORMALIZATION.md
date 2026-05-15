# Normalization Report — 3rd Normal Form Audit

## 1. Original Schema (from Project 2)

```
Users       (user_id PK, name, email, created_at, metadata)
Products    (product_id PK, name, price, stock, created_at, metadata)
Orders      (order_id PK, user_id FK, order_date, status, metadata)
Order_Items (order_item_id PK, order_id FK, product_id FK, quantity, metadata)
Payments    (payment_id PK, order_id FK, amount, payment_date, metadata)
```

---

## 2. Original Functional Dependencies

| Table | Functional Dependency |
|---|---|
| Users | user_id → name, email, created_at, metadata |
| Products | product_id → name, price, stock, created_at, metadata |
| Orders | order_id → user_id, order_date, status, metadata |
| Order_Items | order_item_id → order_id, product_id, quantity |
| Payments | payment_id → order_id, amount, payment_date |

The `metadata` column in every table was a free-text catch-all that bundled multiple conceptually distinct attributes (e.g., category/tags in Products, active/premium tier in Users) into one column.

---

## 3. Anomaly Identification

### 3.1 Update Anomaly  `metadata` in Products
The `metadata` column stored both the product **category** and arbitrary **tags** as a single string (e.g., `"category:Electronics,tag:wireless"`).  
If the category name needed to change (e.g., "Electronics"  "Consumer Electronics"), every product row would need to be updated manually with string manipulation, risking inconsistency.

### 3.2 Insertion Anomaly  `metadata` in Products
A new product cannot be associated with a category without inserting a free-text string.  
If the category list is not enforced as an enum or foreign key, misspellings create phantom categories with no way to detect them.

### 3.3 Deletion Anomaly  `metadata` in Users
The `metadata` column bundled user tier information (e.g., `"active,premium"`).  
Deleting a user deleted all tier history. More critically, tier could not be queried reliably with SQL (e.g., `WHERE metadata = 'premium'` fails if metadata also contains `'active'`).

### 3.4 Transitive Dependency  Products  Category name
In the original schema: `product_id  metadata` where metadata encodes `category_name`.  
This means: `product_id  category_name`, and if we imagine a `category_id` hidden inside metadata, then `category_id → category_name` is a transitive dependency through a non-key attribute. This violates **3NF**.

---

## 4. Decomposition Steps

### Step 1 Reach 1NF
**Problem:** `metadata` is a multi-valued, non-atomic column.  
**Fix:** Remove `metadata` from all tables. Extract atomic values into proper columns.

- `Users.metadata` -> split into `tier` (VARCHAR: 'standard' | 'premium')  
- `Products.metadata`  extracted into a new `Categories` table (see Step 2)  
- `Orders.metadata`, `Order_Items.metadata`, `Payments.metadata`  no meaningful data; dropped  

### Step 2  Reach 2NF
All tables already had single-column primary keys, so there are no partial dependencies on composite keys. **2NF was already satisfied** after Step 1.

### Step 3  Reach 3NF
**Problem (transitive dependency):** `product_id  category_name` where `category_name` is a non-key attribute that determines itself.  
**Fix:** Decompose by creating a `Categories` table:

```
Before:  Products(product_id, name, price, stock, created_at, metadata[category_name])

After:   Categories(category_id PK, name)
         Products(product_id PK, name, price, stock, created_at, category_id FKCategories)
```

Now: `product_id  category_id`, and `category_id  category_name`.  
No non-key attribute determines another non-key attribute. **3NF achieved.**

---

## 5. Final Relational Schema (3NF)

```
Categories  (category_id PK, name)

Users       (user_id PK, name, email, created_at, tier)

Products    (product_id PK, name, price, stock, created_at,
             category_id FK  Categories.category_id)

Orders      (order_id PK, user_id FK  Users.user_id,
             order_date, status)

Order_Items (order_item_id PK,
             order_id FK  Orders.order_id,
             product_id FK  Products.product_id,
             quantity)

Payments    (payment_id PK,
             order_id FK  Orders.order_id,  -- UNIQUE: one payment per order
             amount, payment_date)
```

### Entity-Relationship Summary

- **Users** 1 **Orders** (one user can place many orders)  
- **Orders** 1  **Order_Items** (one order can contain many line items)  
- **Products** 1  **Order_Items** (one product can appear in many orders)  
- **Orders** 1  1 **Payments** (each order has exactly one payment)  
- **Categories** 1 **Products** (one category groups many products)  

All tables are in **1NF** (atomic columns), **2NF** (no partial dependencies), and **3NF** (no transitive dependencies through non-key attributes).
