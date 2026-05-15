"""
StoreDB — CS665 Project 3
Flask + stdlib sqlite3 (no extra ORM required)
Run: python app.py
"""
import sqlite3, os
from datetime import date
from flask import Flask, render_template, request, redirect, url_for, flash, g

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-change-me')
DATABASE = os.path.join(os.path.dirname(__file__), 'store.db')

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
        g.db.execute('PRAGMA foreign_keys = ON')
    return g.db

@app.teardown_appcontext
def close_db(e=None):
    db = g.pop('db', None)
    if db: db.close()

def query(sql, args=(), one=False):
    cur = get_db().execute(sql, args)
    rv  = cur.fetchall()
    return (rv[0] if rv else None) if one else rv

def execute(sql, args=()):
    db = get_db()
    cur = db.execute(sql, args)
    db.commit()
    return cur.lastrowid

SCHEMA = """
CREATE TABLE IF NOT EXISTS categories (category_id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL UNIQUE);
CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, email TEXT NOT NULL UNIQUE, created_at TEXT NOT NULL DEFAULT (DATE('now')), tier TEXT NOT NULL DEFAULT 'standard');
CREATE TABLE IF NOT EXISTS products (product_id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, price REAL NOT NULL CHECK (price>0), stock INTEGER NOT NULL DEFAULT 0 CHECK (stock>=0), created_at TEXT NOT NULL DEFAULT (DATE('now')), category_id INTEGER NOT NULL, FOREIGN KEY (category_id) REFERENCES categories(category_id));
CREATE TABLE IF NOT EXISTS orders (order_id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, order_date TEXT NOT NULL DEFAULT (DATE('now')), status TEXT NOT NULL DEFAULT 'pending', FOREIGN KEY (user_id) REFERENCES users(user_id));
CREATE TABLE IF NOT EXISTS order_items (order_item_id INTEGER PRIMARY KEY AUTOINCREMENT, order_id INTEGER NOT NULL, product_id INTEGER NOT NULL, quantity INTEGER NOT NULL CHECK (quantity>0), FOREIGN KEY (order_id) REFERENCES orders(order_id), FOREIGN KEY (product_id) REFERENCES products(product_id));
CREATE TABLE IF NOT EXISTS payments (payment_id INTEGER PRIMARY KEY AUTOINCREMENT, order_id INTEGER NOT NULL UNIQUE, amount REAL NOT NULL CHECK (amount>0), payment_date TEXT NOT NULL DEFAULT (DATE('now')), FOREIGN KEY (order_id) REFERENCES orders(order_id));
"""

def init_db():
    con = sqlite3.connect(DATABASE)
    con.executescript(SCHEMA)
    if con.execute('SELECT COUNT(*) FROM categories').fetchone()[0] == 0:
        cats = ['Electronics','Clothing','Books','Home & Garden','Sports']
        for c in cats: con.execute('INSERT INTO categories (name) VALUES (?)',(c,))
        con.execute("INSERT INTO users (name,email,tier) VALUES ('Alice Johnson','alice@example.com','premium')")
        con.execute("INSERT INTO users (name,email,tier) VALUES ('Bob Smith','bob@example.com','standard')")
        con.execute("INSERT INTO users (name,email,tier) VALUES ('Carol White','carol@example.com','premium')")
        con.execute("INSERT INTO users (name,email,tier) VALUES ('David Lee','david@example.com','standard')")
        cat_ids = {r[0]:r[1] for r in con.execute('SELECT name,category_id FROM categories')}
        prods=[('Wireless Headphones',89.99,50,cat_ids['Electronics']),('Running Shoes',120.00,30,cat_ids['Sports']),('Python Cookbook',39.99,100,cat_ids['Books']),('Smart Lamp',45.00,20,cat_ids['Home & Garden']),('Denim Jacket',75.50,15,cat_ids['Clothing'])]
        for p in prods: con.execute('INSERT INTO products (name,price,stock,category_id) VALUES (?,?,?,?)',p)
        uids=[r[0] for r in con.execute('SELECT user_id FROM users')]
        pids=[r[0] for r in con.execute('SELECT product_id FROM products')]
        for u,s in [(uids[0],'delivered'),(uids[1],'shipped'),(uids[0],'pending'),(uids[2],'pending')]:
            con.execute('INSERT INTO orders (user_id,status) VALUES (?,?)',(u,s))
        oids=[r[0] for r in con.execute('SELECT order_id FROM orders')]
        for o,p,q in [(oids[0],pids[0],2),(oids[1],pids[1],1),(oids[2],pids[2],3),(oids[3],pids[3],1)]:
            con.execute('INSERT INTO order_items (order_id,product_id,quantity) VALUES (?,?,?)',(o,p,q))
        for o,a in [(oids[0],179.98),(oids[1],120.00),(oids[2],119.97)]:
            con.execute('INSERT INTO payments (order_id,amount) VALUES (?,?)',(o,a))
    con.commit(); con.close()

def v_nonempty(v,f): return None if v and str(v).strip() else f'{f} cannot be empty.'
def v_pos_num(v,f):
    try: return None if float(v)>0 else f'{f} must be > 0.'
    except: return f'{f} must be a valid number.'
def v_nonneg_int(v,f):
    try: return None if int(v)>=0 else f'{f} cannot be negative.'
    except: return f'{f} must be a whole number.'

@app.route('/')
def dashboard():
    tu=query('SELECT COUNT(*) FROM users',one=True)[0]
    to=query('SELECT COUNT(*) FROM orders',one=True)[0]
    tr=query('SELECT COALESCE(SUM(amount),0) FROM payments',one=True)[0]
    ap=query('SELECT COALESCE(AVG(amount),0) FROM payments',one=True)[0]
    tp=query('SELECT COUNT(*) FROM products',one=True)[0]
    top=query('SELECT u.name,COUNT(o.order_id) AS cnt FROM users u JOIN orders o ON u.user_id=o.user_id GROUP BY u.user_id ORDER BY cnt DESC LIMIT 5')
    sc=query('SELECT status,COUNT(*) AS cnt FROM orders GROUP BY status')
    ro=query('SELECT o.order_id,o.status,u.name AS user_name FROM orders o JOIN users u ON o.user_id=u.user_id ORDER BY o.order_date DESC LIMIT 5')
    return render_template('dashboard.html',total_users=tu,total_orders=to,total_revenue=round(float(tr),2),avg_payment=round(float(ap),2),total_products=tp,top_users=top,status_counts=sc,recent_orders=ro)

@app.route('/users')
def users():
    all_users=query('SELECT u.*,COUNT(o.order_id) AS order_count FROM users u LEFT JOIN orders o ON u.user_id=o.user_id GROUP BY u.user_id ORDER BY u.created_at DESC')
    return render_template('users.html',users=all_users)

@app.route('/users/add',methods=['GET','POST'])
def add_user():
    if request.method=='POST':
        name=request.form.get('name','').strip(); email=request.form.get('email','').strip(); tier=request.form.get('tier','standard')
        errors=list(filter(None,[v_nonempty(name,'Name'),v_nonempty(email,'Email'),None if '@' in email else 'Invalid email.',None if not query('SELECT 1 FROM users WHERE email=?',(email,)) else 'Email taken.']))
        if errors: [flash(e,'danger') for e in errors]; return render_template('user_form.html',action='Add',user=None)
        execute('INSERT INTO users (name,email,tier) VALUES (?,?,?)',(name,email,tier)); flash('User added.','success'); return redirect(url_for('users'))
    return render_template('user_form.html',action='Add',user=None)

@app.route('/users/edit/<int:uid>',methods=['GET','POST'])
def edit_user(uid):
    user=query('SELECT * FROM users WHERE user_id=?',(uid,),one=True)
    if not user: return 'Not found',404
    if request.method=='POST':
        name=request.form.get('name','').strip(); email=request.form.get('email','').strip(); tier=request.form.get('tier','standard')
        conflict=query('SELECT user_id FROM users WHERE email=? AND user_id!=?',(email,uid),one=True)
        errors=list(filter(None,[v_nonempty(name,'Name'),v_nonempty(email,'Email'),None if '@' in email else 'Invalid email.','Email taken.' if conflict else None]))
        if errors: [flash(e,'danger') for e in errors]; return render_template('user_form.html',action='Edit',user=user)
        execute('UPDATE users SET name=?,email=?,tier=? WHERE user_id=?',(name,email,tier,uid)); flash('User updated.','success'); return redirect(url_for('users'))
    return render_template('user_form.html',action='Edit',user=user)

@app.route('/users/delete/<int:uid>',methods=['POST'])
def delete_user(uid):
    db=get_db()
    try:
        orders=db.execute('SELECT order_id FROM orders WHERE user_id=?',(uid,)).fetchall()
        for o in orders:
            db.execute('DELETE FROM payments WHERE order_id=?',(o[0],))
            db.execute('DELETE FROM order_items WHERE order_id=?',(o[0],))
        db.execute('DELETE FROM orders WHERE user_id=?',(uid,))
        db.execute('DELETE FROM users WHERE user_id=?',(uid,))
        db.commit(); flash('User deleted.','success')
    except Exception as ex: db.rollback(); flash(f'Error: {ex}','danger')
    return redirect(url_for('users'))

@app.route('/products')
def products():
    prods=query('SELECT p.*,c.name AS category_name FROM products p JOIN categories c ON p.category_id=c.category_id ORDER BY p.created_at DESC')
    return render_template('products.html',products=prods)

@app.route('/products/add',methods=['GET','POST'])
def add_product():
    cats=query('SELECT * FROM categories ORDER BY name')
    if request.method=='POST':
        name=request.form.get('name','').strip(); price=request.form.get('price'); stock=request.form.get('stock'); cat=request.form.get('category_id')
        errors=list(filter(None,[v_nonempty(name,'Name'),v_pos_num(price,'Price'),v_nonneg_int(stock,'Stock'),None if cat else 'Select a category.']))
        if errors: [flash(e,'danger') for e in errors]; return render_template('product_form.html',action='Add',product=None,categories=cats)
        execute('INSERT INTO products (name,price,stock,category_id) VALUES (?,?,?,?)',(name,float(price),int(stock),int(cat))); flash('Product added.','success'); return redirect(url_for('products'))
    return render_template('product_form.html',action='Add',product=None,categories=cats)

@app.route('/products/edit/<int:pid>',methods=['GET','POST'])
def edit_product(pid):
    prod=query('SELECT * FROM products WHERE product_id=?',(pid,),one=True); cats=query('SELECT * FROM categories ORDER BY name')
    if not prod: return 'Not found',404
    if request.method=='POST':
        name=request.form.get('name','').strip(); price=request.form.get('price'); stock=request.form.get('stock'); cat=request.form.get('category_id')
        errors=list(filter(None,[v_nonempty(name,'Name'),v_pos_num(price,'Price'),v_nonneg_int(stock,'Stock')]))
        if errors: [flash(e,'danger') for e in errors]; return render_template('product_form.html',action='Edit',product=prod,categories=cats)
        execute('UPDATE products SET name=?,price=?,stock=?,category_id=? WHERE product_id=?',(name,float(price),int(stock),int(cat),pid)); flash('Product updated.','success'); return redirect(url_for('products'))
    return render_template('product_form.html',action='Edit',product=prod,categories=cats)

@app.route('/products/delete/<int:pid>',methods=['POST'])
def delete_product(pid):
    execute('DELETE FROM products WHERE product_id=?',(pid,)); flash('Product deleted.','success'); return redirect(url_for('products'))

@app.route('/orders')
def orders():
    all_orders=query('SELECT o.order_id,o.order_date,o.status,u.name AS user_name,p.name AS product_name,oi.quantity,pay.amount FROM orders o JOIN users u ON o.user_id=u.user_id LEFT JOIN order_items oi ON o.order_id=oi.order_id LEFT JOIN products p ON oi.product_id=p.product_id LEFT JOIN payments pay ON o.order_id=pay.order_id ORDER BY o.order_date DESC')
    return render_template('orders.html',orders=all_orders)

@app.route('/orders/add',methods=['GET','POST'])
def add_order():
    users_list=query('SELECT user_id,name,email FROM users ORDER BY name')
    prods_list=query('SELECT product_id,name,price,stock FROM products WHERE stock>0 ORDER BY name')
    if request.method=='POST':
        uid=request.form.get('user_id'); pid=request.form.get('product_id'); qty=request.form.get('quantity'); amt=request.form.get('amount')
        errors=list(filter(None,[None if uid else 'Select a customer.',None if pid else 'Select a product.',v_nonneg_int(qty,'Quantity'),v_pos_num(amt,'Payment amount.')]))
        if not errors and int(qty)==0: errors.append('Quantity must be at least 1.')
        prod=query('SELECT * FROM products WHERE product_id=?',(int(pid),),one=True) if pid and not errors else None
        if prod and int(qty)>prod['stock']: errors.append(f'Only {prod["stock"]} in stock.')
        if errors: [flash(e,'danger') for e in errors]; return render_template('order_form.html',users=users_list,products=prods_list)
        db=get_db()
        try:
            cur=db.execute('INSERT INTO orders (user_id,status) VALUES (?,?)',(int(uid),'pending')); oid=cur.lastrowid
            db.execute('INSERT INTO order_items (order_id,product_id,quantity) VALUES (?,?,?)',(oid,int(pid),int(qty)))
            db.execute('UPDATE products SET stock=stock-? WHERE product_id=?',(int(qty),int(pid)))
            db.execute('INSERT INTO payments (order_id,amount) VALUES (?,?)',(oid,float(amt)))
            db.commit(); flash('Order placed!','success')
        except Exception as ex: db.rollback(); flash(f'Transaction failed: {ex}','danger')
        return redirect(url_for('orders'))
    return render_template('order_form.html',users=users_list,products=prods_list)

@app.route('/orders/edit/<int:oid>',methods=['GET','POST'])
def edit_order(oid):
    order=query('SELECT o.*,u.name AS user_name FROM orders o JOIN users u ON o.user_id=u.user_id WHERE o.order_id=?',(oid,),one=True)
    if not order: return 'Not found',404
    if request.method=='POST':
        status=request.form.get('status','').strip()
        if status not in ('pending','shipped','delivered','cancelled'): flash('Invalid status.','danger'); return render_template('order_edit.html',order=order)
        execute('UPDATE orders SET status=? WHERE order_id=?',(status,oid)); flash('Status updated.','success'); return redirect(url_for('orders'))
    return render_template('order_edit.html',order=order)

@app.route('/orders/delete/<int:oid>',methods=['POST'])
def delete_order(oid):
    db=get_db()
    try:
        items=db.execute('SELECT product_id,quantity FROM order_items WHERE order_id=?',(oid,)).fetchall()
        for item in items: db.execute('UPDATE products SET stock=stock+? WHERE product_id=?',(item[1],item[0]))
        db.execute('DELETE FROM payments WHERE order_id=?',(oid,))
        db.execute('DELETE FROM order_items WHERE order_id=?',(oid,))
        db.execute('DELETE FROM orders WHERE order_id=?',(oid,))
        db.commit(); flash('Order deleted and stock restored.','success')
    except Exception as ex: db.rollback(); flash(f'Error: {ex}','danger')
    return redirect(url_for('orders'))

if __name__=='__main__':
    init_db()
    app.run(debug=True)
