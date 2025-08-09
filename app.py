from flask import Flask, render_template, request, jsonify, redirect, url_for
import os
import json
import requests
import time
from firebase_admin import credentials, initialize_app, firestore

# Initialize Flask app
app = Flask(__name__, static_folder='static', template_folder='templates')

# Add custom floatformat filter for Jinja2
def floatformat(value, decimal_places=2):
    try:
        return f"{float(value):.{decimal_places}f}"
    except (ValueError, TypeError):
        return value

app.jinja_env.filters['floatformat'] = floatformat

# Initialize Firebase
firebase_credentials = os.environ.get('FIREBASE_CREDENTIALS')
if firebase_credentials:
    cred = credentials.Certificate(json.loads(firebase_credentials))
else:
    cred_path = 'forever-zama-firebase-adminsdk.json'
    if os.path.exists(cred_path):
        cred = credentials.Certificate(cred_path)
    else:
        raise FileNotFoundError(f"Firebase credentials file '{cred_path}' not found.")
firebase_app = initialize_app(cred)
db = firestore.client()

# Clear cart on startup to remove default items
for doc in db.collection('carts').get():
    doc.reference.delete()

# Menu data updated with PDF catalog (March 2025) and new Combos category
menu = {
    "Health & Wellness": {
        "Supplements": [
            {"name": "Forever Active Boost", "price": 101.22, "description": "Quick energy boost, no calories, carbs, or sugar. ⚡"},
            {"name": "Forever Fast Break", "price": 111.57, "description": "Nutrient-packed meal replacement. 🍽️"},
            {"name": "Nature Min", "price": 381.00, "description": "Multi-minerals for anemia, arthritis, and bone health. 🦴"},
            {"name": "Absorbent-C", "price": 368.11, "description": "Supports immunity, blood pressure, and respiratory health. 🛡️"},
            {"name": "Bee Pollen", "price": 328.80, "description": "Immune booster, energy enhancer, supports skin health. 🐝"},
            {"name": "Forever Therm", "price": 607.73, "description": "Accelerates metabolism and reduces fatigue. 🔥"},
            {"name": "Forever Lite", "price": 650.21, "description": "Supports weight loss, muscle gain, normalizes blood sugar, high in antioxidants. 🥗"},
            {"name": "Lycium Plus", "price": 652.96, "description": "Supports vision, diabetes, and liver/kidney health. 👀"},
            {"name": "Aloe Vera Gel", "price": 561.46, "description": "Detoxifies, controls diabetes, and boosts immunity. 🌱"},
            {"name": "Royal Jelly", "price": 711.07, "description": "Hormone balance, anti-aging, immune support. 👑"},
            {"name": "Aloe Berry Nectar", "price": 561.46, "description": "Supports healthy digestive system, period pains, womb problems, constipation, low blood pressure, heart issues. 🍓"},
            {"name": "Forever Garlic-Thyme", "price": 390.00, "description": "Boosts immunity, supports heart and respiratory health, natural antibiotic. 🧄"},
            {"name": "Forever ImmuBlend", "price": 495.00, "description": "Immune support with vitamins C & D and zinc, full-body formula. 💪"},
            {"name": "Forever Arctic Sea", "price": 659.09, "description": "Supports prostate health, cholesterol, blood pressure, cardiovascular system, skin health. 🐟"},
            {"name": "Forever Freedom", "price": 802.56, "description": "Promotes joint health for sports, stroke, arthritis, gout, and muscle cramps. 🏃"},
            {"name": "Aloe Blossom Herbal Tea", "price": 378.67, "description": "Caffeine-free, relieves stress, insomnia, improves digestion. ☕"},
            {"name": "Bee Propolis", "price": 687.40, "description": "Boosts immunity, fights bacteria, viruses, infections, allergies, and skin diseases. 🐝"},
            {"name": "Multi Maca", "price": 569.14, "description": "Boosts energy, endurance, supports sexual health, fertility, hormonal balance. 60 tablets. 💊"},
            {"name": "Forever iVision", "price": 682.19, "description": "Improves eye circulation, high in vitamins C & A, supports vision, contains bilberry, protects retina. 60 softgels. 👁️"},
            {"name": "Forever Immune Gummy", "price": 788.10, "description": "Supports immune system with 10 vitamins and zinc, tropical-flavored, vegan-friendly. 🍬"},
            {"name": "Vitolize for Men", "price": 639.64, "description": "Supports fertility, PMS, urinary function, prostate health. 🧑"},
            {"name": "Vitolize for Women", "price": 677.05, "description": "Supports fertility, PMS, urinary function. 👩"},
            {"name": "Active Pro-B", "price": 783.76, "description": "Promotes healthy digestion, nutrient absorption. 🦠"},
            {"name": "Forever Supergreens", "price": 820.95, "description": "Supports natural defenses, metabolism, energy levels. 🥬"},
            {"name": "Forever Focus", "price": 178.31, "description": "Enhances focus, concentration, brain energy for students, athletes, professionals. 🧠"},
            {"name": "Aloe Drinks Tripack Aloe Vera Gel", "price": 1669.58, "description": "Pack of 3 x 1 litre aloe vera gel drinks. 🥤"},
            {"name": "Aloe Drinks Tripack Variety", "price": 1669.58, "description": "Pack of 1 litre Aloe Vera Gel, Aloe Peaches, Aloe Berry Nectar. 🍹"},
            {"name": "Aloe Drinks Tripack Aloe Berry Nectar", "price": 1669.58, "description": "Pack of 3 x 1 litre aloe berry nectar. 🍓"},
            {"name": "Forever Calcium", "price": 521.10, "description": "Supports bone and teeth health with vitamins C & D. 🦷"},
            {"name": "Cardio Health", "price": 707.47, "description": "Supports heart function and blood flow. ❤️"},
            {"name": "Active HA", "price": 719.31, "description": "Joint lubrication and arthritis support. 🦵"},
            {"name": "ARGI+", "price": 1612.74, "description": "Anti-aging, energy, cardiovascular health. 🩺"},
            {"name": "Forever Move", "price": 1332.54, "description": "Supports joint health, flexibility, cartilage, reduces stiffness. 🏋️"},
            {"name": "Forever Aloe Peaches", "price": 547.30, "description": "Supports digestive health and immunity. 🍑"},
            {"name": "Forever Daily", "price": 426.43, "description": "Supports general health with vitamins and minerals. 💊"}
        ]
    },
    "Skincare & Personal Care": {
        "Products": [
            {"name": "Aloe & Avocado Soap", "price": 143.27, "description": "Gentle cleanser for all skin types. 🧼"},
            {"name": "Aloe Moisturizing Lotion", "price": 320.56, "description": "Hydrates with collagen and elastin, maintains skin’s pH balance. 💧"},
            {"name": "Aloe Ever-Shield", "price": 154.47, "description": "Aluminium-free deodorant, long-lasting, gentle, no stains. 🛡️"},
            {"name": "Aloe Propolis Crème", "price": 426.22, "description": "Treats acne, eczema, burns. 🩹"},
            {"name": "Aloe Jojoba Shampoo & Conditioning Rinse", "price": 495.11, "description": "Strengthens hair, relieves dandruff. 🧴"},
            {"name": "Aloe Vera Gelly", "price": 320.56, "description": "Soothes skin irritations, deep hydration, speeds healing. 🌿"},
            {"name": "Aloe Heat Lotion", "price": 320.00, "description": "Soothes muscle and joint pain, ideal for massages. 💆"},
            {"name": "Forever R3 Factor", "price": 687.40, "description": "Retains skin moisture, restores resilience with aloe vera, collagen, vitamins A & E. 🌟"},
            {"name": "Replenishing Skin Oil", "price": 644.20, "description": "Nourishes skin, combats environmental stressors, suitable for dry/sensitive skin. 🛢️"},
            {"name": "Aloe Scrub", "price": 338.00, "description": "Natural exfoliator, prepares skin for moisturization, promotes silky skin. ✨"},
            {"name": "Aloe Sunscreen", "price": 442.49, "description": "SPF 30, natural zinc oxide, water-resistant, soothes with aloe and vitamin E. ☀️"},
            {"name": "Aloe Body Lotion", "price": 484.54, "description": "Promotes hydration, supports skin’s moisture barrier, non-greasy. 💦"},
            {"name": "Forever Marine Collagen", "price": 1780.00, "description": "Promotes youthful skin, healthier hair, stronger nails, high in vitamins and zinc. 💅"},
            {"name": "Smoothing Exfoliator", "price": 389.03, "description": "Evens skin tone, brightens complexion, reduces dark spots. 🌞"},
            {"name": "Balancing Toner", "price": 463.41, "description": "Balances skin moisture for combination skin. ⚖️"},
            {"name": "Awakening Eye Cream", "price": 389.03, "description": "Reduces puffiness, dark circles, wrinkles, rejuvenates eyes. 👁️"},
            {"name": "Aloe Activator", "price": 341.27, "description": "Moisturizes, cleanses, soothes, used with Forever Mask for face mask. 😷"},
            {"name": "Hydrating Serum", "price": 740.00, "description": "Boosts hydration with hyaluronic acid, reduces fine lines, protects skin. 💧"},
            {"name": "Infinite Skin Care Kit", "price": 3440.80, "description": "Includes Hydrating Cleanser (R51.18), Firming Serum (R51.96), Firming Complex (R51.96), Restoring Crème (R1066.07). 🎁"},
            {"name": "Aloe Lips", "price": 74.80, "description": "Moisturizes lips, treats dry lips, insect bites, small cuts. 💋"},
            {"name": "Forever Bright Toothgel", "price": 165.04, "description": "Cleans and whitens teeth, fights plaque, fluoride-free, minty taste. 🦷"},
            {"name": "Gentleman\'s Pride", "price": 320.56, "description": "Moisturizing aftershave, alcohol-free, masculine scent. 🧔"},
            {"name": "Deodorant Sprays", "price": 138.26, "description": "Aloe-enriched, high fragrance, paraben-free, up to 1020 sprays. 🌬️"},
            {"name": "MSM Gel", "price": 497.43, "description": "Soothes joints, muscles, non-staining. 🦵"},
            {"name": "Aloe Liquid Soap", "price": 399.38, "description": "Gentle cleanser, retains skin moisture, promotes hydration. 🧼"},
            {"name": "Aloe Body Wash", "price": 479.26, "description": "Gentle cleanser, retains skin moisture, promotes hydration. 🚿"},
            {"name": "Sonya Precision Liquid Eyeliner", "price": 384.17, "description": "Rich black color, defined brush for fine lines, natural wax for thickness. 🖌️"},
            {"name": "Sonya Daily Skincare System", "price": 1817.00, "description": "Balances moisture for combination skin, aloe-based, cruelty-free. 🌸"},
            {"name": "Aloe First", "price": 422.63, "description": "Soothes skin irritations, promotes healing. 🩹"}
        ]
    },
    "Weight Management": {
        "Products": [
            {"name": "Garcinia Plus", "price": 652.96, "description": "Reduces appetite, stabilizes blood sugar. 🍎"},
            {"name": "Forever Lean", "price": 889.84, "description": "Blocks calorie absorption for weight control. ⚖️"},
            {"name": "C9 Pack", "price": 2602.10, "description": "9-day detox and weight loss program, available in Vanilla or Chocolate. 🥗"},
            {"name": "F15", "price": 3156.37, "description": "15-day natural weight loss program. 🏃"},
            {"name": "Forever Fibre", "price": 612.81, "description": "Improves digestion, helps feel fuller, slows nutrient absorption. 🌾"},
            {"name": "Forever Lite", "price": 650.21, "description": "Supports weight loss, muscle gain, normalizes blood sugar, high in antioxidants. 💪"}
        ]
    },
    "Kids & Family": {
        "Products": [
            {"name": "Kids Chewables", "price": 319.72, "description": "Vitamins and minerals for children’s health. 🍬"},
            {"name": "Happy Kids", "price": 319.79, "description": "General health support for children. 120 tablets. 👶"},
            {"name": "Fields of Greens", "price": 274.31, "description": "Dietary supplement with barley grass and alfalfa. 80 tablets. 🥬"}
        ]
    },
    "Combos": {
        "Products": [
            {"name": "Asthma Combo", "price": 0.00, "description": "Combination pack for asthma support. 🫁"},
            {"name": "Diabetes Combo", "price": 0.00, "description": "Combination pack for diabetes management. 💉"},
            {"name": "Stroke Support Combo", "price": 0.00, "description": "Combination pack for stroke recovery support. 🩺"},
            {"name": "Stroke Recovery Pack", "price": 0.00, "description": "Comprehensive pack for stroke recovery. 🩹"},
            {"name": "Weight Gain Muscle Gain Combo", "price": 0.00, "description": "Combination pack for weight and muscle gain. 💪"},
            {"name": "Health 4 Men Combo", "price": 0.00, "description": "Health support combo for men. 🧑"},
            {"name": "Male Performance Combo", "price": 0.00, "description": "Performance enhancement combo for men. 💪"},
            {"name": "Mvusa Nduku Combo", "price": 0.00, "description": "Traditional wellness combo. 🌿"},
            {"name": "Gentlemen\'s Combo", "price": 0.00, "description": "Gentlemen’s wellness pack. 🧔"}
        ]
    },
    "Join Options": [
        {"name": "Minimum Purchase", "price": 1584.00, "type": "Preferred Customer", "description": "Starter pack for Preferred Customers (0.25cc). 🎉"},
        {"name": "Quarter Stock", "price": 2998.00, "type": "Preferred Customer", "description": "Preferred Customer pack (0.5cc). 🌟"},
        {"name": "Half Stock", "price": 5125.00, "type": "Preferred Customer", "description": "Preferred Customer pack (1cc). 🚀"},
        {"name": "Start Your Journey", "price": 7110.00, "type": "Full Membership", "description": "Full membership starter pack (2cc). 💼"},
        {"name": "Full Stock", "price": 10150.00, "type": "Full Membership", "description": "Full membership with comprehensive inventory (4cc). 🎁"}
    ]
}

# Global variables
used_order_numbers = set()
next_order_number = 1
remembered_customer = {}

# Generate unique order number
def generate_order_number():
    global next_order_number
    order_number = f"#{next_order_number:04d}"
    next_order_number += 1
    return order_number

# Send Telegram notification
def send_telegram_notification(order_number, cart_items, customer_details, final_total, payment_method=None, special_note=None):
    bot_token = "7587815614:AAFnVVfaWqNjtmHWuIB88azzEU-vx0lKQak"
    chat_id = "-4891155078"
    message = f"Order Number: {order_number}\n\nCustomer Details:\nName: {customer_details['name']}\nSurname: {customer_details.get('surname', 'N/A')}\nPhone: {customer_details['phone']}\nEmail: {customer_details['email']}\n"
    if special_note:
        message += f"Special Note: {special_note}\n"
    message += "\nOrder Details:\n"
    for item in cart_items:
        if 'quantity' in item:
            message += f"{item['name']} - R{item['amount']:.2f} x {item['quantity']} = R{item['total']:.2f}\n"
        else:
            message += f"{item['name']} - R{item['amount']:.2f}\n"
    message += f"\nPayment Method: {payment_method}\nTotal: R{final_total:.2f}\nTime: {time.strftime('%I:%M %p SAST, %B %d, %Y')}"
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    params = {"chat_id": chat_id, "text": message}
    try:
        response = requests.post(url, data=params, timeout=10)
        if response.status_code == 200 and response.json().get("ok"):
            print("Notification sent successfully! 🌟")
        else:
            print(f"Failed to send notification: {response.text}")
    except Exception as e:
        print(f"Failed to send notification: {e}")

# Placeholder payment processing
def process_payment(total, payment_method, order_number):
    print(f"Processing payment of R{total:.2f} via {payment_method} for order {order_number}... 💸")
    return True

# Add fixed-price item
def add_fixed_price_item(item, quantity):
    total = item["price"] * quantity
    cart_ref = db.collection('carts').document()
    cart_ref.set({"name": item["name"], "amount": item["price"], "quantity": quantity, "total": total})
    return f"Added {quantity} x {item['name']} to cart! 🛒"

# Remove item from cart
@app.route('/remove_from_cart', methods=['POST'])
def remove_from_cart():
    try:
        item_name = request.form.get('name')
        if not item_name:
            return jsonify({"error": "Item name is required 🚫", "popup": True}), 400
        cart_items = [doc for doc in db.collection('carts').where('name', '==', item_name).get()]
        if not cart_items:
            return jsonify({"error": "Item not found in cart 😞", "popup": True}), 404
        for doc in cart_items:
            doc.reference.delete()
        return jsonify({"message": f"Removed {item_name} from cart! 🗑️", "popup": True, "refresh": True}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to remove item: {str(e)} 🚫", "popup": True}), 500

# Routes
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/menus')
def menus():
    return render_template('menus.html', menu=menu)

@app.route('/health_wellness')
def health_wellness():
    return render_template('health_wellness.html', menu=menu["Health & Wellness"])

@app.route('/skincare_personal_care')
def skincare_personal_care():
    return render_template('skincare_personal_care.html', menu=menu["Skincare & Personal Care"])

@app.route('/weight_management')
def weight_management():
    return render_template('weight_management.html', menu=menu["Weight Management"])

@app.route('/kids_family')
def kids_family():
    return render_template('kids_family.html', menu=menu["Kids & Family"])

@app.route('/combos')
def combos():
    return render_template('combos.html', menu=menu["Combos"])

@app.route('/join_options')
def join_options():
    return render_template('business_packages.html', menu=menu["Join Options"])

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    data = request.form
    item_name = data.get('name')
    quantity = int(data.get('quantity', 1))

    item = None
    for category in menu.values():
        if isinstance(category, list):  # For Join Options
            for i in category:
                if i['name'] == item_name:
                    item = i
                    break
        else:
            for subcat, items in category.items():
                for i in items:
                    if i['name'] == item_name:
                        item = i
                        break
                if item:
                    break
        if item:
            break

    if not item:
        return jsonify({"error": "Item not found in menu 🚫", "popup": True}), 404

    try:
        if quantity <= 0:
            return jsonify({"error": "Quantity must be positive 🚫", "popup": True}), 400

        message = add_fixed_price_item(item, quantity)
        return jsonify({"message": message, "popup": True, "refresh": True}), 200
    except ValueError as ve:
        return jsonify({"error": f"Invalid input: {str(ve)} 🚫", "popup": True}), 400
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)} 🚫", "popup": True}), 500

@app.route('/view_cart')
def view_cart():
    try:
        cart_items = [doc.to_dict() for doc in db.collection('carts').get()]
        total = sum(item['total'] if 'total' in item else item['amount'] for item in cart_items)
        return render_template('cart.html', cart_items=cart_items, total=total)
    except Exception as e:
        return redirect(url_for('menus'))  # Fallback to menus if error occurs

@app.route('/clear_cart')
def clear_cart():
    try:
        for doc in db.collection('carts').get():
            doc.reference.delete()
        return jsonify({"message": "Cart cleared! 🗑️", "popup": True, "redirect": url_for('view_cart')}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to clear cart: {str(e)} 🚫", "popup": True}), 500

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if request.method == 'POST':
        try:
            name = request.form['name'].strip()
            phone = request.form['phone'].strip()
            email = request.form['email'].strip()
            surname = request.form.get('surname', '').strip() or 'N/A'
            payment_method = request.form.get('payment_method')
            special_note = request.form.get('special_note', '').strip()
            remember = bool(request.form.get('remember'))

            if not name or not phone or not email:
                return jsonify({"error": "Name, phone, and email are required 🚫", "popup": True}), 400
            if not payment_method:
                return jsonify({"error": "Payment method is required 🚫", "popup": True}), 400
            if payment_method not in ["E-wallet", "Cash send", "In-App"]:
                return jsonify({"error": "Invalid payment method 🚫", "popup": True}), 400
            if payment_method in ["In-App", "EFT"]:
                return jsonify({"error": f"{payment_method} payment is coming soon and not available yet 🚧", "popup": True}), 400

            if remember:
                remembered_customer.update({"name": name, "surname": surname, "phone": phone, "email": email, "remembered": True})

            customer_details = {"name": name, "surname": surname, "phone": phone, "email": email}
            cart_items = [doc.to_dict() for doc in db.collection('carts').get()]
            final_total = sum(item['total'] if 'total' in item else item['amount'] for item in cart_items)

            if not cart_items:
                return jsonify({"error": "Cart is empty 😞", "popup": True}), 400

            order_number = generate_order_number()
            send_telegram_notification(order_number, cart_items, customer_details, final_total, payment_method=payment_method, special_note=special_note)
            process_payment(final_total, payment_method, order_number)
            for doc in db.collection('carts').get():
                doc.reference.delete()
            return jsonify({"message": f"Collection order {order_number} placed! Total: R{final_total:.2f} 🎉", "cart_items": cart_items, "total": final_total, "popup": True, "redirect": url_for('view_cart')}), 200
        except ValueError as ve:
            return jsonify({"error": f"Invalid input: {str(ve)} 🚫", "popup": True}), 400
        except Exception as e:
            return jsonify({"error": f"Checkout failed: {str(e)} 🚫", "popup": True}), 500

    try:
        cart_items = [doc.to_dict() for doc in db.collection('carts').get()]
        total = sum(item['total'] if 'total' in item else item['amount'] for item in cart_items)
        return render_template('checkout.html', cart_items=cart_items, total=total, remembered_customer=remembered_customer)
    except Exception as e:
        return jsonify({"error": f"Failed to load checkout: {str(e)} 🚫", "popup": True}), 500

@app.route('/join', methods=['GET', 'POST'])
def join():
    if request.method == 'POST':
        try:
            name = request.form['name'].strip()
            phone = request.form['phone'].strip()
            email = request.form['email'].strip()
            package = request.form.get('package')
            if not name or not phone or not email or not package:
                return jsonify({"error": "All fields are required 🚫", "popup": True}), 400

            db.collection('join_requests').document().set({"name": name, "phone": phone, "email": email, "package": package, "timestamp": time.time()})
            message = f"New Join Request\nName: {name}\nPhone: {phone}\nEmail: {email}\nPackage: {package}\nTime: {time.strftime('%I:%M %p SAST, %B %d, %Y')}\nContact Zama Sibiya to finalize! 📝"
            send_telegram_notification(order_number=None, cart_items=[], customer_details={"name": name, "phone": phone, "email": email}, final_total=0, payment_method=None, special_note=message)
            return jsonify({"message": "Join request submitted! Zama will contact you soon. 🎉", "popup": True}), 200
        except Exception as e:
            return jsonify({"error": f"Join request failed: {str(e)} 🚫", "popup": True}), 500
    return render_template('join.html', menu=menu["Join Options"])

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        try:
            name = request.form['name'].strip()
            phone = request.form['phone'].strip()
            email = request.form['email'].strip()
            message = request.form['message'].strip()
            if not name or not phone or not email or not message:
                return jsonify({"error": "All fields are required 🚫", "popup": True}), 400
            db.collection('contacts').document().set({"name": name, "phone": phone, "email": email, "message": message, "timestamp": time.time()})
            message_text = f"New Contact Message\nName: {name}\nPhone: {phone}\nEmail: {email}\nMessage: {message}\nTime: {time.strftime('%I:%M %p SAST, %B %d, %Y')} 📬"
            send_telegram_notification(order_number=None, cart_items=[], customer_details={"name": name, "phone": phone, "email": email}, final_total=0, payment_method=None, special_note=message_text)
            return jsonify({"message": "Message sent successfully! 🎉", "popup": True}), 200
        except Exception as e:
            return jsonify({"error": f"Contact submission failed: {str(e)} 🚫", "popup": True}), 500
    return render_template('contact.html')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=False)