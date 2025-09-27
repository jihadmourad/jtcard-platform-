from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
import os
import sqlite3
import hashlib
import secrets
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import qrcode
from io import BytesIO
import base64

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'profiles'), exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'covers'), exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def init_database():
    """Initialize SQLite database"""
    conn = sqlite3.connect('jtcard.db')
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

def get_db_connection():
    conn = sqlite3.connect('jtcard.db')
    conn.row_factory = sqlite3.Row
    return conn

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
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/why-choose-us')
def why_choose_us():
    return render_template('why-choose-us.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/privacy-policy')
def privacy_policy():
    return render_template('privacy-policy.html')

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/signup')
def signup_page():
    return render_template('signup.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    return render_template('dashboard.html')

@app.route('/customize')
def customize():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    return render_template('customize.html')

@app.route('/templates')
def templates():
    return render_template('templates.html')

@app.route('/pricing')
def pricing():
    return render_template('pricing.html')

# API Routes
@app.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        if not all(k in data for k in ['email', 'password', 'firstName', 'lastName']):
            return jsonify({'error': 'All fields are required'}), 400
        
        conn = get_db_connection()
        existing_user = conn.execute('SELECT id FROM users WHERE email = ?', (data['email'],)).fetchone()
        
        if existing_user:
            conn.close()
            return jsonify({'error': 'Email already registered'}), 400
        
        password_hash = generate_password_hash(data['password'])
        cursor = conn.execute(
            'INSERT INTO users (email, password_hash, first_name, last_name) VALUES (?, ?, ?, ?)',
            (data['email'], password_hash, data['firstName'], data['lastName'])
        )
        
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        session['user_id'] = user_id
        session['user_email'] = data['email']
        session['user_name'] = f"{data['firstName']} {data['lastName']}"
        
        return jsonify({'success': True, 'message': 'Registration successful'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        if not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password are required'}), 400
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE email = ? AND is_active = 1', (data['email'],)).fetchone()
        conn.close()
        
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
        conn = get_db_connection()
        cards = conn.execute(
            'SELECT * FROM business_cards WHERE user_id = ? AND is_active = 1 ORDER BY created_at DESC',
            (session['user_id'],)
        ).fetchall()
        
        cards_list = []
        for card in cards:
            # Get social links
            social_links = conn.execute(
                'SELECT platform, url FROM social_links WHERE card_id = ? AND is_visible = 1',
                (card['id'],)
            ).fetchall()
            
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
                'createdAt': card['created_at']
            })
        
        conn.close()
        return jsonify({'cards': cards_list})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/cards', methods=['POST'])
def create_card():
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        data = request.get_json()
        
        conn = get_db_connection()
        cursor = conn.execute(
            '''INSERT INTO business_cards (user_id, title, full_name, job_title, company, email, phone, website, bio, template_id)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (session['user_id'], data.get('title', 'My Card'), data.get('fullName', ''), 
             data.get('jobTitle', ''), data.get('company', ''), data.get('email', ''),
             data.get('phone', ''), data.get('website', ''), data.get('bio', ''), 
             data.get('templateId', 'modern'))
        )
        
        card_id = cursor.lastrowid
        
        # Add social links
        if 'socialLinks' in data:
            for link in data['socialLinks']:
                if link.get('url'):
                    conn.execute(
                        'INSERT INTO social_links (card_id, platform, url) VALUES (?, ?, ?)',
                        (card_id, link['platform'], link['url'])
                    )
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'cardId': card_id})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/cards/<int:card_id>', methods=['PUT'])
def update_card(card_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        data = request.get_json()
        
        conn = get_db_connection()
        
        # Verify ownership
        card = conn.execute('SELECT user_id FROM business_cards WHERE id = ?', (card_id,)).fetchone()
        if not card or card['user_id'] != session['user_id']:
            conn.close()
            return jsonify({'error': 'Card not found'}), 404
        
        # Update card
        conn.execute(
            '''UPDATE business_cards SET title = ?, full_name = ?, job_title = ?, company = ?, 
               email = ?, phone = ?, website = ?, bio = ?, template_id = ? WHERE id = ?''',
            (data.get('title'), data.get('fullName'), data.get('jobTitle'), data.get('company'),
             data.get('email'), data.get('phone'), data.get('website'), data.get('bio'),
             data.get('templateId'), card_id)
        )
        
        # Update social links
        conn.execute('DELETE FROM social_links WHERE card_id = ?', (card_id,))
        if 'socialLinks' in data:
            for link in data['socialLinks']:
                if link.get('url'):
                    conn.execute(
                        'INSERT INTO social_links (card_id, platform, url) VALUES (?, ?, ?)',
                        (card_id, link['platform'], link['url'])
                    )
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/card/<int:card_id>')
def view_card(card_id):
    try:
        conn = get_db_connection()
        card = conn.execute('SELECT * FROM business_cards WHERE id = ? AND is_active = 1', (card_id,)).fetchone()
        
        if not card:
            conn.close()
            return "Card not found", 404
        
        social_links = conn.execute(
            'SELECT platform, url FROM social_links WHERE card_id = ? AND is_visible = 1',
            (card_id,)
        ).fetchall()
        
        conn.close()
        
        # Generate QR code
        card_url = f"{request.host_url}card/{card_id}"
        qr_code = generate_qr_code(card_url)
        
        return render_template('card-preview.html', card=card, social_links=social_links, qr_code=qr_code)
        
    except Exception as e:
        return f"Error: {str(e)}", 500

if __name__ == '__main__':
    init_database()
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)
