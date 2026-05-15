-- ============================================================
-- StoreDB Schema — 3rd Normal Form
-- CS665 Project 3
-- Run with: sqlite3 instance/store.db < schema.sql
-- ============================================================

DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS payments;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS categories;
DROP TABLE IF EXISTS users;

-- Categories table (extracted from Products.metadata to eliminate transitive dependency)
CREATE TABLE categories (
    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name        VARCHAR(100) NOT NULL UNIQUE
);

-- Users (tier replaces free-text metadata)
CREATE TABLE users (
    user_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    name       VARCHAR(100) NOT NULL,
    email      VARCHAR(100) NOT NULL UNIQUE,
    created_at DATE         NOT NULL DEFAULT (DATE('now')),
    tier       VARCHAR(20)  NOT NULL DEFAULT 'standard'  -- 'standard' | 'premium'
);

-- Products (category_id FK eliminates transitive dependency through metadata)
CREATE TABLE products (
    product_id  INTEGER      PRIMARY KEY AUTOINCREMENT,
    name        VARCHAR(100) NOT NULL,
    price       DECIMAL(10,2) NOT NULL CHECK (price > 0),
    stock       INTEGER      NOT NULL DEFAULT 0 CHECK (stock >= 0),
    created_at  DATE         NOT NULL DEFAULT (DATE('now')),
    category_id INTEGER      NOT NULL,
    FOREIGN KEY (category_id) REFERENCES categories(category_id)
);

-- Orders
CREATE TABLE orders (
    order_id   INTEGER     PRIMARY KEY AUTOINCREMENT,
    user_id    INTEGER     NOT NULL,
    order_date DATE        NOT NULL DEFAULT (DATE('now')),
    status     VARCHAR(50) NOT NULL DEFAULT 'pending',   -- pending | shipped | delivered | cancelled
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- Order Items (junction between Orders and Products — Many-to-Many resolved)
CREATE TABLE order_items (
    order_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id      INTEGER NOT NULL,
    product_id    INTEGER NOT NULL,
    quantity      INTEGER NOT NULL CHECK (quantity > 0),
    FOREIGN KEY (order_id)   REFERENCES orders(order_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

-- Payments (UNIQUE on order_id enforces one payment per order)
CREATE TABLE payments (
    payment_id   INTEGER       PRIMARY KEY AUTOINCREMENT,
    order_id     INTEGER       NOT NULL UNIQUE,
    amount       DECIMAL(10,2) NOT NULL CHECK (amount > 0),
    payment_date DATE          NOT NULL DEFAULT (DATE('now')),
    FOREIGN KEY (order_id) REFERENCES orders(order_id)
);
