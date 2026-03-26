import os
import random
import requests
from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'turkmen_biz_2026'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///turkmen_biz.db'

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# --- TRANSLATIONS ---
TRANSLATIONS = {
    'tm': {
        'home': 'Baş sahypa', 'culture': 'Medeniýet', 'cart': 'Sebet', 'settings': 'Sazlamalar',
        'add_to_cart': 'Sebede goş', 'added': 'sebede goşuldy!', 'total': 'Jemi',
        'checkout': 'Sargydy tassykla', 'empty': 'Sebediňiz boş.', 'delivery': 'Eltip bermek dowam edýär!',
        'login': 'Giriş', 'join': 'Agza bol', 'logout': 'Çykyş'
    },
    'en': {
        'home': 'Home', 'culture': 'Culture', 'cart': 'Cart', 'settings': 'Settings',
        'add_to_cart': 'Add to Cart', 'added': 'added to cart!', 'total': 'Total',
        'checkout': 'Proceed to Checkout', 'empty': 'Your cart is empty.', 'delivery': 'Delivery is in process!',
        'login': 'Login', 'join': 'Join', 'logout': 'Logout'
    },
    'ru': {
        'home': 'Главная', 'culture': 'Культура', 'cart': 'Корзина', 'settings': 'Настройки',
        'add_to_cart': 'В корзину', 'added': 'добавлено в корзину!', 'total': 'Итого',
        'checkout': 'Оформить заказ', 'empty': 'Ваша корзина пуста.', 'delivery': 'Доставка в процессе!',
        'login': 'Войти', 'join': 'Регистрация', 'logout': 'Выйти'
    }
}

@app.context_processor
def inject_lang():
    lang = session.get('lang', 'tm')
    return dict(lang=TRANSLATIONS[lang])

@app.route('/set_lang/<l>')
def set_lang(l):
    if l in ['tm', 'en', 'ru']:
        session['lang'] = l
    return redirect(request.referrer or url_for('home'))

# --- MODELS ---
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    dark_mode = db.Column(db.Boolean, default=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- DATA ---
CATEGORIES = ["Tahýa", "Carpets", "Accessories", "Women", "Men"]
IMG_URLS = {
    "Tahýa": "https://images.unsplash.com/photo-1590736912183-7d6182f978ad?w=500",
    "Carpets": "https://images.unsplash.com/photo-1576016773942-3344d5cf11b7?w=500",
    "Accessories": "https://images.unsplash.com/photo-1611591437281-460bfbe1220a?w=500",
    "Women": "https://images.unsplash.com/photo-1528459801416-a9e53bbf4e17?w=500",
    "Men": "https://images.unsplash.com/photo-1507679799987-c73779587ccf?w=500"
}

PRODUCTS = []
for i in range(200):
    cat = CATEGORIES[i % len(CATEGORIES)]
    PRODUCTS.append({
        "id": i,
        "name": f"Turkmen {cat} #{i+1}",
        "category": cat,
        "price": 40 + (i % 20) * 10,
        "img": IMG_URLS[cat],
        "desc": f"Ýokary hilli {cat} önümi. Traditionally crafted in Turkmenistan."
    })

# --- ROUTES ---
@app.route('/')
def home():
    cat = request.args.get('category')
    items = [p for p in PRODUCTS if p['category'] == cat] if cat else PRODUCTS
    return render_template('index.html', products=items, categories=CATEGORIES)

@app.route('/culture')
def culture():
    try:
        r = requests.get("https://en.wikipedia.org/api/rest_v1/page/summary/Culture_of_Turkmenistan")
        info = r.json().get('extract', 'Turkmen culture is famous for its hospitality.')
    except:
        info = "Culture info is currently offline."
    return render_template('culture.html', info=info)

@app.route('/product/<int:pid>')
def product_detail(pid):
    p = next((i for i in PRODUCTS if i['id'] == pid), None)
    return render_template('product.html', product=p)

@app.route('/add_to_cart/<int:pid>', methods=['POST'])
@login_required
def add_to_cart(pid):
    if 'cart' not in session:
        session['cart'] = []
    p = next((i for i in PRODUCTS if i['id'] == pid), None)
    if p:
        session['cart'].append(pid)
        session.modified = True
        flash(f"{p['name']} {TRANSLATIONS[session.get('lang', 'tm')]['added']}")
    # Redirect directly to cart to "proceed"
    return redirect(url_for('cart'))

@app.route('/cart')
@login_required
def cart():
    cart_ids = session.get('cart', [])
    items = [p for p in PRODUCTS if p['id'] in cart_ids]
    total = sum(i['price'] for i in items)
    return render_template('cart.html', items=items, total=total)

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        current_user.dark_mode = not current_user.dark_mode
        db.session.commit()
        return redirect(url_for('settings'))
    return render_template('settings.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and check_password_hash(user.password, request.form['password']):
            login_user(user)
            return redirect(url_for('home'))
        flash("Error")
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        pw = generate_password_hash(request.form['password'], method='pbkdf2:sha256')
        u = User(username=request.form['username'], password=pw)
        db.session.add(u)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)