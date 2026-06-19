from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3

app = Flask(__name__)
app.secret_key = "sheikh_topup_secret_key_123"

DB_FILE = 'orders.db'

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    # ১. অর্ডার টেবিল
    cur.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            uid TEXT NOT NULL,
            package TEXT NOT NULL,
            payment TEXT NOT NULL,
            txid TEXT,
            status TEXT DEFAULT 'Pending'
        )
    ''')
    # ২. প্রোডাক্ট/ঘর টেবিল
    cur.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            image_url TEXT NOT NULL
        )
    ''')
    # ৩. ডায়মন্ড প্যাকেজ টেবিল (নতুন)
    cur.execute('''
        CREATE TABLE IF NOT EXISTS packages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT NOT NULL,
            package_name TEXT NOT NULL,
            price TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT * FROM products")
    all_products = cur.fetchall()
    conn.close()
    return render_template('index.html', products=all_products)

# কিনার পেজ - এখন এই গেমের জন্য তৈরি করা নির্দিষ্ট প্যাকেজগুলো লোড করবে
@app.route('/buy/<game_name>')
def buy(game_name):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT * FROM packages WHERE product_name=?", (game_name,))
    game_packages = cur.fetchall()
    conn.close()
    return render_template('buy.html', game_name=game_name, packages=game_packages)

@app.route('/submit_order', methods=['POST'])
def submit_order():
    if request.method == 'POST':
        uid = request.form.get('uid')
        package = request.form.get('package')
        payment = request.form.get('payment')
        txid = request.form.get('txid', '')

        try:
            conn = sqlite3.connect(DB_FILE)
            cur = conn.cursor()
            cur.execute("INSERT INTO orders (uid, package, payment, txid) VALUES (?, ?, ?, ?)",
                        (uid, package, payment, txid))
            conn.commit()
            conn.close()
            flash('আপনার অর্ডারটি সফলভাবে সম্পন্ন হয়েছে! ধন্যবাদ।', 'success')
        except:
            flash('সমস্যা হয়েছে, আবার চেষ্টা করুন।', 'error')
        return redirect(request.referrer or url_for('index'))

# অ্যাডমিন প্যানেল - ঘর এবং ডায়মন্ড প্যাকেজ দুইটাই কন্ট্রোল করার জন্য
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    if request.method == 'POST':
        action = request.form.get('action')
        
        # ঘর যোগ করা
        if action == 'add_product':
            name = request.form.get('name')
            category = request.form.get('category')
            image_url = request.form.get('image_url')
            cur.execute("INSERT INTO products (name, category, image_url) VALUES (?, ?, ?)", (name, category, image_url))
            conn.commit()
            
        # ঘর ডিলিট করা
        elif action == 'delete_product':
            p_id = request.form.get('product_id')
            cur.execute("DELETE FROM products WHERE id=?", (p_id,))
            conn.commit()
            
        # ডায়মন্ড প্যাকেজ যোগ করা (নতুন)
        elif action == 'add_package':
            product_name = request.form.get('product_name')
            package_name = request.form.get('package_name')
            price = request.form.get('price')
            cur.execute("INSERT INTO packages (product_name, package_name, price) VALUES (?, ?, ?)", (product_name, package_name, price))
            conn.commit()
            
        # ডায়মন্ড প্যাকেজ ডিলিট করা (নতুন)
        elif action == 'delete_package':
            pkg_id = request.form.get('package_id')
            cur.execute("DELETE FROM packages WHERE id=?", (pkg_id,))
            conn.commit()

    cur.execute("SELECT * FROM orders ORDER BY id DESC")
    orders = cur.fetchall()
    cur.execute("SELECT * FROM products")
    products = cur.fetchall()
    cur.execute("SELECT * FROM packages ORDER BY product_name ASC")
    packages = cur.fetchall()
    conn.close()
    
    return render_template('admin.html', orders=orders, products=products, packages=packages)

if __name__ == '__main__':
    app.run(debug=True)
