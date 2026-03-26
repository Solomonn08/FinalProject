import os
import random
import requests
from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_babel import Babel, gettext as _
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'turkmen_biz_2026'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///turkmen_biz.db'

# Flask-Babel configuration
app.config['BABEL_DEFAULT_LOCALE'] = 'en'
app.config['BABEL_DEFAULT_TIMEZONE'] = 'UTC'

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Language detection function
def get_locale():
    # Check URL parameter first
    lang = request.args.get('lang')
    if lang and lang in ['en', 'ru', 'tk']:
        session['language'] = lang
        return lang
    
    # Check session
    if 'language' in session:
        return session['language']
    
    # Check browser preference
    return request.accept_languages.best_match(['en', 'ru', 'tk'], default='en')

# Initialize Flask-Babel with locale selector function
babel = Babel()
babel.init_app(app, locale_selector=get_locale)

# Make translation functions available in templates
@app.context_processor
def inject_translation_functions():
    return {
        'get_translated_product_name': get_translated_product_name,
        'get_translated_product_description': get_translated_product_description
    }

# --- MODELS ---
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    dark_mode = db.Column(db.Boolean, default=False)

# --- USER LOADER ---
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Убедись, что эта строка есть и она НЕ внутри фигурных скобок {}
CATEGORIES = ["Tahýa", "Carpets", "Bags", "Accessories", "Women", "Men", "Headwear", "Traditional"]

PRODUCTS = [
    # Tahýa products
    {
        "id": 1, 
        "name": "Traditional Tahýa", 
        "category": "Tahýa", 
        "subcategory": "Traditional", 
        "price": 250, 
        "img": "/static/images/tahya/t1.jpg" 
    },
    {
        "id": 2, 
        "name": "Elegant Tahýa", 
        "category": "Tahýa", 
        "subcategory": "Elegant", 
        "price": 280, 
        "img": "/static/images/tahya/t2.jpg" 
    },
    {
        "id": 3, 
        "name": "Colorful Tahýa", 
        "category": "Tahýa", 
        "subcategory": "Colorful", 
        "price": 300, 
        "img": "/static/images/tahya/t3.avif" 
    },
    {
        "id": 4, 
        "name": "Simple Tahýa", 
        "category": "Tahýa", 
        "subcategory": "Simple", 
        "price": 220, 
        "img": "/static/images/tahya/t4.jpg" 
    },
    {
        "id": 5, 
        "name": "Traditional Pattern Tahýa", 
        "category": "Tahýa", 
        "subcategory": "Traditional", 
        "price": 260, 
        "img": "/static/images/tahya/t5.jpg" 
    },
    {
        "id": 6, 
        "name": "Modern Tahýa", 
        "category": "Tahýa", 
        "subcategory": "Modern", 
        "price": 240, 
        "img": "/static/images/tahya/t6.webp" 
    },
    {
        "id": 7, 
        "name": "Festive Tahýa", 
        "category": "Tahýa", 
        "subcategory": "Festive", 
        "price": 290, 
        "img": "/static/images/tahya/t7.jpg" 
    },
    {
        "id": 8, 
        "name": "Wedding Tahýa", 
        "category": "Tahýa", 
        "subcategory": "Wedding", 
        "price": 320, 
        "img": "/static/images/tahya/t8.jpg" 
    },
    {
        "id": 9, 
        "name": "Daily Tahýa", 
        "category": "Tahýa", 
        "subcategory": "Daily", 
        "price": 200, 
        "img": "/static/images/tahya/t9.jpg" 
    },
    {
        "id": 10, 
        "name": "Special Occasion Tahýa", 
        "category": "Tahýa", 
        "subcategory": "Special", 
        "price": 350, 
        "img": "/static/images/tahya/t10.jpg" 
    },
    
    # Carpets products
    {
        "id": 11, 
        "name": "Traditional Carpet", 
        "category": "Carpets", 
        "subcategory": "Traditional", 
        "price": 3000, 
        "img": "/static/images/carpets/image-1.jpg" 
    },
    {
        "id": 12, 
        "name": "Geometric Carpet", 
        "category": "Carpets", 
        "subcategory": "Geometric", 
        "price": 3200, 
        "img": "/static/images/carpets/image-2.jpg" 
    },
    {
        "id": 13, 
        "name": "Colorful Carpet", 
        "category": "Carpets", 
        "subcategory": "Colorful", 
        "price": 3500, 
        "img": "/static/images/carpets/images-3.jpg" 
    },
    {
        "id": 14, 
        "name": "Classic Carpet", 
        "category": "Carpets", 
        "subcategory": "Classic", 
        "price": 2800, 
        "img": "/static/images/carpets/image-4.jpg" 
    },
    {
        "id": 15, 
        "name": "Modern Carpet", 
        "category": "Carpets", 
        "subcategory": "Modern", 
        "price": 3100, 
        "img": "/static/images/carpets/image-5.jpg" 
    },
    {
        "id": 16, 
        "name": "Luxury Carpet", 
        "category": "Carpets", 
        "subcategory": "Luxury", 
        "price": 4000, 
        "img": "/static/images/carpets/image-6.jpg" 
    },
    {
        "id": 17, 
        "name": "Handmade Carpet", 
        "category": "Carpets", 
        "subcategory": "Handmade", 
        "price": 3800, 
        "img": "/static/images/carpets/image-7.jpg" 
    },
    {
        "id": 18, 
        "name": "Traditional Pattern Carpet", 
        "category": "Carpets", 
        "subcategory": "Traditional", 
        "price": 3300, 
        "img": "/static/images/carpets/image-8.jpg" 
    },
    {
        "id": 19, 
        "name": "Elegant Carpet", 
        "category": "Carpets", 
        "subcategory": "Elegant", 
        "price": 3600, 
        "img": "/static/images/carpets/image-9.jpg" 
    },
    {
        "id": 20, 
        "name": "Royal Carpet", 
        "category": "Carpets", 
        "subcategory": "Royal", 
        "price": 4200, 
        "img": "/static/images/carpets/image-10.jpg" 
    },
    
    # Bags products
    {
        "id": 21, 
        "name": "Traditional Bag", 
        "category": "Bags", 
        "subcategory": "Traditional", 
        "price": 150, 
        "img": "/static/images/bags/b1.jpg" 
    },
    {
        "id": 22, 
        "name": "Leather Bag", 
        "category": "Bags", 
        "subcategory": "Leather", 
        "price": 180, 
        "img": "/static/images/bags/b2.webp" 
    },
    {
        "id": 23, 
        "name": "Colorful Bag", 
        "category": "Bags", 
        "subcategory": "Colorful", 
        "price": 160, 
        "img": "/static/images/bags/b3.jpg" 
    },
    {
        "id": 24, 
        "name": "Simple Bag", 
        "category": "Bags", 
        "subcategory": "Simple", 
        "price": 140, 
        "img": "/static/images/bags/b4.webp" 
    },
    {
        "id": 25, 
        "name": "Elegant Bag", 
        "category": "Bags", 
        "subcategory": "Elegant", 
        "price": 190, 
        "img": "/static/images/bags/b5.jpg" 
    },
    {
        "id": 26, 
        "name": "Modern Bag", 
        "category": "Bags", 
        "subcategory": "Modern", 
        "price": 170, 
        "img": "/static/images/bags/b6.jpg" 
    },
    {
        "id": 27, 
        "name": "Festival Bag", 
        "category": "Bags", 
        "subcategory": "Festival", 
        "price": 200, 
        "img": "/static/images/bags/b7.jpg" 
    },
    {
        "id": 28, 
        "name": "Travel Bag", 
        "category": "Bags", 
        "subcategory": "Travel", 
        "price": 220, 
        "img": "/static/images/bags/b8.jpg" 
    },
    {
        "id": 29, 
        "name": "Daily Bag", 
        "category": "Bags", 
        "subcategory": "Daily", 
        "price": 130, 
        "img": "/static/images/bags/b9.jpg" 
    },
    {
        "id": 30, 
        "name": "Special Bag", 
        "category": "Bags", 
        "subcategory": "Special", 
        "price": 250, 
        "img": "/static/images/bags/b10.jpg" 
    },
    
    # Accessories - Bracelets
    {
        "id": 31, 
        "name": "Silver Bracelet", 
        "category": "Accessories", 
        "subcategory": "Bracelet", 
        "price": 1200, 
        "img": "/static/images/accessories/bracelets/bracelet1.avif" 
    },
    {
        "id": 32, 
        "name": "Gold Bracelet", 
        "category": "Accessories", 
        "subcategory": "Bracelet", 
        "price": 1500, 
        "img": "/static/images/accessories/bracelets/bracelet2.webp" 
    },
    {
        "id": 33, 
        "name": "Traditional Bracelet", 
        "category": "Accessories", 
        "subcategory": "Bracelet", 
        "price": 1100, 
        "img": "/static/images/accessories/bracelets/bracelet3.avif" 
    },
    {
        "id": 34, 
        "name": "Modern Bracelet", 
        "category": "Accessories", 
        "subcategory": "Bracelet", 
        "price": 1300, 
        "img": "/static/images/accessories/bracelets/bracelet4.avif" 
    },
    {
        "id": 35, 
        "name": "Elegant Bracelet", 
        "category": "Accessories", 
        "subcategory": "Bracelet", 
        "price": 1400, 
        "img": "/static/images/accessories/bracelets/bracelet5.avif" 
    },
    {
        "id": 36, 
        "name": "Simple Bracelet", 
        "category": "Accessories", 
        "subcategory": "Bracelet", 
        "price": 1000, 
        "img": "/static/images/accessories/bracelets/bracelet6.jpg" 
    },
    {
        "id": 37, 
        "name": "Festival Bracelet", 
        "category": "Accessories", 
        "subcategory": "Bracelet", 
        "price": 1600, 
        "img": "/static/images/accessories/bracelets/bracelet7.webp" 
    },
    {
        "id": 38, 
        "name": "Daily Bracelet", 
        "category": "Accessories", 
        "subcategory": "Bracelet", 
        "price": 900, 
        "img": "/static/images/accessories/bracelets/bracelet8.jpg" 
    },
    {
        "id": 39, 
        "name": "Special Bracelet", 
        "category": "Accessories", 
        "subcategory": "Bracelet", 
        "price": 1800, 
        "img": "/static/images/accessories/bracelets/bracelet9.avif" 
    },
    {
        "id": 40, 
        "name": "Luxury Bracelet", 
        "category": "Accessories", 
        "subcategory": "Bracelet", 
        "price": 2000, 
        "img": "/static/images/accessories/bracelets/bracelet10.avif" 
    },
    
    # Accessories - Earrings
    {
        "id": 41, 
        "name": "Traditional Earrings", 
        "category": "Accessories", 
        "subcategory": "Earrings", 
        "price": 800, 
        "img": "/static/images/accessories/earings/e1.jpg" 
    },
    {
        "id": 42, 
        "name": "Silver Earrings", 
        "category": "Accessories", 
        "subcategory": "Earrings", 
        "price": 900, 
        "img": "/static/images/accessories/earings/e2.avif" 
    },
    {
        "id": 43, 
        "name": "Gold Earrings", 
        "category": "Accessories", 
        "subcategory": "Earrings", 
        "price": 1100, 
        "img": "/static/images/accessories/earings/e3.avif" 
    },
    {
        "id": 44, 
        "name": "Modern Earrings", 
        "category": "Accessories", 
        "subcategory": "Earrings", 
        "price": 700, 
        "img": "/static/images/accessories/earings/e4.avif" 
    },
    {
        "id": 45, 
        "name": "Elegant Earrings", 
        "category": "Accessories", 
        "subcategory": "Earrings", 
        "price": 1000, 
        "img": "/static/images/accessories/earings/e5.avif" 
    },
    {
        "id": 46, 
        "name": "Simple Earrings", 
        "category": "Accessories", 
        "subcategory": "Earrings", 
        "price": 600, 
        "img": "/static/images/accessories/earings/e6.avif" 
    },
    {
        "id": 47, 
        "name": "Festival Earrings", 
        "category": "Accessories", 
        "subcategory": "Earrings", 
        "price": 1200, 
        "img": "/static/images/accessories/earings/e7.avif" 
    },
    {
        "id": 48, 
        "name": "Daily Earrings", 
        "category": "Accessories", 
        "subcategory": "Earrings", 
        "price": 500, 
        "img": "/static/images/accessories/earings/e8.webp" 
    },
    {
        "id": 49, 
        "name": "Special Earrings", 
        "category": "Accessories", 
        "subcategory": "Earrings", 
        "price": 1400, 
        "img": "/static/images/accessories/earings/e9.avif" 
    },
    {
        "id": 50, 
        "name": "Luxury Earrings", 
        "category": "Accessories", 
        "subcategory": "Earrings", 
        "price": 1600, 
        "img": "/static/images/accessories/earings/e10.avif" 
    },
    
    # Accessories - Rings
    {
        "id": 51, 
        "name": "Traditional Ring", 
        "category": "Accessories", 
        "subcategory": "Rings", 
        "price": 2000, 
        "img": "/static/images/accessories/rings/r1.jpg" 
    },
    {
        "id": 52, 
        "name": "Silver Ring", 
        "category": "Accessories", 
        "subcategory": "Rings", 
        "price": 2200, 
        "img": "/static/images/accessories/rings/r2.jpg" 
    },
    {
        "id": 53, 
        "name": "Gold Ring", 
        "category": "Accessories", 
        "subcategory": "Rings", 
        "price": 2500, 
        "img": "/static/images/accessories/rings/r3.avif" 
    },
    {
        "id": 54, 
        "name": "Modern Ring", 
        "category": "Accessories", 
        "subcategory": "Rings", 
        "price": 2100, 
        "img": "/static/images/accessories/rings/r4.webp" 
    },
    {
        "id": 55, 
        "name": "Elegant Ring", 
        "category": "Accessories", 
        "subcategory": "Rings", 
        "price": 2400, 
        "img": "/static/images/accessories/rings/r5.avif" 
    },
    {
        "id": 56, 
        "name": "Simple Ring", 
        "category": "Accessories", 
        "subcategory": "Rings", 
        "price": 1800, 
        "img": "/static/images/accessories/rings/r6.avif" 
    },
    {
        "id": 57, 
        "name": "Festival Ring", 
        "category": "Accessories", 
        "subcategory": "Rings", 
        "price": 2600, 
        "img": "/static/images/accessories/rings/r7.avif" 
    },
    {
        "id": 58, 
        "name": "Daily Ring", 
        "category": "Accessories", 
        "subcategory": "Rings", 
        "price": 1600, 
        "img": "/static/images/accessories/rings/r8.avif" 
    },
    {
        "id": 59, 
        "name": "Special Ring", 
        "category": "Accessories", 
        "subcategory": "Rings", 
        "price": 2800, 
        "img": "/static/images/accessories/rings/r9.avif" 
    },
    {
        "id": 60, 
        "name": "Luxury Ring", 
        "category": "Accessories", 
        "subcategory": "Rings", 
        "price": 3000, 
        "img": "/static/images/accessories/rings/r10.avif" 
    },
    
    # Women's dresses
    {
        "id": 61, 
        "name": "Traditional Dress", 
        "category": "Women", 
        "subcategory": "Traditional", 
        "price": 400, 
        "img": "/static/images/women dress/d1.avif" 
    },
    {
        "id": 62, 
        "name": "Elegant Dress", 
        "category": "Women", 
        "subcategory": "Elegant", 
        "price": 450, 
        "img": "/static/images/women dress/d2.webp" 
    },
    {
        "id": 63, 
        "name": "Colorful Dress", 
        "category": "Women", 
        "subcategory": "Colorful", 
        "price": 420, 
        "img": "/static/images/women dress/d3.avif" 
    },
    {
        "id": 64, 
        "name": "Simple Dress", 
        "category": "Women", 
        "subcategory": "Simple", 
        "price": 380, 
        "img": "/static/images/women dress/d4.avif" 
    },
    {
        "id": 65, 
        "name": "Modern Dress", 
        "category": "Women", 
        "subcategory": "Modern", 
        "price": 480, 
        "img": "/static/images/women dress/d5.avif" 
    },
    {
        "id": 66, 
        "name": "Festival Dress", 
        "category": "Women", 
        "subcategory": "Festival", 
        "price": 500, 
        "img": "/static/images/women dress/d6.webp" 
    },
    {
        "id": 67, 
        "name": "Daily Dress", 
        "category": "Women", 
        "subcategory": "Daily", 
        "price": 350, 
        "img": "/static/images/women dress/d7.webp" 
    },
    {
        "id": 68, 
        "name": "Wedding Dress", 
        "category": "Women", 
        "subcategory": "Wedding", 
        "price": 600, 
        "img": "/static/images/women dress/d8.webp" 
    },
    {
        "id": 69, 
        "name": "Special Occasion Dress", 
        "category": "Women", 
        "subcategory": "Special", 
        "price": 550, 
        "img": "/static/images/women dress/d9.webp" 
    },
    {
        "id": 70, 
        "name": "Luxury Dress", 
        "category": "Women", 
        "subcategory": "Luxury", 
        "price": 700, 
        "img": "/static/images/women dress/d10.avif" 
    },
    
    # Men's dresses
    {
        "id": 71, 
        "name": "Traditional Man Dress", 
        "category": "Men", 
        "subcategory": "Traditional", 
        "price": 350, 
        "img": "/static/images/man dress/m1.jpg" 
    },
    {
        "id": 72, 
        "name": "Elegant Man Dress", 
        "category": "Men", 
        "subcategory": "Elegant", 
        "price": 380, 
        "img": "/static/images/man dress/m2.webp" 
    },
    {
        "id": 73, 
        "name": "Simple Man Dress", 
        "category": "Men", 
        "subcategory": "Simple", 
        "price": 320, 
        "img": "/static/images/man dress/m3.webp" 
    },
    {
        "id": 74, 
        "name": "Modern Man Dress", 
        "category": "Men", 
        "subcategory": "Modern", 
        "price": 400, 
        "img": "/static/images/man dress/m4.avif" 
    },
    {
        "id": 75, 
        "name": "Festival Man Dress", 
        "category": "Men", 
        "subcategory": "Festival", 
        "price": 420, 
        "img": "/static/images/man dress/m5.avif" 
    },
    {
        "id": 76, 
        "name": "Daily Man Dress", 
        "category": "Men", 
        "subcategory": "Daily", 
        "price": 300, 
        "img": "/static/images/man dress/m6.webp" 
    },
    {
        "id": 77, 
        "name": "Special Man Dress", 
        "category": "Men", 
        "subcategory": "Special", 
        "price": 450, 
        "img": "/static/images/man dress/m7.avif" 
    },
    {
        "id": 78, 
        "name": "Luxury Man Dress", 
        "category": "Men", 
        "subcategory": "Luxury", 
        "price": 500, 
        "img": "/static/images/man dress/m8.jpg" 
    },
    
    # Headwear
    {
        "id": 79, 
        "name": "Traditional Headwear", 
        "category": "Headwear", 
        "subcategory": "Traditional", 
        "price": 150, 
        "img": "/static/images/on head/h1.webp" 
    },
    {
        "id": 80, 
        "name": "Elegant Headwear", 
        "category": "Headwear", 
        "subcategory": "Elegant", 
        "price": 180, 
        "img": "/static/images/on head/h2.webp" 
    },
    {
        "id": 81, 
        "name": "Simple Headwear", 
        "category": "Headwear", 
        "subcategory": "Simple", 
        "price": 120, 
        "img": "/static/images/on head/h3.avif" 
    },
    {
        "id": 82, 
        "name": "Modern Headwear", 
        "category": "Headwear", 
        "subcategory": "Modern", 
        "price": 160, 
        "img": "/static/images/on head/h4.avif" 
    },
    {
        "id": 83, 
        "name": "Festival Headwear", 
        "category": "Headwear", 
        "subcategory": "Festival", 
        "price": 200, 
        "img": "/static/images/on head/h5.avif" 
    },
    {
        "id": 84, 
        "name": "Daily Headwear", 
        "category": "Headwear", 
        "subcategory": "Daily", 
        "price": 100, 
        "img": "/static/images/on head/h6.jpg" 
    },
    {
        "id": 85, 
        "name": "Special Headwear", 
        "category": "Headwear", 
        "subcategory": "Special", 
        "price": 220, 
        "img": "/static/images/on head/h7.avif" 
    },
    {
        "id": 86, 
        "name": "Luxury Headwear", 
        "category": "Headwear", 
        "subcategory": "Luxury", 
        "price": 250, 
        "img": "/static/images/on head/h8.webp" 
    },
    {
        "id": 87, 
        "name": "Traditional Pattern Headwear", 
        "category": "Headwear", 
        "subcategory": "Traditional", 
        "price": 190, 
        "img": "/static/images/on head/h9.avif" 
    },
    {
        "id": 88, 
        "name": "Special Occasion Headwear", 
        "category": "Headwear", 
        "subcategory": "Special", 
        "price": 280, 
        "img": "/static/images/on head/h10.avif" 
    },
    
    # Traditional items (Telpek)
    {
        "id": 89, 
        "name": "Traditional Telpek", 
        "category": "Traditional", 
        "subcategory": "Traditional", 
        "price": 500, 
        "img": "/static/images/telpek/telpek1.webp" 
    },
    {
        "id": 90, 
        "name": "Elegant Telpek", 
        "category": "Traditional", 
        "subcategory": "Elegant", 
        "price": 550, 
        "img": "/static/images/telpek/telpek2.webp" 
    },
    {
        "id": 91, 
        "name": "Simple Telpek", 
        "category": "Traditional", 
        "subcategory": "Simple", 
        "price": 450, 
        "img": "/static/images/telpek/telpek3.webp" 
    },
    {
        "id": 92, 
        "name": "Modern Telpek", 
        "category": "Traditional", 
        "subcategory": "Modern", 
        "price": 520, 
        "img": "/static/images/telpek/telpek4.webp" 
    },
    {
        "id": 93, 
        "name": "Festival Telpek", 
        "category": "Traditional", 
        "subcategory": "Festival", 
        "price": 600, 
        "img": "/static/images/telpek/telpek5.webp" 
    },
    {
        "id": 94, 
        "name": "Daily Telpek", 
        "category": "Traditional", 
        "subcategory": "Daily", 
        "price": 400, 
        "img": "/static/images/telpek/telpek6.jpg" 
    },
    {
        "id": 95, 
        "name": "Special Telpek", 
        "category": "Traditional", 
        "subcategory": "Special", 
        "price": 650, 
        "img": "/static/images/telpek/telpek7.jpg" 
    }
]


# Translation function for product names
def get_translated_product_name(product_name, category_name):
    """Get translated product name based on current locale"""
    locale = get_locale()
    
    # English is default
    if locale == 'en':
        return product_name
    
    # Russian translations
    if locale == 'ru':
        translations = {
            # Tahýa products
            "Traditional Tahýa": "Традиционная Тахыя",
            "Elegant Tahýa": "Элегантная Тахыя",
            "Colorful Tahýa": "Цветная Тахыя",
            "Simple Tahýa": "Простая Тахыя",
            "Traditional Pattern Tahýa": "Тахыя с традиционным узором",
            "Modern Tahýa": "Современная Тахыя",
            "Festive Tahýa": "Праздничная Тахыя",
            "Wedding Tahýa": "Свадебная Тахыя",
            "Daily Tahýa": "Повседневная Тахыя",
            "Special Occasion Tahýa": "Тахыя для особого случая",
            
            # Carpets products
            "Traditional Carpet": "Традиционный ковер",
            "Geometric Carpet": "Геометрический ковер",
            "Colorful Carpet": "Цветной ковер",
            "Classic Carpet": "Классический ковер",
            "Modern Carpet": "Современный ковер",
            "Luxury Carpet": "Роскошный ковер",
            "Handmade Carpet": "Ручной ковер",
            "Traditional Pattern Carpet": "Ковер с традиционным узором",
            "Elegant Carpet": "Элегантный ковер",
            "Royal Carpet": "Королевский ковер",
            
            # Bags products
            "Traditional Bag": "Традиционная сумка",
            "Leather Bag": "Кожаная сумка",
            "Colorful Bag": "Цветная сумка",
            "Simple Bag": "Простая сумка",
            "Elegant Bag": "Элегантная сумка",
            "Modern Bag": "Современная сумка",
            "Festival Bag": "Фестивальная сумка",
            "Travel Bag": "Дорожная сумка",
            "Daily Bag": "Повседневная сумка",
            "Special Bag": "Специальная сумка",
            
            # Accessories - Bracelets
            "Silver Bracelet": "Серебряный браслет",
            "Gold Bracelet": "Золотой браслет",
            "Traditional Bracelet": "Традиционный браслет",
            "Modern Bracelet": "Современный браслет",
            "Elegant Bracelet": "Элегантный браслет",
            "Simple Bracelet": "Простой браслет",
            "Festival Bracelet": "Фестивальный браслет",
            "Daily Bracelet": "Повседневный браслет",
            "Special Bracelet": "Специальный браслет",
            "Luxury Bracelet": "Роскошный браслет",
            
            # Accessories - Earrings
            "Traditional Earrings": "Традиционные серьги",
            "Silver Earrings": "Серебряные серьги",
            "Gold Earrings": "Золотые серьги",
            "Modern Earrings": "Современные серьги",
            "Elegant Earrings": "Элегантные серьги",
            "Simple Earrings": "Простые серьги",
            "Festival Earrings": "Фестивальные серьги",
            "Daily Earrings": "Повседневные серьги",
            "Special Earrings": "Специальные серьги",
            "Luxury Earrings": "Роскошные серьги",
            
            # Accessories - Rings
            "Traditional Ring": "Традиционное кольцо",
            "Silver Ring": "Серебряное кольцо",
            "Gold Ring": "Золотое кольцо",
            "Modern Ring": "Современное кольцо",
            "Elegant Ring": "Элегантное кольцо",
            "Simple Ring": "Простое кольцо",
            "Festival Ring": "Фестивальное кольцо",
            "Daily Ring": "Повседневное кольцо",
            "Special Ring": "Специальное кольцо",
            "Luxury Ring": "Роскошное кольцо",
            
            # Women's dresses
            "Traditional Dress": "Традиционное платье",
            "Elegant Dress": "Элегантное платье",
            "Colorful Dress": "Цветное платье",
            "Simple Dress": "Простое платье",
            "Modern Dress": "Современное платье",
            "Festival Dress": "Фестивальное платье",
            "Daily Dress": "Повседневное платье",
            "Wedding Dress": "Свадебное платье",
            "Special Occasion Dress": "Платье для особого случая",
            "Luxury Dress": "Роскошное платье",
            
            # Men's dresses
            "Traditional Man Dress": "Традиционная мужская одежда",
            "Elegant Man Dress": "Элегантная мужская одежда",
            "Simple Man Dress": "Простая мужская одежда",
            "Modern Man Dress": "Современная мужская одежда",
            "Festival Man Dress": "Фестивальная мужская одежда",
            "Daily Man Dress": "Повседневная мужская одежда",
            "Special Man Dress": "Специальная мужская одежда",
            "Luxury Man Dress": "Роскошная мужская одежда",
            
            # Headwear
            "Traditional Headwear": "Традиционная головная повязка",
            "Elegant Headwear": "Элегантная головная повязка",
            "Simple Headwear": "Простая головная повязка",
            "Modern Headwear": "Современная головная повязка",
            "Festival Headwear": "Фестивальная головная повязка",
            "Daily Headwear": "Повседневная головная повязка",
            "Special Headwear": "Специальная головная повязка",
            "Luxury Headwear": "Роскошная головная повязка",
            "Traditional Pattern Headwear": "Головная повязка с традиционным узором",
            "Special Occasion Headwear": "Головная повязка для особого случая",
            
            # Traditional items (Telpek)
            "Traditional Telpek": "Традиционный телпек",
            "Elegant Telpek": "Элегантный телпек",
            "Simple Telpek": "Простой телпек",
            "Modern Telpek": "Современный телпек",
            "Festival Telpek": "Фестивальный телпек",
            "Daily Telpek": "Повседневный телпек",
            "Special Telpek": "Специальный телпек",
        }
        return translations.get(product_name, product_name)
    
    # Turkmen translations
    if locale == 'tk':
        translations = {
            # Tahýa products
            "Traditional Tahýa": "Gelenji Tahýa",
            "Elegant Tahýa": "Elegant Tahýa",
            "Colorful Tahýa": "Reňkli Tahýa",
            "Simple Tahýa": "Ýönekeý Tahýa",
            "Traditional Pattern Tahýa": "Gelenji desenli Tahýa",
            "Modern Tahýa": "Modern Tahýa",
            "Festive Tahýa": "Güýjli Tahýa",
            "Wedding Tahýa": "Toý Tahýasy",
            "Daily Tahýa": "Günlük Tahýa",
            "Special Occasion Tahýa": "Ýörite wezamin Tahýasy",
            
            # Carpets products
            "Traditional Carpet": "Gelenji Gylym",
            "Geometric Carpet": "Geometrik Gylym",
            "Colorful Carpet": "Reňkli Gylym",
            "Classic Carpet": "Klassik Gylym",
            "Modern Carpet": "Modern Gylym",
            "Luxury Carpet": "Luks Gylym",
            "Handmade Carpet": "Eli bilen tökülän Gylym",
            "Traditional Pattern Carpet": "Gelenji desenli Gylym",
            "Elegant Carpet": "Elegant Gylym",
            "Royal Carpet": "Patyşalyk Gylymy",
            
            # Bags products
            "Traditional Bag": "Gelenji Çanta",
            "Leather Bag": "Deri Çanta",
            "Colorful Bag": "Reňkli Çanta",
            "Simple Bag": "Ýönekeý Çanta",
            "Elegant Bag": "Elegant Çanta",
            "Modern Bag": "Modern Çanta",
            "Festival Bag": "Güýjli Çanta",
            "Travel Bag": "Seyahat Çantasy",
            "Daily Bag": "Günlük Çanta",
            "Special Bag": "Ýörite Çanta",
            
            # Accessories - Bracelets
            "Silver Bracelet": "Gümüş Bilezik",
            "Gold Bracelet": "Altyn Bilezik",
            "Traditional Bracelet": "Gelenji Bilezik",
            "Modern Bracelet": "Modern Bilezik",
            "Elegant Bracelet": "Elegant Bilezik",
            "Simple Bracelet": "Ýönekeý Bilezik",
            "Festival Bracelet": "Güýjli Bilezik",
            "Daily Bracelet": "Günlük Bilezik",
            "Special Bracelet": "Ýörite Bilezik",
            "Luxury Bracelet": "Luks Bilezik",
            
            # Accessories - Earrings
            "Traditional Earrings": "Gelenji Sazary",
            "Silver Earrings": "Gümüş Sazary",
            "Gold Earrings": "Altyn Sazary",
            "Modern Earrings": "Modern Sazary",
            "Elegant Earrings": "Elegant Sazary",
            "Simple Earrings": "Ýönekeý Sazary",
            "Festival Earrings": "Güýjli Sazary",
            "Daily Earrings": "Günlük Sazary",
            "Special Earrings": "Ýörite Sazary",
            "Luxury Earrings": "Luks Sazary",
            
            # Accessories - Rings
            "Traditional Ring": "Gelenji Ýüzük",
            "Silver Ring": "Gümüş Ýüzük",
            "Gold Ring": "Altyn Ýüzük",
            "Modern Ring": "Modern Ýüzük",
            "Elegant Ring": "Elegant Ýüzük",
            "Simple Ring": "Ýönekeý Ýüzük",
            "Festival Ring": "Güýjli Ýüzük",
            "Daily Ring": "Günlük Ýüzük",
            "Special Ring": "Ýörite Ýüzük",
            "Luxury Ring": "Luks Ýüzük",
            
            # Women's dresses
            "Traditional Dress": "Gelenji Gapyr",
            "Elegant Dress": "Elegant Gapyr",
            "Colorful Dress": "Reňkli Gapyr",
            "Simple Dress": "Ýönekeý Gapyr",
            "Modern Dress": "Modern Gapyr",
            "Festival Dress": "Güýjli Gapyr",
            "Daily Dress": "Günlük Gapyr",
            "Wedding Dress": "Toý Gapyry",
            "Special Occasion Dress": "Ýörite wezamin Gapyry",
            "Luxury Dress": "Luks Gapyr",
            
            # Men's dresses
            "Traditional Man Dress": "Gelenji Erkek Gapyry",
            "Elegant Man Dress": "Elegant Erkek Gapyry",
            "Simple Man Dress": "Ýönekeý Erkek Gapyry",
            "Modern Man Dress": "Modern Erkek Gapyry",
            "Festival Man Dress": "Güýjli Erkek Gapyry",
            "Daily Man Dress": "Günlük Erkek Gapyry",
            "Special Man Dress": "Ýörite Erkek Gapyry",
            "Luxury Man Dress": "Luks Erkek Gapyry",
            
            # Headwear
            "Traditional Headwear": "Gelenji Baş Gapyry",
            "Elegant Headwear": "Elegant Baş Gapyry",
            "Simple Headwear": "Ýönekeý Baş Gapyry",
            "Modern Headwear": "Modern Baş Gapyry",
            "Festival Headwear": "Güýjli Baş Gapyry",
            "Daily Headwear": "Günlük Baş Gapyry",
            "Special Headwear": "Ýörite Baş Gapyry",
            "Luxury Headwear": "Luks Baş Gapyry",
            "Traditional Pattern Headwear": "Gelenji desenli Baş Gapyry",
            "Special Occasion Headwear": "Ýörite wezamin Baş Gapyry",
            
            # Traditional items (Telpek)
            "Traditional Telpek": "Gelenji Telpek",
            "Elegant Telpek": "Elegant Telpek",
            "Simple Telpek": "Ýönekeý Telpek",
            "Modern Telpek": "Modern Telpek",
            "Festival Telpek": "Güýjli Telpek",
            "Daily Telpek": "Günlük Telpek",
            "Special Telpek": "Ýörite Telpek",
        }
        return translations.get(product_name, product_name)
    
    return product_name

# New function to get translated product description
def get_translated_product_description(product_name, category_name):
    """Get translated product description based on current locale"""
    locale = get_locale()
    
    # English is default
    if locale == 'en':
        return "Traditional Turkmen product"
    
    # Russian translations
    if locale == 'ru':
        descriptions = {
            # Tahýa products
            "Traditional Tahýa": "Традиционный туркменский головной убор",
            "Elegant Tahýa": "Элегантный туркменский головной убор",
            "Colorful Tahýa": "Цветной туркменский головной убор",
            "Simple Tahýa": "Простой туркменский головной убор",
            "Traditional Pattern Tahýa": "Туркменский головной убор с традиционным узором",
            "Modern Tahýa": "Современный туркменский головной убор",
            "Festive Tahýa": "Праздничный туркменский головной убор",
            "Wedding Tahýa": "Свадебный туркменский головной убор",
            "Daily Tahýa": "Повседневный туркменский головной убор",
            "Special Occasion Tahýa": "Туркменский головной убор для особого случая",
            
            # Carpets products
            "Traditional Carpet": "Традиционный туркменский ковер",
            "Geometric Carpet": "Геометрический туркменский ковер",
            "Colorful Carpet": "Цветной туркменский ковер",
            "Classic Carpet": "Классический туркменский ковер",
            "Modern Carpet": "Современный туркменский ковер",
            "Luxury Carpet": "Роскошный туркменский ковер",
            "Handmade Carpet": "Ручной туркменский ковер",
            "Traditional Pattern Carpet": "Туркменский ковер с традиционным узором",
            "Elegant Carpet": "Элегантный туркменский ковер",
            "Royal Carpet": "Королевский туркменский ковер",
            
            # Bags products
            "Traditional Bag": "Традиционная туркменская сумка",
            "Leather Bag": "Кожаная туркменская сумка",
            "Colorful Bag": "Цветная туркменская сумка",
            "Simple Bag": "Простая туркменская сумка",
            "Elegant Bag": "Элегантная туркменская сумка",
            "Modern Bag": "Современная туркменская сумка",
            "Festival Bag": "Фестивальная туркменская сумка",
            "Travel Bag": "Дорожная туркменская сумка",
            "Daily Bag": "Повседневная туркменская сумка",
            "Special Bag": "Специальная туркменская сумка",
            
            # Accessories - Bracelets
            "Silver Bracelet": "Серебряный туркменский браслет",
            "Gold Bracelet": "Золотой туркменский браслет",
            "Traditional Bracelet": "Традиционный туркменский браслет",
            "Modern Bracelet": "Современный туркменский браслет",
            "Elegant Bracelet": "Элегантный туркменский браслет",
            "Simple Bracelet": "Простой туркменский браслет",
            "Festival Bracelet": "Фестивальный туркменский браслет",
            "Daily Bracelet": "Повседневный туркменский браслет",
            "Special Bracelet": "Специальный туркменский браслет",
            "Luxury Bracelet": "Роскошный туркменский браслет",
            
            # Accessories - Earrings
            "Traditional Earrings": "Традиционные туркменские серьги",
            "Silver Earrings": "Серебряные туркменские серьги",
            "Gold Earrings": "Золотые туркменские серьги",
            "Modern Earrings": "Современные туркменские серьги",
            "Elegant Earrings": "Элегантные туркменские серьги",
            "Simple Earrings": "Простые туркменские серьги",
            "Festival Earrings": "Фестивальные туркменские серьги",
            "Daily Earrings": "Повседневные туркменские серьги",
            "Special Earrings": "Специальные туркменские серьги",
            "Luxury Earrings": "Роскошные туркменские серьги",
            
            # Accessories - Rings
            "Traditional Ring": "Традиционное туркменское кольцо",
            "Silver Ring": "Серебряное туркменское кольцо",
            "Gold Ring": "Золотое туркменское кольцо",
            "Modern Ring": "Современное туркменское кольцо",
            "Elegant Ring": "Элегантное туркменское кольцо",
            "Simple Ring": "Простое туркменское кольцо",
            "Festival Ring": "Фестивальное туркменское кольцо",
            "Daily Ring": "Повседневное туркменское кольцо",
            "Special Ring": "Специальное туркменское кольцо",
            "Luxury Ring": "Роскошное туркменское кольцо",
            
            # Women's dresses
            "Traditional Dress": "Традиционное туркменское платье",
            "Elegant Dress": "Элегантное туркменское платье",
            "Colorful Dress": "Цветное туркменское платье",
            "Simple Dress": "Простое туркменское платье",
            "Modern Dress": "Современное туркменское платье",
            "Festival Dress": "Фестивальное туркменское платье",
            "Daily Dress": "Повседневное туркменское платье",
            "Wedding Dress": "Свадебное туркменское платье",
            "Special Occasion Dress": "Туркменское платье для особого случая",
            "Luxury Dress": "Роскошное туркменское платье",
            
            # Men's dresses
            "Traditional Man Dress": "Традиционная туркменская мужская одежда",
            "Elegant Man Dress": "Элегантная туркменская мужская одежда",
            "Simple Man Dress": "Простая туркменская мужская одежда",
            "Modern Man Dress": "Современная туркменская мужская одежда",
            "Festival Man Dress": "Фестивальная туркменская мужская одежда",
            "Daily Man Dress": "Повседневная туркменская мужская одежда",
            "Special Man Dress": "Специальная туркменская мужская одежда",
            "Luxury Man Dress": "Роскошная туркменская мужская одежда",
            
            # Headwear
            "Traditional Headwear": "Традиционная туркменская головная повязка",
            "Elegant Headwear": "Элегантная туркменская головная повязка",
            "Simple Headwear": "Простая туркменская головная повязка",
            "Modern Headwear": "Современная туркменская головная повязка",
            "Festival Headwear": "Фестивальная туркменская головная повязка",
            "Daily Headwear": "Повседневная туркменская головная повязка",
            "Special Headwear": "Специальная туркменская головная повязка",
            "Luxury Headwear": "Роскошная туркменская головная повязка",
            "Traditional Pattern Headwear": "Туркменская головная повязка с традиционным узором",
            "Special Occasion Headwear": "Туркменская головная повязка для особого случая",
            
            # Traditional items (Telpek)
            "Traditional Telpek": "Традиционный туркменский телпек",
            "Elegant Telpek": "Элегантный туркменский телпек",
            "Simple Telpek": "Простой туркменский телпек",
            "Modern Telpek": "Современный туркменский телпек",
            "Festival Telpek": "Фестивальный туркменский телпек",
            "Daily Telpek": "Повседневный туркменский телпек",
            "Special Telpek": "Специальный туркменский телпек",
        }
        return descriptions.get(product_name, "Традиционный туркменский продукт")
    
    # Turkmen translations
    if locale == 'tk':
        descriptions = {
            # Tahýa products
            "Traditional Tahýa": "Gelenji turkmen baş gapyry",
            "Elegant Tahýa": "Elegant turkmen baş gapyry",
            "Colorful Tahýa": "Reňkli turkmen baş gapyry",
            "Simple Tahýa": "Ýönekeý turkmen baş gapyry",
            "Traditional Pattern Tahýa": "Gelenji desenli turkmen baş gapyry",
            "Modern Tahýa": "Modern turkmen baş gapyry",
            "Festive Tahýa": "Güýjli turkmen baş gapyry",
            "Wedding Tahýa": "Toý turkmen baş gapyry",
            "Daily Tahýa": "Günlük turkmen baş gapyry",
            "Special Occasion Tahýa": "Ýörite wezamin turkmen baş gapyry",
            
            # Carpets products
            "Traditional Carpet": "Gelenji turkmen gylymy",
            "Geometric Carpet": "Geometrik turkmen gylymy",
            "Colorful Carpet": "Reňkli turkmen gylymy",
            "Classic Carpet": "Klassik turkmen gylymy",
            "Modern Carpet": "Modern turkmen gylymy",
            "Luxury Carpet": "Luks turkmen gylymy",
            "Handmade Carpet": "Eli bilen tökülän turkmen gylymy",
            "Traditional Pattern Carpet": "Gelenji desenli turkmen gylymy",
            "Elegant Carpet": "Elegant turkmen gylymy",
            "Royal Carpet": "Patyşalyk turkmen gylymy",
            
            # Bags products
            "Traditional Bag": "Gelenji turkmen çantasy",
            "Leather Bag": "Deri turkmen çantasy",
            "Colorful Bag": "Reňkli turkmen çantasy",
            "Simple Bag": "Ýönekeý turkmen çantasy",
            "Elegant Bag": "Elegant turkmen çantasy",
            "Modern Bag": "Modern turkmen çantasy",
            "Festival Bag": "Güýjli turkmen çantasy",
            "Travel Bag": "Seyahat turkmen çantasy",
            "Daily Bag": "Günlük turkmen çantasy",
            "Special Bag": "Ýörite turkmen çantasy",
            
            # Accessories - Bracelets
            "Silver Bracelet": "Gümüş turkmen bilezigi",
            "Gold Bracelet": "Altyn turkmen bilezigi",
            "Traditional Bracelet": "Gelenji turkmen bilezigi",
            "Modern Bracelet": "Modern turkmen bilezigi",
            "Elegant Bracelet": "Elegant turkmen bilezigi",
            "Simple Bracelet": "Ýönekeý turkmen bilezigi",
            "Festival Bracelet": "Güýjli turkmen bilezigi",
            "Daily Bracelet": "Günlük turkmen bilezigi",
            "Special Bracelet": "Ýörite turkmen bilezigi",
            "Luxury Bracelet": "Luks turkmen bilezigi",
            
            # Accessories - Earrings
            "Traditional Earrings": "Gelenji turkmen sazarlary",
            "Silver Earrings": "Gümüş turkmen sazarlary",
            "Gold Earrings": "Altyn turkmen sazarlary",
            "Modern Earrings": "Modern turkmen sazarlary",
            "Elegant Earrings": "Elegant turkmen sazarlary",
            "Simple Earrings": "Ýönekeý turkmen sazarlary",
            "Festival Earrings": "Güýjli turkmen sazarlary",
            "Daily Earrings": "Günlük turkmen sazarlary",
            "Special Earrings": "Ýörite turkmen sazarlary",
            "Luxury Earrings": "Luks turkmen sazarlary",
            
            # Accessories - Rings
            "Traditional Ring": "Gelenji turkmen ýüzügi",
            "Silver Ring": "Gümüş turkmen ýüzügi",
            "Gold Ring": "Altyn turkmen ýüzügi",
            "Modern Ring": "Modern turkmen ýüzügi",
            "Elegant Ring": "Elegant turkmen ýüzügi",
            "Simple Ring": "Ýönekeý turkmen ýüzügi",
            "Festival Ring": "Güýjli turkmen ýüzügi",
            "Daily Ring": "Günlük turkmen ýüzügi",
            "Special Ring": "Ýörite turkmen ýüzügi",
            "Luxury Ring": "Luks turkmen ýüzügi",
            
            # Women's dresses
            "Traditional Dress": "Gelenji turkmen gapyry",
            "Elegant Dress": "Elegant turkmen gapyry",
            "Colorful Dress": "Reňkli turkmen gapyry",
            "Simple Dress": "Ýönekeý turkmen gapyry",
            "Modern Dress": "Modern turkmen gapyry",
            "Festival Dress": "Güýjli turkmen gapyry",
            "Daily Dress": "Günlük turkmen gapyry",
            "Wedding Dress": "Toý turkmen gapyry",
            "Special Occasion Dress": "Ýörite wezamin turkmen gapyry",
            "Luxury Dress": "Luks turkmen gapyry",
            
            # Men's dresses
            "Traditional Man Dress": "Gelenji turkmen erkek gapyry",
            "Elegant Man Dress": "Elegant turkmen erkek gapyry",
            "Simple Man Dress": "Ýönekeý turkmen erkek gapyry",
            "Modern Man Dress": "Modern turkmen erkek gapyry",
            "Festival Man Dress": "Güýjli turkmen erkek gapyry",
            "Daily Man Dress": "Günlük turkmen erkek gapyry",
            "Special Man Dress": "Ýörite turkmen erkek gapyry",
            "Luxury Man Dress": "Luks turkmen erkek gapyry",
            
            # Headwear
            "Traditional Headwear": "Gelenji turkmen baş gapyry",
            "Elegant Headwear": "Elegant turkmen baş gapyry",
            "Simple Headwear": "Ýönekeý turkmen baş gapyry",
            "Modern Headwear": "Modern turkmen baş gapyry",
            "Festival Headwear": "Güýjli turkmen baş gapyry",
            "Daily Headwear": "Günlük turkmen baş gapyry",
            "Special Headwear": "Ýörite turkmen baş gapyry",
            "Luxury Headwear": "Luks turkmen baş gapyry",
            "Traditional Pattern Headwear": "Gelenji desenli turkmen baş gapyry",
            "Special Occasion Headwear": "Ýörite wezamin turkmen baş gapyry",
            
            # Traditional items (Telpek)
            "Traditional Telpek": "Gelenji turkmen telpegi",
            "Elegant Telpek": "Elegant turkmen telpegi",
            "Simple Telpek": "Ýönekeý turkmen telpegi",
            "Modern Telpek": "Modern turkmen telpegi",
            "Festival Telpek": "Güýjli turkmen telpegi",
            "Daily Telpek": "Günlük turkmen telpegi",
            "Special Telpek": "Ýörite turkmen telpegi",
        }
        return descriptions.get(product_name, "Gelenji turkmen önümi")
    
    return "Traditional Turkmen product"

#routes
@app.route('/')
def home():
    import random
    cat = request.args.get('category')
    subcat = request.args.get('subcategory')
    
    # Берем твои новые товары
    items = PRODUCTS.copy()
    
    # Фильтруем, если выбрана категория
    if cat:
        items = [p for p in items if p['category'] == cat]
        
        # Если выбрана подкатегория и это Accessories, фильтруем дальше
        if subcat and cat == 'Accessories':
            items = [p for p in items if p.get('subcategory', '').lower() == subcat.lower()]
    
    else:
        # Если мы на главной — перемешиваем для "разброса"
        random.shuffle(items)
        
    return render_template('index.html', products=items, categories=CATEGORIES)

@app.route('/search')
def search():
    query = request.args.get('q', '').strip().lower()
    
    if not query:
        # If no search query, redirect to home
        return redirect(url_for('home'))
    
    # Filter products based on search query
    # Search in name, category, and subcategory
    search_results = []
    for product in PRODUCTS:
        product_text = f"{product['name']} {product['category']} {product.get('subcategory', '')}".lower()
        if query in product_text:
            search_results.append(product)
    
    return render_template('index.html', 
                         products=search_results, 
                         categories=CATEGORIES, 
                         is_search=True, 
                         query=query)
@app.route('/product/<int:pid>')
def product_detail(pid):
    p = next((i for i in PRODUCTS if i['id'] == pid), None)
    reviews = ["Great quality!", "Very traditional.", "Excellent handmade work.", "Beautiful colors!"]
    ai_reviews = random.sample(reviews, 2)
    return render_template('product.html', product=p, reviews=ai_reviews)

# FIXED: Added methods=['POST'] and matched 'pid' to HTML
@app.route('/add_to_cart/<int:pid>', methods=['POST'])
@login_required
def add_to_cart(pid):
    if 'cart' not in session:
        session['cart'] = []
    session['cart'].append(pid)
    session.modified = True
    flash("Sebede goşuldy!")
    return redirect(url_for('cart'))

@app.route('/cart')
@login_required
def cart():
    cart_ids = session.get('cart', [])
    # Get details for every ID in the cart session
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
        flash("Ýalňyş ulanyjy ady ýa-da parol.")
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
