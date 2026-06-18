import sqlite3
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# ডেটাবেজ টেবিল তৈরি করার ফাংশন
def init_db():
    conn = sqlite3.connect('orders.db')
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            uid TEXT NOT NULL,
            package TEXT NOT NULL,
            payment TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# হোম পেজ (টপ-আপ ফর্ম)
@app.route('/')
def index():
    return render_template('index.html')

# অর্ডার সাবমিট নেওয়ার রুট
@app.route('/submit', methods=['POST'])
def submit():
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

# অ্যাডমিন প্যানেল রুট
@app.route('/admin')
def admin():
    conn = sqlite3.connect('orders.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM orders")
    orders = cur.fetchall()
    conn.close()
    return render_template('admin.html', orders=orders)

# মেইন ফাংশন (সার্ভার রান করার অংশ)
if __name__ == '__main__':
    init_db()
    app.run(debug=True)