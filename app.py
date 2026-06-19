from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "sheikh_topup_super_secure_key_2026"

DB_FILE = 'orders.db'

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    
    # টেবিল তৈরি
    cur.execute('''CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, uid TEXT, package TEXT, payment TEXT, txid TEXT, status TEXT DEFAULT 'Pending'
    )''')
    cur.execute('''CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE, category TEXT, image_url TEXT
    )''')
    cur.execute('''CREATE TABLE IF NOT EXISTS packages (
        id INTEGER PRIMARY KEY AUTOINCREMENT, product_name TEXT, package_name TEXT, price TEXT
    )''')
    cur.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, email TEXT UNIQUE, password TEXT
    )''')
    
    # 🎯 ওয়েবসাইট খালি না রাখার জন্য স্বয়ংক্রিয়ভাবে ৭টি প্রাথমিক অফার যোগ করা (যা পরে ডিলিট করা যাবে)
    default_products = [
        ("DAILY LIKE", "Offer", "https://i.ibb.co/6w2XmXv/daily.png"),
        ("Discount Weekly", "Offer", "https://i.ibb.co/Vv3xM3q/weekly.png"),
        ("Monthly Pack Special", "Offer", "https://i.ibb.co/yR4m8Yq/monthly.png"),
        ("FREE FIRE (UID) - ID CODE TOPUP", "Free Fire", "https://i.ibb.co/X7P4pL4/ff-uid.png"),
        ("Weekly & Monthly", "Free Fire", "https://i.ibb.co/Vv3xM3q/weekly.png"),
        ("Level Up Pass", "Free Fire", "https://i.ibb.co/60B8Z9G/levelup.png"),
        ("Evoground Access", "Free Fire", "https://i.ibb.co/M9XhN3H/evo.png")
    ]
    
    for name, cat, img in default_products:
        try:
            cur.execute("INSERT INTO products (name, category, image_url) VALUES (?, ?, ?)", (name, cat, img))
        except sqlite3.IntegrityError:
            pass # ইতিমধ্যে থাকলে নতুন করে যোগ হবে না
            
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

# 🔐 সাইন আপ / রেজিস্ট্রেশন রুট (৪0৪ ফিক্স)
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username').strip()
        email = request.form.get('email').strip()
        password = request.form.get('password')
        hashed_password = generate_password_hash(password, method='scrypt')
        try:
            conn = sqlite3.connect(DB_FILE)
            cur = conn.cursor()
            cur.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)", (username, email, hashed_password))
            conn.commit()
            conn.close()
            flash('রেজিস্ট্রেশন সফল হয়েছে! লগইন করুন।', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('এই ইউজারনেম বা ইমেইলটি ইতিমধ্যে নিবন্ধিত!', 'error')
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username').strip()
        password = request.form.get('password')
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username=?", (username,))
        user = cur.fetchone()
        conn.close()
        if user and check_password_hash(user[3], password):
            session['username'] = user[1]
            flash(f'স্বাগতম {user[1]}!', 'success')
            return redirect(url_for('index'))
        else:
            flash('ভুল ইউজারনেম বা পাসওয়ার্ড!', 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

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
        username = session.get('username', 'Guest')
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        cur.execute("INSERT INTO orders (username, uid, package, payment, txid) VALUES (?, ?, ?, ?, ?)", (username, uid, package, payment, txid))
        conn.commit()
        conn.close()
        flash('আপনার অর্ডারটি সফলভাবে জমা হয়েছে!', 'success')
        return redirect(url_for('index'))

# 🎯 আপনার অ্যাডমিন প্যানেলের সিক্রেট পাসওয়ার্ড
ADMIN_PASSWORD = "Saju@Admin#2026"

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    # 🔒 ১. প্রথমবার ঢুকলে বা লগআউট থাকলে পাসওয়ার্ড ভেরিফিকেশন করবে
    if not session.get('admin_logged_in'):
        if request.method == 'POST' and request.form.get('admin_pass'):
            entered_password = request.form.get('admin_pass')
            if entered_password == ADMIN_PASSWORD:
                session['admin_logged_in'] = True
                return redirect('/admin')
            else:
                return render_template('admin_login.html', error="ভুল পাসওয়ার্ড! আবার চেষ্টা করুন।")
        return render_template('admin_login.html')

    # 🔓 ২. পাসওয়ার্ড সঠিক হলে আপনার আগের নিচের কোডগুলো হুবহু রান হবে:
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add_product':
            name = request.form.get('name')
            category = request.form.get('category')
            image_url = request.form.get('image_url')
            try: cur.execute("INSERT INTO products (name, category, image_url) VALUES (?, ?, ?)", (name, category, image_url)); conn.commit()
            except: pass
        elif action == 'delete_product':
            p_id = request.form.get('product_id')
            cur.execute("DELETE FROM products WHERE id=?", (p_id,)); conn.commit()
        elif action == 'add_package':
            product_name = request.form.get('product_name')
            package_name = request.form.get('package_name')
            price = request.form.get('price')
            cur.execute("INSERT INTO packages (product_name, package_name, price) VALUES (?, ?, ?)", (product_name, package_name, price)); conn.commit()
        elif action == 'delete_package':
            pkg_id = request.form.get('package_id')
            cur.execute("DELETE FROM packages WHERE id=?", (pkg_id,)); conn.commit()

    cur.execute("SELECT * FROM orders ORDER BY id DESC")
    orders = cur.fetchall()
    cur.execute("SELECT * FROM products")
    products = cur.fetchall()
    cur.execute("SELECT * FROM packages")
    packages = cur.fetchall()
    conn.close()
    return render_template('admin.html', orders=orders, products=products, packages=packages)


# 🚪 অ্যাডমিন প্যানেল থেকে বের হওয়ার জন্য লগআউট রুট (এটি ঠিক admin ফাংশনের নিচে বসবে)
@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)
