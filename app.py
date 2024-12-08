from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from flask_session import Session
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Mail, Message
import csv
import os
import uuid
import time
from datetime import datetime, timedelta


app = Flask(__name__)
app.config['SESSION_TYPE'] = 'filesystem'  # Example session type
app.config.from_object(__name__)
Session(app)
app.secret_key = 'your_secret_key'
ORDER_DIR = 'orders'
os.makedirs(ORDER_DIR, exist_ok=True)
app.config['SESSION_COOKIE_NAME'] = 'your_cookie_name'  # Define the session cookie name explicitly


# Flask-Mail configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'decobweb@gmail.com'
app.config['MAIL_PASSWORD'] = 'dqaarqodqpwgrajb'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False


mail = Mail(app)
serializer = URLSafeTimedSerializer(app.secret_key)

ADMIN_EMAIL = "cobwebb784@gmail.com"
SUBSCRIPTION_FILE = os.path.join(ORDER_DIR, 'subscriptions.csv')



# Sample product list
ROYAL_PICASSA1= {
    '1': {'name': 'ROYAL PICASSA1', 'price': 1000.00, 'no': '1'},
    '2': {'name': 'ROYAL PICASSA2', 'price': 1100.00, 'no': '2'},
    '3': {'name': 'ROYAL PICASSA3', 'price': 1200.00, 'no': '3'},
    '4': {'name': 'ROYAL PICASSA4', 'price': 1300.00, 'no': '4'},
    '5': {'name': 'ROYAL PICASSA5', 'price': 1400.00, 'no': '5'},
    '6': {'name': 'ROYAL PICASSA6', 'price': 1500.00, 'no': '6'},
}

products = {
    #'1': {'name': 'Arab', 'price': 10.00, 'no': '1',},
    #'2': {'name': 'Now', 'price': 15.00, 'no': '2',},
    #'3': {'name': 'The King', 'price': 20.00, 'no': '3',},
    #'4': {'name': 'The Queen', 'price': 30.00, 'no': '4',},
    '5': {'name': 'AUDIENCE BY VENETEY ', 'price': 8800, 'no': '5',},
    '6': {'name': 'AUDIENCE BY VENETEY ', 'price': 8800.00, 'no': '6',},
    '7': {'name': 'AUDIENCE BY VENETEY ', 'price': 8800.00, 'no': '7',},
    '8': {'name': 'AUDIENCE BY VENETEY ', 'price': 8800.00, 'no': '8',},
    '9': {'name': 'K WOOL ', 'price': 6000, 'no': '9',},
    '10': {'name': 'K WOOL ', 'price': 6000, 'no': '10',},
    '11': {'name': 'K WOOL ', 'price': 6000, 'no': '11',},
    '12': {'name': 'K WOOL ', 'price': 6000, 'no': '12',},
    '13': {'name': 'K WOOL ', 'price': 6000, 'no': '13',},
    '14': {'name': 'K WOOL ', 'price': 6000, 'no': '14',},
    '15': {'name': 'K WOOL ', 'price': 6000, 'no': '15',},
    '16': {'name': 'K WOOL ', 'price': 6000, 'no': '16',},
    '17': {'name': 'ROYAL PICASSA1', 'price': 5000.00, 'no': '17'},
    '18': {'name': 'ROYAL PICASSA2', 'price': 5000.00, 'no': '18'},
    '19': {'name': 'ROYAL PICASSA3', 'price': 5000.00, 'no': '19'},
    '20': {'name': 'ROYAL PICASSA4', 'price': 5000.00, 'no': '20'},
    '21': {'name': 'ROYAL PICASSA5', 'price': 5000.00, 'no': '21'},
    '22': {'name': 'ROYAL PICASSA6', 'price': 5000.00, 'no': '22'},
    #'17': {'name': 'K WOOL ', 'price': 6000, 'no': '17',},

}


# Ensure the CSV file exists
if not os.path.exists(SUBSCRIPTION_FILE):
    with open(SUBSCRIPTION_FILE, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['email', 'token', 'timestamp'])

def save_subscription(email, token):
    """Save email, token, and timestamp to a CSV file."""
    timestamp = time.time()  # Current time in seconds since epoch
    with open(SUBSCRIPTION_FILE, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([email, token, timestamp])


def validate_token(token):
    """Validate the token and check if it's expired."""
    if not os.path.exists(SUBSCRIPTION_FILE):
        return None

    with open(SUBSCRIPTION_FILE, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['token'] == token.strip():
                email = row['email']
                timestamp = float(row['timestamp'])
                # Check if the token is within the 5-minute window
                if time.time() - timestamp <= 300:  # 5 minutes = 300 seconds
                    return email
    return None

def save_cart_to_csv(order_code, cart):
    """Save cart information to a CSV file."""
    with open(os.path.join(ORDER_DIR, f'{order_code}.csv'), mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Product Name', 'Quantity', 'Price'])
        for product_id, quantity in cart.items():
            product = products[product_id]
            writer.writerow([product['name'], quantity, product['price']])


def update_cart_csv(order_code, cart):
    """Update CSV file when cart is modified."""
    if cart:
        save_cart_to_csv(order_code, cart)
    else:
        try:
            os.remove(os.path.join(ORDER_DIR, f'{order_code}.csv'))
        except FileNotFoundError:
            pass

@app.route('/')
def index():
    # Define the list of native product IDs
    native_ids = [ '9', '10', '11', '12', '13', '14', '15', '16','5', '6', '7', '8']

    # Check if the request is for natives
    category = request.args.get('category', 'all')
    if category == 'natives':
        filtered_products = {key: value for key, value in products.items() if key in native_ids}
    else:
        filtered_products = products

    return render_template('index.html', products=filtered_products, cart=session.get('cart', {}))


@app.route('/subscribe', methods=['POST'])
def subscribe():
    email = request.form['email']
    token = str(uuid.uuid4())  # Generate a unique token
    save_subscription(email, token)

    confirmation_link = f"http://{request.host}/confirm_subscription?token={token}"
    msg = Message("Confirm Your Subscription", sender=app.config['MAIL_USERNAME'], recipients=[email])
    msg.body = f"""
    Hi,
    Thank you for subscribing! Confirm via the link below (valid for 5 minutes):
    {confirmation_link}
    """
    mail.send(msg)
    return "A confirmation link has been sent to your email."


@app.route('/confirm_subscription')
def confirm_subscription():
    token = request.args.get('token')
    email = validate_token(token)
    if not email:
        return "Invalid or expired link.", 400

    try:
        msg = Message("New Subscription", sender=app.config['MAIL_USERNAME'], recipients=[ADMIN_EMAIL])
        msg.body = f"A new user subscribed: {email}"
        mail.send(msg)
    except Exception as e:
        print(f"Error sending email to admin: {e}")
    return render_template('subscription_success.html', email=email)




@app.route('/subscription_success')
def subscription_success():
    email = request.args.get('email', 'User')
    return render_template('subscription_success.html', email=email)



@app.route('/add_to_cartt/<product_id>', methods=['POST'])
def add_to_cartt(product_id):
    if 'cart' not in session:
        session['cart'] = {}

    # Increase quantity or add new product
    session['cart'][product_id] = session['cart'].get(product_id, 0) + 1

    # Debugging: Print current cart status
    print("Cart after adding:", session['cart'])

    if 'order_code' in session:
        update_cart_csv(session['order_code'], session['cart'])

    # Return the updated cart as JSON
    return jsonify(cart=session['cart'])


# Route to render the contact form
@app.route('/contact', methods=['GET'])
def contact():
    return render_template('contact.html')

# Route to handle form submission
@app.route('/contact', methods=['POST'])
def handle_contact():
    # Retrieve form data
    name = request.form.get('name')
    email = request.form.get('email')
    message = request.form.get('message')

    if not name or not email or not message:
        flash("All fields are required!", "danger")
        return render_template('contact.html')

    # Send email to admin
    try:
        msg = Message(
            subject="New Contact Form Submission",
            recipients=['sadiqabuidris@gmail.com'],  # Replace with the admin's email
            body=f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}"
        )
        mail.send(msg)
        flash("Your message has been sent successfully!", "success")
    except Exception as e:
        print(f"Error sending email: {e}")
        flash("There was an error sending your message. Please try again later.", "danger")

    return render_template('contact.html')


@app.route('/add_to_cart/<product_id>', methods=['POST'])
def add_to_cart(product_id):
    if 'cart' not in session:
        session['cart'] = {}

    # Increase quantity or add new product
    session['cart'][product_id] = session['cart'].get(product_id, 0) + 1

    # Debugging: Print current cart status
    print("Cart after adding:", session['cart'])

    if 'order_code' in session:
        update_cart_csv(session['order_code'], session['cart'])

    # Return the updated cart as JSON
    return jsonify(cart=session['cart'])



@app.route('/update_cart/<product_id>/<int:quantity>', methods=['POST'])
def update_cart(product_id, quantity):
    if 'cart' not in session:
        session['cart'] = {}

    if quantity > 0:
        session['cart'][product_id] = quantity
    else:
        session.pop(product_id, None)

    # Update the CSV if needed
    if 'order_code' in session:
        update_cart_csv(session['order_code'], session['cart'])

    # Return updated cart for potential frontend use
    return jsonify(cart=session['cart'])


@app.route('/view_selected_items', methods=['GET', 'POST'])
def view_selected_items():
    selected_items = []
    if request.method == 'POST':
        # Get the comma-separated IDs from the admin
        raw_ids = request.form.get('product_ids', '')
        ids = raw_ids.split(',')

        # Fetch the products corresponding to the IDs
        for product_id in ids:
            product_id = product_id.strip()  # Remove any extra spaces
            if product_id in products:
                product = products[product_id]
                selected_items.append({
                    'id': product_id,
                    'name': product['name'],
                    'price': product['price'],
                    'image': f"img/ROYAL_PICASSA{product['no']}.jpg" if product['name'].startswith("ROYAL PICASSA")
                             else f"img/Spray_{product['no']}.jpg"
                })

    return render_template('view_selected_items.html', selected_items=selected_items)



@app.route('/remove_from_cart/<product_id>', methods=['POST'])
def remove_from_cart(product_id):
    if 'cart' in session and product_id in session['cart']:
        # Remove the product from the cart
        del session['cart'][product_id]

        # Debugging: Print current cart status
        print("Cart after removing:", session['cart'])

        if 'order_code' in session:
            update_cart_csv(session['order_code'], session['cart'])

    return '', 204  # No content response


@app.route('/remove_from_cartt/<product_id>')
def remove_from_cartt(product_id):
    if 'cart' in session and product_id in session['cart']:
        if session['cart'][product_id] > 1:
            session['cart'][product_id] -= 1
        else:
            del session['cart'][product_id]

        # Debugging: Print current cart status
        print("Cart after removing:", session['cart'])

        if 'order_code' in session:
            update_cart_csv(session['order_code'], session['cart'])
    return redirect(url_for('cart'))


@app.route('/cart')
def cart():
    if 'cart' not in session:
        return redirect(url_for('index'))

    # Remove invalid product IDs from the cart
    session['cart'] = {pid: qty for pid, qty in session['cart'].items() if pid in products}

    subtotal = sum(products[pid]['price'] * qty for pid, qty in session['cart'].items())
    shipping = 3.00
    total = subtotal + shipping

    return render_template('cart.html', cart=session['cart'], products=products,
                           subtotal=f"{subtotal:.2f}", shipping=f"{shipping:.2f}", total=f"{total:.2f}")

@app.route('/checkout', methods=['GET'])
def checkout():
    # Assuming 'cart' contains the items selected by the user with their quantities
    cart = session.get('cart', {})
    subtotal = sum(products[item_id]['price'] * quantity for item_id, quantity in cart.items())
    shipping = 500  # Example flat rate for shipping
    total = subtotal + shipping

    # Build the order details
    order_details = []
    id_list = []

    for item_id, quantity in cart.items():
        product = products[item_id]
        order_details.append(f"- {product['name']} (ID: {item_id}) x{quantity}")
        id_list.append(str(item_id))

    order_message = (
        "Order Details:\n"
        + "\n".join(order_details)
        + f"\nTotal: ₦{total:,.2f}\n"
        + f"Ids= {','.join(id_list)},"
    )

    # Perform replacements outside the f-string
    formatted_message = order_message.replace(' ', '%20').replace('\n', '%0A')

    # Use the processed string in the f-string
    whatsapp_link = f"https://wa.me/2348155114430?text={formatted_message}"

    # Redirect to the WhatsApp link
    return redirect(whatsapp_link)


@app.route('/clear_order')
def clear_session():
    session.clear()

    return render_template('index.html', products=products)


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    order_details = []
    total_amount = 0

    if request.method == 'POST':
        order_code = request.form['order_code']
        print(f"Received order code: {order_code}")

        # Read the order details from the CSV file
        order_file = os.path.join(ORDER_DIR, f'{order_code}.csv')
        if os.path.exists(order_file):
            with open(order_file, mode='r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    order_details.append({
                        'name': row['Product Name'],
                        'price': float(row['Price']),
                        'quantity': int(row['Quantity'])
                    })
                    total_amount += float(row['Price']) * int(row['Quantity'])
        else:
            print("Order code does not exist.")

    return render_template('admin.html', order_code=request.form.get('order_code'), order_details=order_details,
                           total_amount=total_amount)

if __name__ == '__main__':
    app.run(debug=True)

