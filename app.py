import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'saju_secret_key_123' # সেশন সিকিউরিটির জন্য

# ডেটাবেজ টেবিল তৈরি করার ফাংশন
def init_db():
    conn = sqlite3.connect('orders.db')
    cur = conn.cursor()
    # অর্ডার টেবিল
    cur.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            uid TEXT NOT NULL,
            package TEXT NOT NULL,
            payment TEXT NOT NULL,
            status TEXT DEFAULT 'Pending'
        )
    ''')
    # ইউজার টেবিল (লগইন/সাইনআপের জন্য)
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# হোস্টিং সার্ভারে রান হওয়ার সাথে সাথেই যাতে ডাটাবেজ তৈরি হয়
init_db()

# ১. হোম পেজ (সব গেমের তালিকা)
@app.route('/')
def index():
    return render_template('index.html')

# ২. ডায়মন্ড কেনার পেজ (যেমন: Free Fire UID Topup)
@app.route('/buy/<game_name>')
def buy(game_name):
    return render_template('buy.html', game_name=game_name)

# ৩. অর্ডার সাবমিট নেওয়ার রুট
@app.route('/submit_order', methods=['POST'])
def submit_order():
    if request.method == 'POST':
        uid = request.form.get('uid')
        package = request.form.get('package')
        payment = request.form.get('payment')

        conn = sqlite3.connect('orders.db')
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO orders (uid, package, payment) VALUES (?, ?, ?)",
            (uid, package, payment)
        )
        conn.commit()
        conn.close()
        return redirect(url_for('index'))

# ৪. সাইন-আপ রুট
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        password = request.form.get('password')

        try:
            conn = sqlite3.connect('orders.db')
            cur = conn.cursor()
            cur.execute("INSERT INTO users (name, email, phone, password) VALUES (?, ?, ?, ?)",
                        (name, email, phone, password))
            conn.commit()
            conn.close()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            return "Email already exists!"
    return render_template('signup.html')

# ৫. লগইন রুট
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        conn = sqlite3.connect('orders.db')
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password))
        user = cur.fetchone()
        conn.close()

        if user:
            session['user'] = user[1] # ইউজারের নাম সেশনে সেভ
            return redirect(url_for('index'))
        else:
            return "Invalid Credentials!"
    return render_template('login.html')

# ৬. লগআউট রুট
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

# ৭. অ্যাডমিন প্যানেল রুট
@app.route('/admin')
def admin():
    conn = sqlite3.connect('orders.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM orders ORDER BY id DESC")
    orders = cur.fetchall()
    conn.close()
    return render_template('admin.html', orders=orders)

if __name__ == '__main__':
    app.run(debug=True)
