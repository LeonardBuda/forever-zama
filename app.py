import os
import json
import requests
import time
from firebase_admin import credentials, initialize_app, firestore
from flask import Flask, render_template, request, jsonify, redirect, url_for, session

# Initialize Flask App
# Use environment variable for secret key for security
app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'default_fallback_secret_key') # Use an environment variable for security

# Add custom floatformat filter for Jinja2
@app.template_filter('floatformat')
def floatformat_filter(value, decimal_places=2):
    try:
        return f"{float(value):.{decimal_places}f}"
    except (ValueError, TypeError):
        return value

# Firebase Configuration
# Use environment variable for production, fallback to local file for development
cred_path = os.path.join(os.getcwd(), 'forever-zama-firebase-adminsdk-fbsvc-b267055d4b.json')
firebase_credentials = os.environ.get('FIREBASE_CREDENTIALS')

if firebase_credentials:
    print("Using Firebase credentials from environment variable.")
    cred_dict = json.loads(firebase_credentials)
    cred = credentials.Certificate(cred_dict)
elif os.path.exists(cred_path):
    print("Using local Firebase credentials file.")
    cred = credentials.Certificate(cred_path)
else:
    raise FileNotFoundError(
        "Firebase credentials not found. Set FIREBASE_CREDENTIALS environment variable "
        f"or place '{cred_path}' in the project root."
    )

firebase_app = initialize_app(cred)
db = firestore.client()

# --- Hardcoded menu data (To be migrated to Firestore) ---
menu = {
    "Health & Wellness": {
        "Supplements": [
            {"name": "Forever Active Boost", "price": 101.22, "description": "Quick energy boost, no calories, carbs, or sugar. ⚡", "id": "fab"},
            {"name": "Forever Fast Break", "price": 111.57, "description": "Nutrient-packed meal replacement. 🍽️", "id": "ffb"},
            {"name": "Nature Min", "price": 381.00, "description": "Multi-minerals for anemia, arthritis, and bone health. 🦴", "id": "nm"},
            {"name": "Absorbent-C", "price": 368.11, "description": "Supports immunity, blood pressure, and respiratory health. 🛡️", "id": "ac"},
            {"name": "Bee Pollen", "price": 328.80, "description": "Immune booster, energy enhancer, supports skin health. 🐝", "id": "bp"},
            {"name": "Forever Therm", "price": 607.73, "description": "Accelerates metabolism and reduces fatigue. 🔥", "id": "ft"},
            {"name": "Forever Lite", "price": 650.21, "description": "Supports weight loss, muscle gain, normalizes blood sugar, high in antioxidants. 🥗", "id": "fl"},
            {"name": "Lycium Plus", "price": 652.96, "description": "Supports vision, diabetes, and liver/kidney health. 👀", "id": "lp"},
            {"name": "Aloe Vera Gel", "price": 561.46, "description": "Detoxifies, controls diabetes, and boosts immunity. 🌱", "id": "avg"},
            {"name": "Royal Jelly", "price": 711.07, "description": "Hormone balance, anti-aging, immune support. 👑", "id": "rj"},
            {"name": "Aloe Berry Nectar", "price": 561.46, "description": "Supports healthy digestive system, period pains, womb problems, constipation, low blood pressure, heart issues. 🍓", "id": "abn"},
            {"name": "Forever Garlic-Thyme", "price": 390.00, "description": "Boosts immunity, supports heart and respiratory health, natural antibiotic. 🧄", "id": "fgt"},
            {"name": "Forever ImmuBlend", "price": 495.00, "description": "Immune support with vitamins C & D and zinc, full-body formula. 💪", "id": "fib"},
            {"name": "Forever Arctic Sea", "price": 638.59, "description": "Supports prostate health, cholesterol, blood pressure, cardiovascular system, skin health. 🐟", "id": "fas"},
            {"name": "Forever Freedom", "price": 802.56, "description": "Promotes joint health for sports, stroke, arthritis, gout, and muscle cramps. 🏃", "id": "ff"},
            {"name": "Aloe Blossom Herbal Tea", "price": 378.67, "description": "Caffeine-free, relieves stress, insomnia, improves digestion. ☕", "id": "abht"},
            {"name": "Bee Propolis", "price": 687.40, "description": "Boosts immunity, fights bacteria, viruses, infections, allergies, and skin diseases. 🐝", "id": "bp2"},
            {"name": "Multi Maca", "price": 569.14, "description": "Boosts energy, endurance, supports sexual health, fertility, hormonal balance. 60 tablets. 💊", "id": "mm"},
            {"name": "Forever iVision", "price": 682.19, "description": "Improves eye circulation, high in vitamins C & A, supports vision, contains bilberry, protects retina. 60 softgels. 👁️", "id": "fiv"},
            {"name": "Forever Immune Gummy", "price": 788.10, "description": "Supports immune system with 10 vitamins and zinc, tropical-flavored, vegan-friendly. 🍬", "id": "fig"},
            {"name": "Vitolize for Men", "price": 639.64, "description": "Supports fertility, PMS, urinary function, prostate health. 🧑", "id": "vfm"},
            {"name": "Vitolize for Women", "price": 677.05, "description": "Supports fertility, PMS, urinary function. 👩", "id": "vfw"},
            {"name": "Active Pro-B", "price": 783.76, "description": "Promotes healthy digestion, nutrient absorption. 🦠", "id": "apb"},
            {"name": "Forever Supergreens", "price": 820.95, "description": "Supports natural defenses, metabolism, energy levels. 🥬", "id": "fs"},
            {"name": "Forever Focus", "price": 178.31, "description": "Enhances focus, concentration, brain energy for students, athletes, professionals. 🧠", "id": "ffo"},
            {"name": "Aloe Drinks Tripack Aloe Vera Gel", "price": 1669.58, "description": "Pack of 3 x 1 litre aloe vera gel drinks. 🥤", "id": "adtavg"},
            {"name": "Aloe Drinks Tripack Variety", "price": 1669.58, "description": "Pack of 1 litre Aloe Vera Gel, Aloe Peaches, Aloe Berry Nectar. 🍹", "id": "adtav"},
            {"name": "Aloe Drinks Tripack Aloe Berry Nectar", "price": 1669.58, "description": "Pack of 3 x 1 litre aloe berry nectar. 🍓", "id": "adtabn"},
            {"name": "Forever Calcium", "price": 521.10, "description": "Supports bone and teeth health with vitamins C & D. 🦷", "id": "fc"},
            {"name": "Cardio Health", "price": 707.47, "description": "Supports heart function and blood flow. ❤️", "id": "ch"},
            {"name": "Active HA", "price": 719.31, "description": "Joint lubrication and arthritis support. 🦵", "id": "aha"},
            {"name": "ARGI+", "price": 1612.74, "description": "Anti-aging, energy, cardiovascular health. 🩺", "id": "argi"},
            {"name": "Forever Move", "price": 1332.54, "description": "Supports joint health, flexibility, cartilage, reduces stiffness. 🏋️", "id": "fm"},
            {"name": "Forever Aloe Peaches", "price": 561.46, "description": "Supports digestive health and immunity. 🍑", "id": "fap"},
            {"name": "Forever Daily", "price": 650.21, "description": "Supports general health with vitamins and minerals. 💊", "id": "fd"}
        ]
    },
    "Skincare & Personal Care": {
        "Products": [
            {"name": "Aloe & Avocado Soap", "price": 143.27, "description": "Gentle cleanser for all skin types. 🧼", "id": "aas"},
            {"name": "Aloe Moisturizing Lotion", "price": 320.56, "description": "Hydrates with collagen and elastin, maintains skin’s pH balance. 💧", "id": "aml"},
            {"name": "Aloe Ever-Shield", "price": 154.47, "description": "Aluminium-free deodorant, long-lasting, gentle, no stains. 🛡️", "id": "aes"},
            {"name": "Aloe Propolis Crème", "price": 426.22, "description": "Treats acne, eczema, burns. 🩹", "id": "apc"},
            {"name": "Aloe Jojoba Shampoo & Conditioning Rinse", "price": 495.11, "description": "Strengthens hair, relieves dandruff. 🧴", "id": "ajs"},
            {"name": "Aloe Vera Gelly", "price": 320.56, "description": "Soothes skin irritations, deep hydration, speeds healing. 🌿", "id": "avg2"},
            {"name": "Aloe Heat Lotion", "price": 320.00, "description": "Soothes muscle and joint pain, ideal for massages. 💆", "id": "ahl"},
            {"name": "Forever R3 Factor", "price": 687.40, "description": "Retains skin moisture, restores resilience with aloe vera, collagen, vitamins A & E. 🌟", "id": "frf"},
            {"name": "Replenishing Skin Oil", "price": 644.20, "description": "Nourishes skin, combats environmental stressors, suitable for dry/sensitive skin. 🛢️", "id": "rso"},
            {"name": "Aloe Scrub", "price": 338.00, "description": "Natural exfoliator, prepares skin for moisturization, promotes silky skin. ✨", "id": "as"},
            {"name": "Aloe Sunscreen", "price": 442.49, "description": "SPF 30, natural zinc oxide, water-resistant, soothes with aloe and vitamin E. ☀️", "id": "asun"},
            {"name": "Aloe Body Lotion", "price": 484.54, "description": "Promotes hydration, supports skin’s moisture barrier, non-greasy. 💦", "id": "abl"},
            {"name": "Forever Marine Collagen", "price": 1780.00, "description": "Promotes youthful skin, healthier hair, stronger nails, high in vitamins and zinc. 💅", "id": "fmc"},
            {"name": "Smoothing Exfoliator", "price": 389.03, "description": "Evens skin tone, brightens complexion, reduces dark spots. 🌞", "id": "se"},
            {"name": "Balancing Toner", "price": 463.41, "description": "Balances skin moisture for combination skin. ⚖️", "id": "bt"},
            {"name": "Awakening Eye Cream", "price": 389.03, "description": "Reduces puffiness, dark circles, wrinkles, rejuvenates eyes. 👁️", "id": "aec"},
            {"name": "Aloe Activator", "price": 341.27, "description": "Moisturizes, cleanses, soothes, used with Forever Mask for face mask. 😷", "id": "aa"},
            {"name": "Hydrating Serum", "price": 740.00, "description": "Boosts hydration with hyaluronic acid, reduces fine lines, protects skin. 💧", "id": "hs"},
            {"name": "Infinite Skin Care Kit", "price": 3440.80, "description": "Includes Hydrating Cleanser (R51.18), Firming Serum (R51.96), Firming Complex (R51.96), Restoring Crème (R1066.07). 🎁", "id": "isck"},
            {"name": "Aloe Lips", "price": 74.80, "description": "Moisturizes lips, treats dry lips, insect bites, small cuts. 💋", "id": "al"},
            {"name": "Forever Bright Toothgel", "price": 165.04, "description": "Cleans and whitens teeth, fights plaque, fluoride-free, minty taste. 🦷", "id": "fbt"},
            {"name": "Gentleman's Pride", "price": 320.56, "description": "Moisturizing aftershave, alcohol-free, masculine scent. 🧔", "id": "gp"},
            {"name": "Deodorant Sprays", "price": 138.26, "description": "Aloe-enriched, high fragrance, paraben-free, up to 1020 sprays. 🌬️", "id": "ds"},
            {"name": "MSM Gel", "price": 497.43, "description": "Soothes joints, muscles, non-staining. 🦵", "id": "msmg"},
            {"name": "Aloe Liquid Soap", "price": 399.38, "description": "Gentle cleanser, retains skin moisture, promotes hydration. 🧼", "id": "als"},
            {"name": "Aloe Body Wash", "price": 479.26, "description": "Gentle cleanser, retains skin moisture, promotes hydration. 🚿", "id": "abw"},
            {"name": "Sonya Precision Liquid Eyeliner", "price": 384.17, "description": "Rich black color, defined brush for fine lines, natural wax for thickness. 🖌️", "id": "sple"},
            {"name": "Sonya Daily Skincare System", "price": 1817.00, "description": "Balances moisture for combination skin, aloe-based, cruelty-free. 🌸", "id": "sdss"},
            {"name": "Aloe First", "price": 320.56, "description": "Soothes skin irritations, promotes healing. 🩹", "id": "af"}
        ]
    },
    "Weight Management": {
        "Products": [
            {"name": "Garcinia Plus", "price": 652.96, "description": "Reduces appetite, stabilizes blood sugar. 🍎", "id": "gp"},
            {"name": "Forever Lean", "price": 889.84, "description": "Blocks calorie absorption for weight control. ⚖️", "id": "fl2"},
            {"name": "C9 Pack", "price": 2602.10, "description": "9-day detox and weight loss program, available in Vanilla or Chocolate. 🥗", "id": "c9p"},
            {"name": "F15", "price": 3156.37, "description": "15-day natural weight loss program. 🏃", "id": "f15"},
            {"name": "Forever Fibre", "price": 612.81, "description": "Improves digestion, helps feel fuller, slows nutrient absorption. 🌾", "id": "ffib"},
            {"name": "Forever Lite", "price": 650.21, "description": "Supports weight loss, muscle gain, normalizes blood sugar, high in antioxidants. 💪", "id": "fl3"}
        ]
    },
    "Kids & Family": {
        "Products": [
            {"name": "Kids Chewables", "price": 319.72, "description": "Vitamins and minerals for children’s health. 🍬", "id": "kc"},
            {"name": "Happy Kids", "price": 319.79, "description": "General health support for children. 120 tablets. 👶", "id": "hk"},
            {"name": "Fields of Greens", "price": 274.31, "description": "Dietary supplement with barley grass and alfalfa. 80 tablets. 🥬", "id": "fog"}
        ]
    },
    "Combos": {
        "Products": [
            {"name": "Asthma Combo", "price": 0.00, "description": "Combination pack for asthma support. 🫁", "id": "acombo"},
            {"name": "Diabetes Combo", "price": 0.00, "description": "Combination pack for diabetes management. 💉", "id": "dcombo"},
            {"name": "Stroke Support Combo", "price": 0.00, "description": "Combination pack for stroke recovery support. 🩺", "id": "sscombo"},
            {"name": "Stroke Recovery Pack", "price": 0.00, "description": "Comprehensive pack for stroke recovery. 🩹", "id": "srp"},
            {"name": "Weight Gain Muscle Gain Combo", "price": 0.00, "description": "Combination pack for weight and muscle gain. 💪", "id": "wgmcombo"},
            {"name": "Health 4 Men Combo", "price": 0.00, "description": "Health support combo for men. 🧑", "id": "h4mcombo"},
            {"name": "Male Performance Combo", "price": 0.00, "description": "Performance enhancement combo for men. 💪", "id": "mpcombo"},
            {"name": "Mvusa Nduku Combo", "price": 0.00, "description": "Traditional wellness combo. 🌿", "id": "mncombo"},
            {"name": "Gentlemen\'s Combo", "price": 0.00, "description": "Gentlemen’s wellness pack. 🧔", "id": "gcombo"}
        ]
    },
    "Join Options": {
        "Products": [
            {"name": "Minimum Purchase", "price": 1584.00, "type": "Preferred Customer", "description": "Starter pack for Preferred Customers (0.25cc). 🎉", "id": "mp"},
            {"name": "Quarter Stock", "price": 2998.00, "type": "Preferred Customer", "description": "Preferred Customer pack (0.5cc). 🌟", "id": "qs"},
            {"name": "Half Stock", "price": 5125.00, "type": "Preferred Customer", "description": "Preferred Customer pack (1cc). 🚀", "id": "hs"},
            {"name": "Start Your Journey", "price": 7110.00, "type": "Full Membership", "description": "Full membership starter pack (2cc). 💼", "id": "syj"},
            {"name": "Full Stock", "price": 10150.00, "type": "Full Membership", "description": "Full membership with comprehensive inventory (4cc). 🎁", "id": "fs"}
        ]
    }
}
# --- End of Hardcoded menu data ---

# Global variables
next_order_number = 1
remembered_customer = {}

def get_product_by_name(product_name):
    """Finds a product in the menu dictionary by name."""
    for category in menu.values():
        if "Products" in category:
            for item in category["Products"]:
                if item["name"] == product_name:
                    return item
        elif isinstance(category, list): # For the 'Join Options' list
             for item in category:
                 if item["name"] == product_name:
                     return item
    return None

# Send Telegram notification
def send_telegram_notification(order_number, cart_items, customer_details, final_total, payment_method=None, special_note=None):
    # Use environment variables for bot token and chat ID for security
    bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')

    if not bot_token or not chat_id:
        print("Telegram bot token or chat ID is not set. Notification not sent.")
        return

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
@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    data = request.form
    item_name = data.get('name')
    quantity = int(data.get('quantity', 1))

    # Find the item in the hardcoded menu
    item = get_product_by_name(item_name)
    
    if not item:
        return jsonify({"error": "Item not found in menu 🚫", "popup": True}), 404

    try:
        if quantity <= 0:
            return jsonify({"error": "Quantity must be positive 🚫", "popup": True}), 400

        total = item["price"] * quantity
        cart_ref = db.collection('carts').document()
        cart_ref.set({"name": item["name"], "amount": item["price"], "quantity": quantity, "total": total})
        return jsonify({"message": f"Added {quantity} x {item['name']} to cart! 🛒", "popup": True, "refresh": True}), 200
    except ValueError as ve:
        return jsonify({"error": f"Invalid input: {str(ve)} 🚫", "popup": True}), 400
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)} 🚫", "popup": True}), 500

# Remove item from cart
@app.route('/remove_from_cart', methods=['POST'])
def remove_from_cart():
    try:
        item_name = request.form.get('name')
        if not item_name:
            return jsonify({"error": "Item name is required 🚫", "popup": True}), 400
        
        # Check if the cart has items with the same name and delete them
        cart_items = db.collection('carts').where('name', '==', item_name).get()
        if not cart_items:
            return jsonify({"error": "Item not found in cart 😞", "popup": True}), 404
        
        for doc in cart_items:
            doc.reference.delete()
            
        return jsonify({"message": f"Removed {item_name} from cart! 🗑️", "popup": True, "refresh": True}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to remove item: {str(e)} 🚫", "popup": True}), 500

# Other routes (view_cart, clear_cart, checkout, etc.) are unchanged from your previous version.

# Generic route to handle rendering other HTML files
@app.route('/<page_name>')
def render_page(page_name):
    # This is a generic route to handle rendering other HTML files
    try:
        # Prevent path traversal
        if '..' in page_name or page_name.startswith('/'):
            return 'Invalid page name', 400
        
        # Check if the template exists
        if os.path.exists(os.path.join(app.template_folder, f'{page_name}.html')):
            if page_name in ["health_wellness", "skincare_personal_care", "weight_management", "kids_family", "combos", "join_options"]:
                # The generic route can't pass specific menu data, so we need to handle this
                # This is a good opportunity to refactor and pass dynamic data from Firestore
                return render_template(f'{page_name}.html', menu=menu)
            return render_template(f'{page_name}.html')
        else:
            return render_template('404.html'), 404
    except Exception as e:
        print(f"Error rendering page: {e}")
        return render_template('500.html'), 500

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=False)