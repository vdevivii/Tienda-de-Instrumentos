from flask import render_template, request, redirect, url_for, session, flash
from app import app, db
from app.models import (
    add_user, validate_user, get_user,
    get_all_instruments, add_instrument, get_instrument_by_id, update_instrument, delete_instrument,
    add_card, get_card, add_order, get_orders, add_review, get_reviews
)
from datetime import datetime
from bson import ObjectId
import random

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/shop')
def shop():
    instruments = list(get_all_instruments())
    return render_template('shop.html', instruments=instruments)

@app.route('/admin_dashboard')
def admin_dashboard():
    instruments = list(get_all_instruments())
    return render_template('admin_dashboard.html', instruments=instruments)

@app.route('/add_instrument', methods=['GET', 'POST'])
def add_instrument_route():
    if request.method == 'POST':
        instrument = {
            'name': request.form.get('name'),
            'description': request.form.get('description'),
            'category': request.form.get('category'),
            'price': request.form.get('price'),
            'image_url': request.form.get('image_url')
        }
        add_instrument(instrument)
        return redirect(url_for('admin_dashboard'))
    return render_template('add_instrument.html')

@app.route('/edit_instrument/<instrument_id>', methods=['GET', 'POST'])
def edit_instrument_route(instrument_id):
    instrument = get_instrument_by_id(instrument_id)
    if request.method == 'POST':
        updated_instrument = {
            'name': request.form.get('name'),
            'description': request.form.get('description'),
            'category': request.form.get('category'),
            'price': float(request.form.get(('price'))),
            'image_url': request.form.get('image_url')
        }
        update_instrument(instrument_id, updated_instrument)
        return redirect(url_for('admin_dashboard'))
    return render_template('edit_instrument.html', instrument=instrument)

@app.route('/delete_instrument/<instrument_id>', methods=['POST'])
def delete_instrument_route(instrument_id):
    delete_instrument(instrument_id)
    return redirect(url_for('admin_dashboard'))

@app.route('/add_to_cart/<instrument_id>')
def add_to_cart(instrument_id):
    instrument = get_instrument_by_id(instrument_id)
    if 'cart' not in session:
        session['cart'] = []

    # Convertir ObjectId a cadena
    instrument['_id'] = str(instrument['_id'])
    
    # Verificar si el producto ya está en el carrito y aumentar la cantidad si es así
    for item in session['cart']:
        if item['_id'] == instrument_id:
            item['quantity'] += 1
            break
    else:
        # Si el producto no está en el carrito, agregarlo con cantidad 1
        instrument['quantity'] = 1
        session['cart'].append(instrument)
    
    session.modified = True
    return redirect(url_for('shop'))

@app.route('/remove_from_cart/<index>')
def remove_from_cart(index):
    if 'cart' in session:
        session['cart'].pop(int(index))
        session.modified = True
    return redirect(url_for('cart'))

@app.route('/cart')
def cart():
    if 'cart' not in session:
        session['cart'] = []
    cart = session.get('cart', [])
    for item in cart:
        if 'quantity' not in item:
            item['quantity'] = 1
    total = sum(float(item[('price')]) * item['quantity'] for item in cart)
    return render_template('cart.html', cart=cart, total=total)

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if 'username' not in session:
        flash('Por favor, inicie sesión para proceder con la compra.')
        return redirect(url_for('login'))
    if 'cart' not in session or not session['cart']:
        flash('No hay productos en el carrito')
        return redirect(url_for('cart'))
    
    if request.method == 'GET' or request.method == 'POST':
        card = get_card(session['username'])
        if not card:
            flash('No se ha registrado una tarjeta. Añada una tarjeta antes de proceder.')
            return redirect(url_for('add_card_route'))
        items = session['cart']
        total = sum(item['price'] * item['quantity'] for item in items)
        add_order(session['username'], items, total)
        session.pop('cart')
        probabilidad = random.random()
        if probabilidad < 0.8:
            return render_template('checkout.html', success=True, items=items, total=total, date=datetime.now())
        else:
            return render_template('checkout.html', success=False, items=items, total=total, date=datetime.now())
        
    
    items = session['cart']
    total = sum(item['price'] * item['quantity'] for item in items)
    return render_template('checkout.html', success=False, items=items, total=total, date=datetime.now())

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = 'user'
        if get_user(username):
            flash('El nombre de usuario ya está en uso.')
            
        else:
            add_user(username, password, role)
            flash('Usuario registrado con éxito.')
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = validate_user(username, password)
        if user:
            session['username'] = user['username']
            session['role'] = user['role']
            session.pop('cart', None)
            return redirect(url_for('index'))
        else:
            flash('Nombre de usuario o contraseña incorrectos.')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('role', None)
    session.pop('cart', None)
    flash('Has cerrado sesión exitosamente.')
    return redirect(url_for('index'))

@app.route('/order_history')
def order_history():
    if 'username' not in session:
        flash('Por favor, inicie sesión para ver su historial de compras.')
        return redirect(url_for('login'))
    
    orders = list(get_orders(session['username']))
    return render_template('order_history.html', orders=orders)

@app.route('/add_card', methods=['GET', 'POST'])
def add_card_route():
    if 'username' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        card_number = request.form.get('card_number')
        expiration_date = request.form.get('expiration_date')
        cvv = request.form.get('cvv')
        add_card(session['username'], card_number, expiration_date, cvv)
        return redirect(url_for('checkout'))
    return render_template('add_card.html')

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query')
    category = request.args.get('category')
    min_price = request.args.get('min_price')
    max_price = request.args.get('max_price')

    filters = {}
    if query:
        filters['$text'] = {'$search': query}
    if category:
        filters['category'] = category
    if min_price:
        filters['price'] = {'$gte': float(min_price)}
    if max_price:
        if 'price' in filters:
            filters['price']['$lte'] = float(max_price)
        else:
            filters['price'] = {'$lte': float(max_price)}

    instruments = list(db.instruments.find(filters))
    return render_template('shop.html', instruments=instruments)

@app.route('/update_cart', methods=['POST'])
def update_cart():
    index = int(request.form.get('index'))
    quantity = int(request.form.get('quantity'))
    if 'cart' in session:
        cart = session['cart']
        if 0 <= index < len(cart):
            cart[index]['quantity'] = quantity
            session.modified = True
    return redirect(url_for('cart'))

@app.route('/cancel_purchase')
def cancel_purchase():
    if 'cart' in session:
        session.pop('cart')
    flash('La compra ha sido cancelada y el carrito se ha vaciado.')
    return redirect(url_for('cart'))

@app.route('/reset_session')
def reset_session():
    session.clear()
    return redirect(url_for('index'))
