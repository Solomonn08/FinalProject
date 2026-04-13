import os
import random
import requests
import stripe
from dotenv import load_dotenv
from collections import Counter
from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_babel import Babel, gettext as _
from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'turkmen_biz_2026')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///turkmen_biz.db'
app.config['BABEL_DEFAULT_LOCALE'] = 'en'
app.config['BABEL_DEFAULT_TIMEZONE'] = 'UTC'

# Stripe
app.config['STRIPE_SECRET_KEY'] = os.getenv('STRIPE_SECRET_KEY', '')
app.config['STRIPE_WEBHOOK_SECRET'] = os.getenv('STRIPE_WEBHOOK_SECRET', '')
app.config['DOMAIN_URL'] = os.getenv('DOMAIN_URL', 'http://127.0.0.1:5000')
app.config['CHECKOUT_CURRENCY'] = os.getenv('CHECKOUT_CURRENCY', 'usd')

stripe.api_key = app.config['STRIPE_SECRET_KEY']

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'


def get_locale():
    lang = request.args.get('lang')
    if lang and lang in ['en', 'ru', 'tk']:
        session['language'] = lang
        return lang

    if 'language' in session:
        return session['language']

    return request.accept_languages.best_match(['en', 'ru', 'tk'], default='en')


babel = Babel()
babel.init_app(app, locale_selector=get_locale)


@app.context_processor
def inject_translation_functions():
    return {
        '_': _,
        'get_translated_product_name': get_translated_product_name,
        'get_translated_product_description': get_translated_product_description
    }


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    dark_mode = db.Column(db.Boolean, default=False)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


CATEGORIES = ["Tahýa", "Carpets", "Bags", "Accessories", "Women", "Men", "Headwear", "Traditional"]

PRODUCTS = [
    # Tahýa
    {"id": 1, "name": "Traditional Tahýa", "category": "Tahýa", "subcategory": "Traditional", "price": 250, "img": "/static/images/tahya/t1.jpg"},
    {"id": 2, "name": "Elegant Tahýa", "category": "Tahýa", "subcategory": "Elegant", "price": 280, "img": "/static/images/tahya/t2.jpg"},
    {"id": 3, "name": "Colorful Tahýa", "category": "Tahýa", "subcategory": "Colorful", "price": 300, "img": "/static/images/tahya/t3.avif"},
    {"id": 4, "name": "Simple Tahýa", "category": "Tahýa", "subcategory": "Simple", "price": 220, "img": "/static/images/tahya/t4.jpg"},
    {"id": 5, "name": "Traditional Pattern Tahýa", "category": "Tahýa", "subcategory": "Traditional", "price": 260, "img": "/static/images/tahya/t5.jpg"},
    {"id": 6, "name": "Modern Tahýa", "category": "Tahýa", "subcategory": "Modern", "price": 240, "img": "/static/images/tahya/t6.webp"},
    {"id": 7, "name": "Festive Tahýa", "category": "Tahýa", "subcategory": "Festive", "price": 290, "img": "/static/images/tahya/t7.jpg"},
    {"id": 8, "name": "Wedding Tahýa", "category": "Tahýa", "subcategory": "Wedding", "price": 320, "img": "/static/images/tahya/t8.jpg"},
    {"id": 9, "name": "Daily Tahýa", "category": "Tahýa", "subcategory": "Daily", "price": 200, "img": "/static/images/tahya/t9.jpg"},
    {"id": 10, "name": "Special Occasion Tahýa", "category": "Tahýa", "subcategory": "Special", "price": 350, "img": "/static/images/tahya/t10.jpg"},

    # Carpets
    {"id": 11, "name": "Traditional Carpet", "category": "Carpets", "subcategory": "Traditional", "price": 3000, "img": "/static/images/carpets/image-1.jpg"},
    {"id": 12, "name": "Geometric Carpet", "category": "Carpets", "subcategory": "Geometric", "price": 3200, "img": "/static/images/carpets/image-2.jpg"},
    {"id": 13, "name": "Colorful Carpet", "category": "Carpets", "subcategory": "Colorful", "price": 3500, "img": "/static/images/carpets/images-3.jpg"},
    {"id": 14, "name": "Classic Carpet", "category": "Carpets", "subcategory": "Classic", "price": 2800, "img": "/static/images/carpets/image-4.jpg"},
    {"id": 15, "name": "Modern Carpet", "category": "Carpets", "subcategory": "Modern", "price": 3100, "img": "/static/images/carpets/image-5.jpg"},
    {"id": 16, "name": "Luxury Carpet", "category": "Carpets", "subcategory": "Luxury", "price": 4000, "img": "/static/images/carpets/image-6.jpg"},
    {"id": 17, "name": "Handmade Carpet", "category": "Carpets", "subcategory": "Handmade", "price": 3800, "img": "/static/images/carpets/image-7.jpg"},
    {"id": 18, "name": "Traditional Pattern Carpet", "category": "Carpets", "subcategory": "Traditional", "price": 3300, "img": "/static/images/carpets/image-8.jpg"},
    {"id": 19, "name": "Elegant Carpet", "category": "Carpets", "subcategory": "Elegant", "price": 3600, "img": "/static/images/carpets/image-9.jpg"},
    {"id": 20, "name": "Royal Carpet", "category": "Carpets", "subcategory": "Royal", "price": 4200, "img": "/static/images/carpets/image-10.jpg"},

    # Bags
    {"id": 21, "name": "Traditional Bag", "category": "Bags", "subcategory": "Traditional", "price": 150, "img": "/static/images/bags/b1.jpg"},
    {"id": 22, "name": "Leather Bag", "category": "Bags", "subcategory": "Leather", "price": 180, "img": "/static/images/bags/b2.webp"},
    {"id": 23, "name": "Colorful Bag", "category": "Bags", "subcategory": "Colorful", "price": 160, "img": "/static/images/bags/b3.jpg"},
    {"id": 24, "name": "Simple Bag", "category": "Bags", "subcategory": "Simple", "price": 140, "img": "/static/images/bags/b4.webp"},
    {"id": 25, "name": "Elegant Bag", "category": "Bags", "subcategory": "Elegant", "price": 190, "img": "/static/images/bags/b5.jpg"},
    {"id": 26, "name": "Modern Bag", "category": "Bags", "subcategory": "Modern", "price": 170, "img": "/static/images/bags/b6.jpg"},
    {"id": 27, "name": "Festival Bag", "category": "Bags", "subcategory": "Festival", "price": 200, "img": "/static/images/bags/b7.jpg"},
    {"id": 28, "name": "Travel Bag", "category": "Bags", "subcategory": "Travel", "price": 220, "img": "/static/images/bags/b8.jpg"},
    {"id": 29, "name": "Daily Bag", "category": "Bags", "subcategory": "Daily", "price": 130, "img": "/static/images/bags/b9.jpg"},
    {"id": 30, "name": "Special Bag", "category": "Bags", "subcategory": "Special", "price": 250, "img": "/static/images/bags/b10.jpg"},

    # Accessories - Bracelets
    {"id": 31, "name": "Silver Bracelet", "category": "Accessories", "subcategory": "Bracelet", "price": 1200, "img": "/static/images/accessories/bracelets/bracelet1.avif"},
    {"id": 32, "name": "Gold Bracelet", "category": "Accessories", "subcategory": "Bracelet", "price": 1500, "img": "/static/images/accessories/bracelets/bracelet2.webp"},
    {"id": 33, "name": "Traditional Bracelet", "category": "Accessories", "subcategory": "Bracelet", "price": 1100, "img": "/static/images/accessories/bracelets/bracelet3.avif"},
    {"id": 34, "name": "Modern Bracelet", "category": "Accessories", "subcategory": "Bracelet", "price": 1300, "img": "/static/images/accessories/bracelets/bracelet4.avif"},
    {"id": 35, "name": "Elegant Bracelet", "category": "Accessories", "subcategory": "Bracelet", "price": 1400, "img": "/static/images/accessories/bracelets/bracelet5.avif"},
    {"id": 36, "name": "Simple Bracelet", "category": "Accessories", "subcategory": "Bracelet", "price": 1000, "img": "/static/images/accessories/bracelets/bracelet6.jpg"},
    {"id": 37, "name": "Festival Bracelet", "category": "Accessories", "subcategory": "Bracelet", "price": 1600, "img": "/static/images/accessories/bracelets/bracelet7.webp"},
    {"id": 38, "name": "Daily Bracelet", "category": "Accessories", "subcategory": "Bracelet", "price": 900, "img": "/static/images/accessories/bracelets/bracelet8.jpg"},
    {"id": 39, "name": "Special Bracelet", "category": "Accessories", "subcategory": "Bracelet", "price": 1800, "img": "/static/images/accessories/bracelets/bracelet9.avif"},
    {"id": 40, "name": "Luxury Bracelet", "category": "Accessories", "subcategory": "Bracelet", "price": 2000, "img": "/static/images/accessories/bracelets/bracelet10.avif"},

    # Accessories - Earrings
    {"id": 41, "name": "Traditional Earrings", "category": "Accessories", "subcategory": "Earrings", "price": 800, "img": "/static/images/accessories/earings/e1.jpg"},
    {"id": 42, "name": "Silver Earrings", "category": "Accessories", "subcategory": "Earrings", "price": 900, "img": "/static/images/accessories/earings/e2.avif"},
    {"id": 43, "name": "Gold Earrings", "category": "Accessories", "subcategory": "Earrings", "price": 1100, "img": "/static/images/accessories/earings/e3.avif"},
    {"id": 44, "name": "Modern Earrings", "category": "Accessories", "subcategory": "Earrings", "price": 700, "img": "/static/images/accessories/earings/e4.avif"},
    {"id": 45, "name": "Elegant Earrings", "category": "Accessories", "subcategory": "Earrings", "price": 1000, "img": "/static/images/accessories/earings/e5.avif"},
    {"id": 46, "name": "Simple Earrings", "category": "Accessories", "subcategory": "Earrings", "price": 600, "img": "/static/images/accessories/earings/e6.avif"},
    {"id": 47, "name": "Festival Earrings", "category": "Accessories", "subcategory": "Earrings", "price": 1200, "img": "/static/images/accessories/earings/e7.avif"},
    {"id": 48, "name": "Daily Earrings", "category": "Accessories", "subcategory": "Earrings", "price": 500, "img": "/static/images/accessories/earings/e8.webp"},
    {"id": 49, "name": "Special Earrings", "category": "Accessories", "subcategory": "Earrings", "price": 1400, "img": "/static/images/accessories/earings/e9.avif"},
    {"id": 50, "name": "Luxury Earrings", "category": "Accessories", "subcategory": "Earrings", "price": 1600, "img": "/static/images/accessories/earings/e10.avif"},

    # Accessories - Rings
    {"id": 51, "name": "Traditional Ring", "category": "Accessories", "subcategory": "Rings", "price": 2000, "img": "/static/images/accessories/rings/r1.jpg"},
    {"id": 52, "name": "Silver Ring", "category": "Accessories", "subcategory": "Rings", "price": 2200, "img": "/static/images/accessories/rings/r2.jpg"},
    {"id": 53, "name": "Gold Ring", "category": "Accessories", "subcategory": "Rings", "price": 2500, "img": "/static/images/accessories/rings/r3.avif"},
    {"id": 54, "name": "Modern Ring", "category": "Accessories", "subcategory": "Rings", "price": 2100, "img": "/static/images/accessories/rings/r4.webp"},
    {"id": 55, "name": "Elegant Ring", "category": "Accessories", "subcategory": "Rings", "price": 2400, "img": "/static/images/accessories/rings/r5.avif"},
    {"id": 56, "name": "Simple Ring", "category": "Accessories", "subcategory": "Rings", "price": 1800, "img": "/static/images/accessories/rings/r6.avif"},
    {"id": 57, "name": "Festival Ring", "category": "Accessories", "subcategory": "Rings", "price": 2600, "img": "/static/images/accessories/rings/r7.avif"},
    {"id": 58, "name": "Daily Ring", "category": "Accessories", "subcategory": "Rings", "price": 1600, "img": "/static/images/accessories/rings/r8.avif"},
    {"id": 59, "name": "Special Ring", "category": "Accessories", "subcategory": "Rings", "price": 2800, "img": "/static/images/accessories/rings/r9.avif"},
    {"id": 60, "name": "Luxury Ring", "category": "Accessories", "subcategory": "Rings", "price": 3000, "img": "/static/images/accessories/rings/r10.avif"},

    # Women
    {"id": 61, "name": "Traditional Dress", "category": "Women", "subcategory": "Traditional", "price": 400, "img": "/static/images/women dress/d1.avif"},
    {"id": 62, "name": "Elegant Dress", "category": "Women", "subcategory": "Elegant", "price": 450, "img": "/static/images/women dress/d2.webp"},
    {"id": 63, "name": "Colorful Dress", "category": "Women", "subcategory": "Colorful", "price": 420, "img": "/static/images/women dress/d3.avif"},
    {"id": 64, "name": "Simple Dress", "category": "Women", "subcategory": "Simple", "price": 380, "img": "/static/images/women dress/d4.avif"},
    {"id": 65, "name": "Modern Dress", "category": "Women", "subcategory": "Modern", "price": 480, "img": "/static/images/women dress/d5.avif"},
    {"id": 66, "name": "Festival Dress", "category": "Women", "subcategory": "Festival", "price": 500, "img": "/static/images/women dress/d6.webp"},
    {"id": 67, "name": "Daily Dress", "category": "Women", "subcategory": "Daily", "price": 350, "img": "/static/images/women dress/d7.webp"},
    {"id": 68, "name": "Wedding Dress", "category": "Women", "subcategory": "Wedding", "price": 600, "img": "/static/images/women dress/d8.webp"},
    {"id": 69, "name": "Special Occasion Dress", "category": "Women", "subcategory": "Special", "price": 550, "img": "/static/images/women dress/d9.webp"},
    {"id": 70, "name": "Luxury Dress", "category": "Women", "subcategory": "Luxury", "price": 700, "img": "/static/images/women dress/d10.avif"},

    # Men
    {"id": 71, "name": "Traditional Man Dress", "category": "Men", "subcategory": "Traditional", "price": 350, "img": "/static/images/man dress/m1.jpg"},
    {"id": 72, "name": "Elegant Man Dress", "category": "Men", "subcategory": "Elegant", "price": 380, "img": "/static/images/man dress/m2.webp"},
    {"id": 73, "name": "Simple Man Dress", "category": "Men", "subcategory": "Simple", "price": 320, "img": "/static/images/man dress/m3.webp"},
    {"id": 74, "name": "Modern Man Dress", "category": "Men", "subcategory": "Modern", "price": 400, "img": "/static/images/man dress/m4.avif"},
    {"id": 75, "name": "Festival Man Dress", "category": "Men", "subcategory": "Festival", "price": 420, "img": "/static/images/man dress/m5.avif"},
    {"id": 76, "name": "Daily Man Dress", "category": "Men", "subcategory": "Daily", "price": 300, "img": "/static/images/man dress/m6.webp"},
    {"id": 77, "name": "Special Man Dress", "category": "Men", "subcategory": "Special", "price": 450, "img": "/static/images/man dress/m7.avif"},
    {"id": 78, "name": "Luxury Man Dress", "category": "Men", "subcategory": "Luxury", "price": 500, "img": "/static/images/man dress/m8.jpg"},

    # Headwear
    {"id": 79, "name": "Traditional Headwear", "category": "Headwear", "subcategory": "Traditional", "price": 150, "img": "/static/images/on head/h1.webp"},
    {"id": 80, "name": "Elegant Headwear", "category": "Headwear", "subcategory": "Elegant", "price": 180, "img": "/static/images/on head/h2.webp"},
    {"id": 81, "name": "Simple Headwear", "category": "Headwear", "subcategory": "Simple", "price": 120, "img": "/static/images/on head/h3.avif"},
    {"id": 82, "name": "Modern Headwear", "category": "Headwear", "subcategory": "Modern", "price": 160, "img": "/static/images/on head/h4.avif"},
    {"id": 83, "name": "Festival Headwear", "category": "Headwear", "subcategory": "Festival", "price": 200, "img": "/static/images/on head/h5.avif"},
    {"id": 84, "name": "Daily Headwear", "category": "Headwear", "subcategory": "Daily", "price": 100, "img": "/static/images/on head/h6.jpg"},
    {"id": 85, "name": "Special Headwear", "category": "Headwear", "subcategory": "Special", "price": 220, "img": "/static/images/on head/h7.avif"},
    {"id": 86, "name": "Luxury Headwear", "category": "Headwear", "subcategory": "Luxury", "price": 250, "img": "/static/images/on head/h8.webp"},
    {"id": 87, "name": "Traditional Pattern Headwear", "category": "Headwear", "subcategory": "Traditional", "price": 190, "img": "/static/images/on head/h9.avif"},
    {"id": 88, "name": "Special Occasion Headwear", "category": "Headwear", "subcategory": "Special", "price": 280, "img": "/static/images/on head/h10.avif"},

    # Traditional / Telpek
    {"id": 89, "name": "Traditional Telpek", "category": "Traditional", "subcategory": "Traditional", "price": 500, "img": "/static/images/telpek/telpek1.webp"},
    {"id": 90, "name": "Elegant Telpek", "category": "Traditional", "subcategory": "Elegant", "price": 550, "img": "/static/images/telpek/telpek2.webp"},
    {"id": 91, "name": "Simple Telpek", "category": "Traditional", "subcategory": "Simple", "price": 450, "img": "/static/images/telpek/telpek3.webp"},
    {"id": 92, "name": "Modern Telpek", "category": "Traditional", "subcategory": "Modern", "price": 520, "img": "/static/images/telpek/telpek4.webp"},
    {"id": 93, "name": "Festival Telpek", "category": "Traditional", "subcategory": "Festival", "price": 600, "img": "/static/images/telpek/telpek5.webp"},
    {"id": 94, "name": "Daily Telpek", "category": "Traditional", "subcategory": "Daily", "price": 400, "img": "/static/images/telpek/telpek6.jpg"},
    {"id": 95, "name": "Special Telpek", "category": "Traditional", "subcategory": "Special", "price": 650, "img": "/static/images/telpek/telpek7.jpg"},
]


CATEGORY_TRANSLATIONS = {
    'ru': {
        'Tahýa': 'Тахыя',
        'Carpets': 'Ковры',
        'Bags': 'Сумки',
        'Accessories': 'Аксессуары',
        'Women': 'Женское',
        'Men': 'Мужское',
        'Headwear': 'Головные уборы',
        'Traditional': 'Традиционное'
    },
    'tk': {
        'Tahýa': 'Tahýa',
        'Carpets': 'Galymlar',
        'Bags': 'Çantalar',
        'Accessories': 'Aksesuarlar',
        'Women': 'Aýallar',
        'Men': 'Erkekler',
        'Headwear': 'Baş geýimler',
        'Traditional': 'Däp-dessur önümleri'
    }
}


NAME_TRANSLATIONS_RU = {
    "Traditional Tahýa": "Традиционная тахыя",
    "Elegant Tahýa": "Элегантная тахыя",
    "Colorful Tahýa": "Цветная тахыя",
    "Simple Tahýa": "Простая тахыя",
    "Traditional Pattern Tahýa": "Тахыя с традиционным узором",
    "Modern Tahýa": "Современная тахыя",
    "Festive Tahýa": "Праздничная тахыя",
    "Wedding Tahýa": "Свадебная тахыя",
    "Daily Tahýa": "Повседневная тахыя",
    "Special Occasion Tahýa": "Тахыя для особого случая",
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
    "Traditional Bag": "Традиционная сумка",
    "Leather Bag": "Кожаная сумка",
    "Colorful Bag": "Цветная сумка",
    "Simple Bag": "Простая сумка",
    "Elegant Bag": "Элегантная сумка",
    "Modern Bag": "Современная сумка",
    "Festival Bag": "Праздничная сумка",
    "Travel Bag": "Дорожная сумка",
    "Daily Bag": "Повседневная сумка",
    "Special Bag": "Особая сумка",
    "Silver Bracelet": "Серебряный браслет",
    "Gold Bracelet": "Золотой браслет",
    "Traditional Bracelet": "Традиционный браслет",
    "Modern Bracelet": "Современный браслет",
    "Elegant Bracelet": "Элегантный браслет",
    "Simple Bracelet": "Простой браслет",
    "Festival Bracelet": "Праздничный браслет",
    "Daily Bracelet": "Повседневный браслет",
    "Special Bracelet": "Особый браслет",
    "Luxury Bracelet": "Роскошный браслет",
    "Traditional Earrings": "Традиционные серьги",
    "Silver Earrings": "Серебряные серьги",
    "Gold Earrings": "Золотые серьги",
    "Modern Earrings": "Современные серьги",
    "Elegant Earrings": "Элегантные серьги",
    "Simple Earrings": "Простые серьги",
    "Festival Earrings": "Праздничные серьги",
    "Daily Earrings": "Повседневные серьги",
    "Special Earrings": "Особые серьги",
    "Luxury Earrings": "Роскошные серьги",
    "Traditional Ring": "Традиционное кольцо",
    "Silver Ring": "Серебряное кольцо",
    "Gold Ring": "Золотое кольцо",
    "Modern Ring": "Современное кольцо",
    "Elegant Ring": "Элегантное кольцо",
    "Simple Ring": "Простое кольцо",
    "Festival Ring": "Праздничное кольцо",
    "Daily Ring": "Повседневное кольцо",
    "Special Ring": "Особое кольцо",
    "Luxury Ring": "Роскошное кольцо",
    "Traditional Dress": "Традиционное платье",
    "Elegant Dress": "Элегантное платье",
    "Colorful Dress": "Цветное платье",
    "Simple Dress": "Простое платье",
    "Modern Dress": "Современное платье",
    "Festival Dress": "Праздничное платье",
    "Daily Dress": "Повседневное платье",
    "Wedding Dress": "Свадебное платье",
    "Special Occasion Dress": "Платье для особого случая",
    "Luxury Dress": "Роскошное платье",
    "Traditional Man Dress": "Традиционная мужская одежда",
    "Elegant Man Dress": "Элегантная мужская одежда",
    "Simple Man Dress": "Простая мужская одежда",
    "Modern Man Dress": "Современная мужская одежда",
    "Festival Man Dress": "Праздничная мужская одежда",
    "Daily Man Dress": "Повседневная мужская одежда",
    "Special Man Dress": "Особая мужская одежда",
    "Luxury Man Dress": "Роскошная мужская одежда",
    "Traditional Headwear": "Традиционный головной убор",
    "Elegant Headwear": "Элегантный головной убор",
    "Simple Headwear": "Простой головной убор",
    "Modern Headwear": "Современный головной убор",
    "Festival Headwear": "Праздничный головной убор",
    "Daily Headwear": "Повседневный головной убор",
    "Special Headwear": "Особый головной убор",
    "Luxury Headwear": "Роскошный головной убор",
    "Traditional Pattern Headwear": "Головной убор с традиционным узором",
    "Special Occasion Headwear": "Головной убор для особого случая",
    "Traditional Telpek": "Традиционный телпек",
    "Elegant Telpek": "Элегантный телпек",
    "Simple Telpek": "Простой телпек",
    "Modern Telpek": "Современный телпек",
    "Festival Telpek": "Праздничный телпек",
    "Daily Telpek": "Повседневный телпек",
    "Special Telpek": "Особый телпек",
}

NAME_TRANSLATIONS_TK = {
    "Traditional Tahýa": "Geleneksel Tahýa",
    "Elegant Tahýa": "Owadan Tahýa",
    "Colorful Tahýa": "Reňkli Tahýa",
    "Simple Tahýa": "Ýönekeý Tahýa",
    "Traditional Pattern Tahýa": "Nagyşly Tahýa",
    "Modern Tahýa": "Modern Tahýa",
    "Festive Tahýa": "Baýramçylyk Tahýasy",
    "Wedding Tahýa": "Toý Tahýasy",
    "Daily Tahýa": "Gündelik Tahýa",
    "Special Occasion Tahýa": "Ýörite Tahýa",
    "Traditional Carpet": "Geleneksel Haly",
    "Geometric Carpet": "Geometrik Haly",
    "Colorful Carpet": "Reňkli Haly",
    "Classic Carpet": "Klassik Haly",
    "Modern Carpet": "Modern Haly",
    "Luxury Carpet": "Gymmat Haly",
    "Handmade Carpet": "Elden edilen Haly",
    "Traditional Pattern Carpet": "Nagyşly Haly",
    "Elegant Carpet": "Owadan Haly",
    "Royal Carpet": "Patyşalyk Halysy",
    "Traditional Bag": "Geleneksel Çanta",
    "Leather Bag": "Deri Çanta",
    "Colorful Bag": "Reňkli Çanta",
    "Simple Bag": "Ýönekeý Çanta",
    "Elegant Bag": "Owadan Çanta",
    "Modern Bag": "Modern Çanta",
    "Festival Bag": "Baýramçylyk Çantasy",
    "Travel Bag": "Syýahat Çantasy",
    "Daily Bag": "Gündelik Çanta",
    "Special Bag": "Ýörite Çanta",
    "Silver Bracelet": "Kümüş Bilezik",
    "Gold Bracelet": "Altyn Bilezik",
    "Traditional Bracelet": "Geleneksel Bilezik",
    "Modern Bracelet": "Modern Bilezik",
    "Elegant Bracelet": "Owadan Bilezik",
    "Simple Bracelet": "Ýönekeý Bilezik",
    "Festival Bracelet": "Baýramçylyk Bilegzi",
    "Daily Bracelet": "Gündelik Bilezik",
    "Special Bracelet": "Ýörite Bilezik",
    "Luxury Bracelet": "Gymmat Bilezik",
    "Traditional Earrings": "Geleneksel Gulakhalka",
    "Silver Earrings": "Kümüş Gulakhalka",
    "Gold Earrings": "Altyn Gulakhalka",
    "Modern Earrings": "Modern Gulakhalka",
    "Elegant Earrings": "Owadan Gulakhalka",
    "Simple Earrings": "Ýönekeý Gulakhalka",
    "Festival Earrings": "Baýramçylyk Gulakhalka",
    "Daily Earrings": "Gündelik Gulakhalka",
    "Special Earrings": "Ýörite Gulakhalka",
    "Luxury Earrings": "Gymmat Gulakhalka",
    "Traditional Ring": "Geleneksel Ýüzük",
    "Silver Ring": "Kümüş Ýüzük",
    "Gold Ring": "Altyn Ýüzük",
    "Modern Ring": "Modern Ýüzük",
    "Elegant Ring": "Owadan Ýüzük",
    "Simple Ring": "Ýönekeý Ýüzük",
    "Festival Ring": "Baýramçylyk Ýüzügi",
    "Daily Ring": "Gündelik Ýüzük",
    "Special Ring": "Ýörite Ýüzük",
    "Luxury Ring": "Gymmat Ýüzük",
    "Traditional Dress": "Geleneksel Köýnek",
    "Elegant Dress": "Owadan Köýnek",
    "Colorful Dress": "Reňkli Köýnek",
    "Simple Dress": "Ýönekeý Köýnek",
    "Modern Dress": "Modern Köýnek",
    "Festival Dress": "Baýramçylyk Köýnegi",
    "Daily Dress": "Gündelik Köýnek",
    "Wedding Dress": "Toý Köýnegi",
    "Special Occasion Dress": "Ýörite Köýnek",
    "Luxury Dress": "Gymmat Köýnek",
    "Traditional Man Dress": "Geleneksel Erkek Egin-eşigi",
    "Elegant Man Dress": "Owadan Erkek Egin-eşigi",
    "Simple Man Dress": "Ýönekeý Erkek Egin-eşigi",
    "Modern Man Dress": "Modern Erkek Egin-eşigi",
    "Festival Man Dress": "Baýramçylyk Erkek Egin-eşigi",
    "Daily Man Dress": "Gündelik Erkek Egin-eşigi",
    "Special Man Dress": "Ýörite Erkek Egin-eşigi",
    "Luxury Man Dress": "Gymmat Erkek Egin-eşigi",
    "Traditional Headwear": "Geleneksel Baş Geýim",
    "Elegant Headwear": "Owadan Baş Geýim",
    "Simple Headwear": "Ýönekeý Baş Geýim",
    "Modern Headwear": "Modern Baş Geýim",
    "Festival Headwear": "Baýramçylyk Baş Geýim",
    "Daily Headwear": "Gündelik Baş Geýim",
    "Special Headwear": "Ýörite Baş Geýim",
    "Luxury Headwear": "Gymmat Baş Geýim",
    "Traditional Pattern Headwear": "Nagyşly Baş Geýim",
    "Special Occasion Headwear": "Ýörite Baş Geýim",
    "Traditional Telpek": "Geleneksel Telpek",
    "Elegant Telpek": "Owadan Telpek",
    "Simple Telpek": "Ýönekeý Telpek",
    "Modern Telpek": "Modern Telpek",
    "Festival Telpek": "Baýramçylyk Telpegi",
    "Daily Telpek": "Gündelik Telpek",
    "Special Telpek": "Ýörite Telpek",
}


def get_translated_product_name(product_name, category_name):
    locale = get_locale()

    if locale == 'en':
        return product_name

    if locale == 'ru':
        return NAME_TRANSLATIONS_RU.get(product_name, product_name)

    if locale == 'tk':
        return NAME_TRANSLATIONS_TK.get(product_name, product_name)

    return product_name


def get_translated_product_description(product_name, category_name):
    locale = get_locale()

    if locale == 'ru':
        category_ru = CATEGORY_TRANSLATIONS['ru'].get(category_name, category_name)
        return f"Традиционный туркменский товар из категории {category_ru}"

    if locale == 'tk':
        category_tk = CATEGORY_TRANSLATIONS['tk'].get(category_name, category_name)
        return f"{category_tk} kategoriýasyndaky däp bolan türkmen önümi"

    return "Traditional Turkmen product"


def build_cart_items():
    cart_ids = session.get('cart', [])
    counts = Counter(cart_ids)

    items = []
    total = 0

    for pid, qty in counts.items():
        product = next((p for p in PRODUCTS if p['id'] == pid), None)
        if product:
            item = product.copy()
            item['qty'] = qty
            item['line_total'] = product['price'] * qty
            items.append(item)
            total += item['line_total']

    return items, total


@app.route('/')
def home():
    cat = request.args.get('category')
    subcat = request.args.get('subcategory')

    items = PRODUCTS.copy()

    if cat:
        items = [p for p in items if p['category'] == cat]

        if subcat and cat == 'Accessories':
            items = [p for p in items if p.get('subcategory', '').lower() == subcat.lower()]
    else:
        random.shuffle(items)

    return render_template('index.html', products=items, categories=CATEGORIES)


@app.route('/search')
def search():
    query = request.args.get('q', '').strip().lower()

    if not query:
        return redirect(url_for('home'))

    search_results = []
    for product in PRODUCTS:
        product_text = f"{product['name']} {product['category']} {product.get('subcategory', '')}".lower()
        if query in product_text:
            search_results.append(product)

    return render_template(
        'index.html',
        products=search_results,
        categories=CATEGORIES,
        is_search=True,
        query=query
    )


@app.route('/product/<int:pid>')
def product_detail(pid):
    p = next((i for i in PRODUCTS if i['id'] == pid), None)
    if not p:
        flash("Product not found.")
        return redirect(url_for('home'))

    reviews = ["Great quality!", "Very traditional.", "Excellent handmade work.", "Beautiful colors!"]
    ai_reviews = random.sample(reviews, 2)
    return render_template('product.html', product=p, reviews=ai_reviews)


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
    items, total = build_cart_items()
    return render_template('cart.html', items=items, total=total)


@app.route('/create-checkout-session', methods=['POST'])
@login_required
def create_checkout_session():
    items, total = build_cart_items()

    if not items:
        flash("Your cart is empty.")
        return redirect(url_for('cart'))

    line_items = []
    for item in items:
        line_items.append({
            'price_data': {
                'currency': app.config['CHECKOUT_CURRENCY'],
                'product_data': {
                    'name': get_translated_product_name(item['name'], item['category']),
                    'description': get_translated_product_description(item['name'], item['category']),
                },
                'unit_amount': int(item['price'] * 100),
            },
            'quantity': item['qty'],
        })

    try:
        checkout_session = stripe.checkout.Session.create(
            mode='payment',
            line_items=line_items,
            success_url=app.config['DOMAIN_URL'] + url_for('checkout_success') + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=app.config['DOMAIN_URL'] + url_for('checkout_cancel'),
            client_reference_id=str(current_user.id),
        )
        return redirect(checkout_session.url, code=303)

    except Exception as e:
        flash(f"Payment error: {str(e)}")
        return redirect(url_for('cart'))


@app.route('/checkout/success')
@login_required
def checkout_success():
    session_id = request.args.get('session_id')

    if not session_id:
        flash("Session not found.")
        return redirect(url_for('cart'))

    try:
        checkout_session = stripe.checkout.Session.retrieve(session_id)

        if checkout_session.payment_status == 'paid':
            session['cart'] = []
            session.modified = True
            return render_template('success.html')

        flash("Payment is not completed yet.")
        return redirect(url_for('cart'))

    except Exception as e:
        flash(f"Verification error: {str(e)}")
        return redirect(url_for('cart'))


@app.route('/checkout/cancel')
def checkout_cancel():
    flash("Payment was cancelled.")
    return render_template('cancel.html')


@app.route('/stripe/webhook', methods=['POST'])
def stripe_webhook():
    payload = request.get_data()
    sig_header = request.headers.get('Stripe-Signature')

    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            app.config['STRIPE_WEBHOOK_SECRET']
        )
    except Exception:
        return 'Invalid webhook', 400

    if event['type'] == 'checkout.session.completed':
        stripe_session = event['data']['object']
        print('Payment completed:', stripe_session.get('id'))

    return '', 200


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
        existing_user = User.query.filter_by(username=request.form['username']).first()
        if existing_user:
            flash("This username already exists.")
            return redirect(url_for('register'))

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


@app.route('/culture')
def culture():
    return render_template('culture.html')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)