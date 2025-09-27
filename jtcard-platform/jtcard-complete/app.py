#!/usr/bin/env python3
"""
JTCard Platform - Professional Digital Business Cards
Render Deployment Version with PostgreSQL
"""

import os
import hashlib
import secrets
from datetime import datetime
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import qrcode
from io import BytesIO
import base64
from dotenv import load_dotenv
import sqlite3


# Load environment variables
load_dotenv()

# Database imports - try PostgreSQL first, fallback to SQLite
try:
    import psycopg2
    import psycopg2.extras
    USE_POSTGRESQL = True
except ImportError:
    import sqlite3
    USE_POSTGRESQL = False

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(32))
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'profiles'), exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'covers'), exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_db_connection():
    """Get database connection - PostgreSQL for production, SQLite for development"""
    if USE_POSTGRESQL and os.environ.get('DATABASE_URL'):
        conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
        return conn
    else:
        # Fallback to SQLite
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'jtcard.db')
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn

def init_database():
    """Initialize database tables"""
    conn = get_db_connection()
    
    if USE_POSTGRESQL and os.environ.get('DATABASE_URL'):
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                first_name VARCHAR(100) NOT NULL,
                last_name VARCHAR(100) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE
            )
        ''')
        
        # Business cards table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS business_cards (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id),
                title VARCHAR(255) NOT NULL,
                full_name VARCHAR(255),
                job_title VARCHAR(255),
                company VARCHAR(255),
                email VARCHAR(255),
                phone VARCHAR(50),
                website VARCHAR(255),
                bio TEXT,
                profile_image VARCHAR(255),
                cover_image VARCHAR(255),
                template_id VARCHAR(50) DEFAULT 'modern',
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Social links table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS social_links (
                id SERIAL PRIMARY KEY,
                card_id INTEGER NOT NULL REFERENCES business_cards(id),
                platform VARCHAR(50) NOT NULL,
                url VARCHAR(500) NOT NULL,
                is_visible BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
    else:
        # SQLite fallback
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
        ''')
        
        # Business cards table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS business_cards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                full_name TEXT,
                job_title TEXT,
                company TEXT,
                email TEXT,
                phone TEXT,
                website TEXT,
                bio TEXT,
                profile_image TEXT,
                cover_image TEXT,
                template_id TEXT DEFAULT 'modern',
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Social links table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS social_links (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                card_id INTEGER NOT NULL,
                platform TEXT NOT NULL,
                url TEXT NOT NULL,
                is_visible BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (card_id) REFERENCES business_cards (id)
            )
        ''')
    
    conn.commit()
    conn.close()

def execute_query(query, params=None, fetch=False):
    """Execute database query with proper connection handling"""
    conn = get_db_connection()
    
    if USE_POSTGRESQL and os.environ.get('DATABASE_URL'):
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    else:
        cursor = conn.cursor()
    
    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        if fetch == 'one':
            result = cursor.fetchone()
        elif fetch == 'all':
            result = cursor.fetchall()
        else:
            result = cursor.lastrowid if hasattr(cursor, 'lastrowid') else cursor.rowcount
        
        conn.commit()
        return result
    finally:
        conn.close()

def generate_qr_code(data):
    """Generate QR code for card sharing"""
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    img_base64 = base64.b64encode(buffer.getvalue()).decode()
    return f"data:image/png;base64,{img_base64}"

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/why-choose-us')
def why_choose_us():
    return render_template('why-choose-us.html')

@app.route('/templates')
def templates():
    return render_template('templates.html')

@app.route('/pricing')
def pricing():
    return render_template('pricing.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/privacy-policy')
def privacy_policy():
    return render_template('privacy-policy.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/customize')
def customize():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('customize.html')

# API Routes
@app.route('/api/register', methods=['POST'])
def register():
    try:
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400
            
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['firstName', 'lastName', 'email', 'password']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if user already exists
        existing_user = execute_query(
            'SELECT id FROM users WHERE email = %s' if USE_POSTGRESQL else 'SELECT id FROM users WHERE email = ?',
            (data['email'],),
            fetch='one'
        )
        
        if existing_user:
            return jsonify({'error': 'Email already registered'}), 400
        
        # Create new user
        password_hash = generate_password_hash(data['password'])
        
        if USE_POSTGRESQL:
            result = execute_query(
                'INSERT INTO users (email, password_hash, first_name, last_name) VALUES (%s, %s, %s, %s) RETURNING id',
                (data['email'], password_hash, data['firstName'], data['lastName']),
                fetch='one'
            )
            user_id = result['id']
        else:
            user_id = execute_query(
                'INSERT INTO users (email, password_hash, first_name, last_name) VALUES (?, ?, ?, ?)',
                (data['email'], password_hash, data['firstName'], data['lastName'])
            )
        
        # Log in the user
        session['user_id'] = user_id
        session['user_email'] = data['email']
        session['user_name'] = f"{data['firstName']} {data['lastName']}"
        
        return jsonify({'success': True, 'message': 'Account created successfully'})
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/login', methods=['POST'])
def api_login():
    try:
        data = request.get_json()
        
        if not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password are required'}), 400
        
        user = execute_query(
            'SELECT * FROM users WHERE email = %s AND is_active = TRUE' if USE_POSTGRESQL 
            else 'SELECT * FROM users WHERE email = ? AND is_active = 1',
            (data['email'],),
            fetch='one'
        )
        
        if not user or not check_password_hash(user['password_hash'], data['password']):
            return jsonify({'error': 'Invalid email or password'}), 401
        
        session['user_id'] = user['id']
        session['user_email'] = user['email']
        session['user_name'] = f"{user['first_name']} {user['last_name']}"
        
        return jsonify({'success': True, 'message': 'Login successful'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True, 'message': 'Logged out successfully'})

@app.route('/api/cards', methods=['GET'])
def get_cards():
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        cards = execute_query(
            'SELECT * FROM business_cards WHERE user_id = %s AND is_active = TRUE ORDER BY created_at DESC' if USE_POSTGRESQL
            else 'SELECT * FROM business_cards WHERE user_id = ? AND is_active = 1 ORDER BY created_at DESC',
            (session['user_id'],),
            fetch='all'
        )
        
        cards_list = []
        for card in cards:
            # Get social links
            social_links = execute_query(
                'SELECT platform, url FROM social_links WHERE card_id = %s AND is_visible = TRUE' if USE_POSTGRESQL
                else 'SELECT platform, url FROM social_links WHERE card_id = ? AND is_visible = 1',
                (card['id'],),
                fetch='all'
            )
            
            cards_list.append({
                'id': card['id'],
                'title': card['title'],
                'fullName': card['full_name'],
                'jobTitle': card['job_title'],
                'company': card['company'],
                'email': card['email'],
                'phone': card['phone'],
                'website': card['website'],
                'bio': card['bio'],
                'profileImage': card['profile_image'],
                'coverImage': card['cover_image'],
                'templateId': card['template_id'],
                'socialLinks': [{'platform': row['platform'], 'url': row['url']} for row in social_links],
                'createdAt': str(card['created_at'])
            })
        
        return jsonify({'cards': cards_list})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/cards', methods=['POST'])
def create_card():
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        data = request.get_json()
        
        if USE_POSTGRESQL:
            result = execute_query(
                '''INSERT INTO business_cards (user_id, title, full_name, job_title, company, email, phone, website, bio, template_id)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id''',
                (session['user_id'], data.get('title', 'My Card'), data.get('fullName', ''), 
                 data.get('jobTitle', ''), data.get('company', ''), data.get('email', ''),
                 data.get('phone', ''), data.get('website', ''), data.get('bio', ''), 
                 data.get('templateId', 'modern')),
                fetch='one'
            )
            card_id = result['id']
        else:
            card_id = execute_query(
                '''INSERT INTO business_cards (user_id, title, full_name, job_title, company, email, phone, website, bio, template_id)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (session['user_id'], data.get('title', 'My Card'), data.get('fullName', ''), 
                 data.get('jobTitle', ''), data.get('company', ''), data.get('email', ''),
                 data.get('phone', ''), data.get('website', ''), data.get('bio', ''), 
                 data.get('templateId', 'modern'))
            )
        
        # Add social links
        if 'socialLinks' in data:
            for link in data['socialLinks']:
                if link.get('url'):
                    execute_query(
                        'INSERT INTO social_links (card_id, platform, url) VALUES (%s, %s, %s)' if USE_POSTGRESQL
                        else 'INSERT INTO social_links (card_id, platform, url) VALUES (?, ?, ?)',
                        (card_id, link['platform'], link['url'])
                    )
        
        return jsonify({'success': True, 'cardId': card_id})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/card/<int:card_id>')
def view_card(card_id):
    try:
        card = execute_query(
            'SELECT * FROM business_cards WHERE id = %s AND is_active = TRUE' if USE_POSTGRESQL
            else 'SELECT * FROM business_cards WHERE id = ? AND is_active = 1',
            (card_id,),
            fetch='one'
        )
        
        if not card:
            return "Card not found", 404
        
        social_links = execute_query(
            'SELECT platform, url FROM social_links WHERE card_id = %s AND is_visible = TRUE' if USE_POSTGRESQL
            else 'SELECT platform, url FROM social_links WHERE card_id = ? AND is_visible = 1',
            (card_id,),
            fetch='all'
        )
        
        # Generate QR code
        card_url = f"{request.host_url}card/{card_id}"
        qr_code = generate_qr_code(card_url)
        
        return render_template('card-preview.html', card=card, social_links=social_links, qr_code=qr_code)
        
    except Exception as e:
        return f"Error: {str(e)}", 500

if __name__ == '__main__':
    # Initialize database on startup
    init_database()
    
    # Get port from environment variable or default to 8000
    port = int(os.environ.get('PORT', 8000))
    
    # Run the application
    app.run(host='0.0.0.0', port=port, debug=False)
