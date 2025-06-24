from flask import Flask, render_template, session, redirect, url_for, request
import os

app = Flask(__name__)
app.secret_key = 'super-secret-keyss'


def get_items():
    return {
        'item1': {'name': 'T-Shirt', 'img': url_for('static', filename='t-shirt.png'), 'price': 100},
        'item2': {'name': 'Sun Glasses', 'img': url_for('static', filename='sunglass.png'), 'price': 60},
        'item3': {'name': 'Cap', 'img': url_for('static', filename='cap.png'), 'price': 10}
    }

    
WALLET_BALANCE = 50

@app.before_request
def init_session():
    if 'cart' not in session:
        session['cart'] = {}
    if 'purchased' not in session:
        session['purchased'] = False

@app.route('/')

def index():
    ITEMS = get_items()
    return render_template('index.html', items=ITEMS)

import math

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    ITEMS = get_items()
    item_id = request.form.get('item_id')
    quantity_str = request.form.get('quantity')

    try:
        # Convert to float first
        quantity_float = float(quantity_str)

        # Round upward to the nearest whole number
        quantity = math.ceil(quantity_float)

    except (ValueError, TypeError):
        session['error'] = "Invalid quantity. Please enter a number."
        return redirect(url_for('cart'))

    if item_id in ITEMS:
        cart = session['cart']
        cart[item_id] = cart.get(item_id, 0) + quantity
        session['cart'] = cart

    return redirect(url_for('cart'))


@app.route('/cart')
def cart():
    ITEMS = get_items()
    cart_items = []
    total = 0

    for item_id, quantity in session['cart'].items():
        item = ITEMS.get(item_id)
        if item:
            subtotal = item['price'] * quantity
            cart_items.append({
                'id': item_id,
                'name': item['name'],
                'price': item['price'],
                'img': item['img'],
                'quantity': quantity,
                'subtotal': subtotal
            })
            total += subtotal

    if total < 0:
        total = 0

    error = session.pop('error', None)

    return render_template(
        'cart.html',
        cart_items=cart_items,
        total=total,
        wallet=WALLET_BALANCE,
        error=error
    )


@app.route('/checkout', methods=['POST'])
def checkout():
    ITEMS = get_items()
    total = 0
    bought_100_item = False

    for item_id, quantity in session['cart'].items():
        item = ITEMS.get(item_id)
        if item:
            subtotal = item['price'] * quantity
            total += subtotal
            if item['price'] == 100 and quantity > 0:
                bought_100_item = True

    if total <= 0:
        session['error'] = "Cart total must be more than $0 to proceed with checkout."
        return redirect(url_for('cart'))

    if total <= WALLET_BALANCE and bought_100_item:
        session['purchased'] = True
        return redirect(url_for('success'))
    else:
        session['error'] = "You don't have enough wallet balance, or you didn't purchase the right item."
        return redirect(url_for('cart'))

@app.route('/success')
def success():
    if session.get('purchased'):
        with open('flag.txt') as f:
            flag = f.read()
        return render_template('success.html', flag=flag)
    else:
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=False)
