from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Secret key for session management
app.secret_key = 'your_secret_key_here_change_in_production'

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'saqib'  # Change as per your setup
app.config['MYSQL_PASSWORD'] = 'cse@123'  # Change as per your setup
app.config['MYSQL_DB'] = 'ecofind'

# Initialize MySQL
mysql = MySQL(app)

# Define upload folder (for future image uploads)
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Allowed extensions (for future)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ========================
# ROUTES
# ========================

# --- Home / Product Feed ---
@app.route('/')
def home():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    # Get filter and search parameters
    category_filter = request.args.get('category', None)
    search_query = request.args.get('search', None)

    # Base query
    query = """
        SELECT p.id, p.title, p.description, p.price, p.category, p.image_url, u.username as seller_name
        FROM products p
        JOIN users u ON p.user_id = u.id
        WHERE p.is_active = 1
    """
    params = []

    if category_filter:
        query += " AND p.category = %s"
        params.append(category_filter)

    if search_query:
        query += " AND p.title LIKE %s"
        params.append(f"%{search_query}%")

    cursor.execute(query, tuple(params))
    products = cursor.fetchall()

    # Get all categories for filter dropdown
    cursor.execute("SELECT DISTINCT category FROM products WHERE is_active = 1")
    categories = [row['category'] for row in cursor.fetchall()]

    cursor.close()

    return render_template('index.html', products=products, categories=categories, selected_category=category_filter, search_query=search_query)

# --- User Registration ---
@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form and 'username' in request.form:
        email = request.form['email']
        password = request.form['password']
        username = request.form['username']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
        account = cursor.fetchone()

        if account:
            msg = 'Account already exists with this email!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            cursor.execute('INSERT INTO users (username, email, password) VALUES (%s, %s, %s)', (username, email, password))
            mysql.connection.commit()
            msg = 'You have successfully registered! Please login.'
            return redirect(url_for('login'))

        cursor.close()
    elif request.method == 'POST':
        msg = 'Please fill out the form!'

    return render_template('register.html', msg=msg)

# --- User Login ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE email = %s AND password = %s', (email, password))
        account = cursor.fetchone()

        if account:
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            session['email'] = account['email']
            return redirect(url_for('home'))
        else:
            msg = 'Incorrect email/password!'

    return render_template('login.html', msg=msg)

# --- User Logout ---
@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    session.pop('email', None)
    return redirect(url_for('login'))

# --- User Dashboard (Profile) ---
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'loggedin' not in session:
        return redirect(url_for('login'))

    msg = ''
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']

        # Check if email is being changed to one that already exists
        cursor.execute('SELECT * FROM users WHERE email = %s AND id != %s', (email, session['id']))
        existing = cursor.fetchone()
        if existing:
            msg = 'Email already in use by another account.'
        else:
            cursor.execute('UPDATE users SET username = %s, email = %s WHERE id = %s', (username, email, session['id']))
            mysql.connection.commit()
            session['username'] = username
            session['email'] = email
            msg = 'Profile updated successfully!'
            flash(msg, 'success')

    cursor.execute('SELECT * FROM users WHERE id = %s', (session['id'],))
    user = cursor.fetchone()
    cursor.close()

    return render_template('dashboard.html', user=user, msg=msg)

# --- Add New Product ---
@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if 'loggedin' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        category = request.form['category']
        price = request.form['price']
        image_url = request.form.get('image_url', '/static/placeholder.jpg')  # Default placeholder

        # In MVP, we use a text field for image URL. In future, handle file upload.
        # if 'image' in request.files:
        #     file = request.files['image']
        #     if file and allowed_file(file.filename):
        #         filename = secure_filename(file.filename)
        #         file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        #         image_url = f'/static/uploads/{filename}'

        cursor = mysql.connection.cursor()
        cursor.execute(
            'INSERT INTO products (user_id, title, description, category, price, image_url, is_active) VALUES (%s, %s, %s, %s, %s, %s, %s)',
            (session['id'], title, description, category, price, image_url, 1)
        )
        mysql.connection.commit()
        cursor.close()
        flash('Product added successfully!', 'success')
        return redirect(url_for('my_listings'))

    return render_template('add_product.html')

# --- My Listings (View, Edit, Delete) ---
@app.route('/my_listings')
def my_listings():
    if 'loggedin' not in session:
        return redirect(url_for('login'))

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM products WHERE user_id = %s AND is_active = 1', (session['id'],))
    products = cursor.fetchall()
    cursor.close()

    return render_template('my_listings.html', products=products)

# --- Edit Product ---
@app.route('/edit_product/<int:id>', methods=['GET', 'POST'])
def edit_product(id):
    if 'loggedin' not in session:
        return redirect(url_for('login'))

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM products WHERE id = %s AND user_id = %s', (id, session['id']))
    product = cursor.fetchone()

    if not product:
        flash('Product not found or you do not have permission to edit it.', 'danger')
        return redirect(url_for('my_listings'))

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        category = request.form['category']
        price = request.form['price']
        image_url = request.form.get('image_url', product['image_url'])

        cursor.execute(
            'UPDATE products SET title = %s, description = %s, category = %s, price = %s, image_url = %s WHERE id = %s AND user_id = %s',
            (title, description, category, price, image_url, id, session['id'])
        )
        mysql.connection.commit()
        flash('Product updated successfully!', 'success')
        return redirect(url_for('my_listings'))

    cursor.close()
    return render_template('edit_product.html', product=product)

# --- Delete Product ---
@app.route('/delete_product/<int:id>', methods=['POST'])
def delete_product(id):
    if 'loggedin' not in session:
        return redirect(url_for('login'))

    cursor = mysql.connection.cursor()
    cursor.execute('UPDATE products SET is_active = 0 WHERE id = %s AND user_id = %s', (id, session['id']))
    mysql.connection.commit()
    cursor.close()
    flash('Product deleted successfully!', 'success')
    return redirect(url_for('my_listings'))

# --- Product Detail View ---
@app.route('/product/<int:id>')
def product_detail(id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('''
        SELECT p.*, u.username as seller_name
        FROM products p
        JOIN users u ON p.user_id = u.id
        WHERE p.id = %s AND p.is_active = 1
    ''', (id,))
    product = cursor.fetchone()
    cursor.close()

    if not product:
        flash('Product not found.', 'danger')
        return redirect(url_for('home'))

    return render_template('product_detail.html', product=product)

# --- Add to Cart ---
@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    if 'loggedin' not in session:
        return jsonify({'success': False, 'message': 'Please login to add items to cart.'})

    if 'cart' not in session:
        session['cart'] = []

    # Check if product exists and is active
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT id, title, price, image_url FROM products WHERE id = %s AND is_active = 1', (product_id,))
    product = cursor.fetchone()
    cursor.close()

    if not product:
        return jsonify({'success': False, 'message': 'Product not found.'})

    # Add to session cart (for MVP simplicity)
    cart_item = {
        'product_id': product['id'],
        'title': product['title'],
        'price': float(product['price']),
        'image_url': product['image_url']
    }
    session['cart'].append(cart_item)
    session.modified = True

    return jsonify({'success': True, 'message': 'Item added to cart!'})

# --- View Cart ---
@app.route('/cart')
def view_cart():
    if 'loggedin' not in session:
        return redirect(url_for('login'))

    cart = session.get('cart', [])
    total = sum(item['price'] for item in cart)

    return render_template('cart.html', cart=cart, total=total)

# --- Clear Cart (for MVP) ---
@app.route('/clear_cart', methods=['POST'])
def clear_cart():
    if 'loggedin' in session:
        session.pop('cart', None)
        flash('Cart cleared.', 'info')
    return redirect(url_for('view_cart'))

# --- Simulate Purchase (MVP) ---
@app.route('/checkout', methods=['POST'])
def checkout():
    if 'loggedin' not in session:
        return redirect(url_for('login'))

    cart = session.get('cart', [])
    if not cart:
        flash('Your cart is empty.', 'warning')
        return redirect(url_for('view_cart'))

    cursor = mysql.connection.cursor()
    try:
        for item in cart:
            cursor.execute(
                'INSERT INTO purchases (user_id, product_id, purchase_price) VALUES (%s, %s, %s)',
                (session['id'], item['product_id'], item['price'])
            )
        mysql.connection.commit()
        session.pop('cart', None)  # Clear cart after purchase
        flash('Purchase successful! Thank you for shopping sustainably.', 'success')
    except Exception as e:
        mysql.connection.rollback()
        flash('An error occurred during checkout.', 'danger')
    finally:
        cursor.close()

    return redirect(url_for('previous_purchases'))

# --- Previous Purchases ---
@app.route('/previous_purchases')
def previous_purchases():
    if 'loggedin' not in session:
        return redirect(url_for('login'))

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('''
        SELECT p.title, p.description, p.price, p.image_url, pur.purchase_date
        FROM purchases pur
        JOIN products p ON pur.product_id = p.id
        WHERE pur.user_id = %s
        ORDER BY pur.purchase_date DESC
    ''', (session['id'],))
    purchases = cursor.fetchall()
    cursor.close()

    return render_template('previous_purchases.html', purchases=purchases)

# --- Run App ---
if __name__ == '__main__':
    app.run(debug=True)