from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key="hotel123"

def get_db():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# ---------------- HOME PAGE ----------------
@app.route('/')
def home():
    return '''
    <h1>Hotel QR Ordering System</h1>
    <a href="/table/1">Customer - Table 1</a><br><br>
    <a href="/login">Manager Login</a>
    '''

# ---------------- MANAGER LOGIN ----------------
@app.route('/login', methods=['GET','POST'])
def login():

    if request.method=='POST':

        username=request.form['username']
        password=request.form['password']

        if username=="admin" and password=="1234":
            session['admin']=True
            return redirect('/admin')

    return render_template('login.html')

# ---------------- LOGOUT ----------------
@app.route('/logout')
def logout():
    session.pop('admin',None)
    return redirect('/login')

# ---------------- CUSTOMER MENU ----------------
@app.route('/table/<int:table_id>')
def menu(table_id):
    return render_template('menu.html', table=table_id)

# ---------------- PLACE ORDER ----------------
@app.route('/order', methods=['POST'])
def order():
    table = request.form['table']
    food = request.form['food']
    qty = request.form['qty']

    conn = get_db()
    conn.execute("INSERT INTO orders (table_id, food, qty, status, payment) VALUES (?, ?, ?, ?, ?)",
                 (table, food, qty, "Pending", "Unpaid"))
    conn.commit()
    return redirect(f'/table/{table}')

# ---------------- ADMIN DASHBOARD + FILTER ----------------
@app.route('/admin', methods=['GET','POST'])
def admin():

    if 'admin' not in session:
        return redirect('/login')

    conn=get_db()

    if request.method=='POST':
        table=request.form['table']

        if table=="all":
            orders=conn.execute("SELECT * FROM orders").fetchall()
        else:
            orders=conn.execute("SELECT * FROM orders WHERE table_id=?",
                                (table,)).fetchall()
    else:
        orders=conn.execute("SELECT * FROM orders").fetchall()

    return render_template('admin.html',orders=orders)

# ---------------- COOKING STATUS ----------------
@app.route('/cook/<int:id>')
def cook(id):
    if 'admin' not in session:
        return redirect('/login')

    conn = get_db()
    conn.execute("UPDATE orders SET status='Cooking' WHERE id=?", (id,))
    conn.commit()
    return redirect('/admin')

# ---------------- SERVED STATUS ----------------
@app.route('/serve/<int:id>')
def serve(id):
    if 'admin' not in session:
        return redirect('/login')

    conn = get_db()
    conn.execute("UPDATE orders SET status='Served' WHERE id=?", (id,))
    conn.commit()
    return redirect('/admin')

# ---------------- PAYMENT STATUS ----------------
@app.route('/pay/<int:id>')
def pay(id):
    if 'admin' not in session:
        return redirect('/login')

    conn = get_db()
    conn.execute("UPDATE orders SET payment='Paid' WHERE id=?", (id,))
    conn.commit()
    return redirect('/admin')

# ---------------- EDIT ORDER ----------------
@app.route('/edit/<int:id>', methods=['GET','POST'])
def edit(id):

    if 'admin' not in session:
        return redirect('/login')

    conn=get_db()

    if request.method=='POST':
        food=request.form['food']
        qty=request.form['qty']

        conn.execute("UPDATE orders SET food=?, qty=? WHERE id=?",
                     (food,qty,id))
        conn.commit()

        return redirect('/admin')

    order=conn.execute("SELECT * FROM orders WHERE id=?",
                       (id,)).fetchone()

    return render_template('edit.html',order=order)

# ---------------- DELETE ORDER ----------------
@app.route('/delete/<int:id>')
def delete(id):

    if 'admin' not in session:
        return redirect('/login')

    conn = get_db()
    conn.execute("DELETE FROM orders WHERE id=?", (id,))
    conn.commit()

    return redirect('/admin')

# ---------------- RUN ----------------
app.run(debug=True)