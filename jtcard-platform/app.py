#!/usr/bin/env python3
"""
JTCard Platform - Flask Backend Application
Professional digital business card platform with complete functionality
"""

import os
import sqlite3
import hashlib
import secrets
import json
from datetime import datetime, timedelta
from functools import wraps
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, request, jsonify, session, redirect, url_for, render_template_string, send_from_directory
import qrcode
from io import BytesIO
import base64

# Initialize Flask app
app = Flask(__name__)
app.secret_key = secrets.token_hex(32)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'profiles'), exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'covers'), exist_ok=True)

# Allowed file extensions for uploads
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def init_database():
    """Initialize SQLite database with all required tables"""
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
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT 1,
            subscription_plan TEXT DEFAULT 'free'
        )
    ''')
    
    # Business cards table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS business_cards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            template_id TEXT DEFAULT 'modern',
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Card data table (stores all card information)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS card_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            card_id INTEGER NOT NULL,
            field_name TEXT NOT NULL,
            field_value TEXT,
            is_visible BOOLEAN DEFAULT 1,
            sort_order INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (card_id) REFERENCES business_cards (id),
            UNIQUE(card_id, field_name)
        )
    ''')
    
    # Social media links table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS social_links (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            card_id INTEGER NOT NULL,
            platform TEXT NOT NULL,
            url TEXT NOT NULL,
            is_visible BOOLEAN DEFAULT 1,
            sort_order INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (card_id) REFERENCES business_cards (id)
        )
    ''')
    
    # Card analytics table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS card_analytics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            card_id INTEGER NOT NULL,
            event_type TEXT NOT NULL,
            ip_address TEXT,
            user_agent TEXT,
            referrer TEXT,
            country TEXT,
            city TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (card_id) REFERENCES business_cards (id)
        )
    ''')
    
    # File uploads table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS file_uploads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            card_id INTEGER NOT NULL,
            file_type TEXT NOT NULL,
            original_filename TEXT NOT NULL,
            stored_filename TEXT NOT NULL,
            file_size INTEGER,
            mime_type TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (card_id) REFERENCES business_cards (id)
        )
    ''')
    
    conn.commit()
    conn.close()

def get_db_connection():
    """Get database connection with row factory"""
    conn = sqlite3.connect('jtcard.db')
    conn.row_factory = sqlite3.Row
    return conn

def login_required(f):
    """Decorator to require login for protected routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

def generate_qr_code(data):
    """Generate QR code for card sharing"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    # Convert to base64 for easy embedding
    img_base64 = base64.b64encode(buffer.getvalue()).decode()
    return f"data:image/png;base64,{img_base64}"

# API Routes

@app.route('/api/register', methods=['POST'])
def register():
    """User registration endpoint"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['email', 'password', 'firstName', 'lastName']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if user already exists
        conn = get_db_connection()
        existing_user = conn.execute(
            'SELECT id FROM users WHERE email = ?', (data['email'],)
        ).fetchone()
        
        if existing_user:
            conn.close()
            return jsonify({'error': 'Email already registered'}), 400
        
        # Create new user
        password_hash = generate_password_hash(data['password'])
        cursor = conn.execute(
            '''INSERT INTO users (email, password_hash, first_name, last_name)
               VALUES (?, ?, ?, ?)''',
            (data['email'], password_hash, data['firstName'], data['lastName'])
        )
        
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # Set session
        session['user_id'] = user_id
        session['user_email'] = data['email']
        session['user_name'] = f"{data['firstName']} {data['lastName']}"
        
        return jsonify({
            'success': True,
            'message': 'Registration successful',
            'user': {
                'id': user_id,
                'email': data['email'],
                'name': session['user_name']
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/login', methods=['POST'])
def login():
    """User login endpoint"""
    try:
        data = request.get_json()
        
        if not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password are required'}), 400
        
        conn = get_db_connection()
        user = conn.execute(
            'SELECT * FROM users WHERE email = ? AND is_active = 1',
            (data['email'],)
        ).fetchone()
        conn.close()
        
        if not user or not check_password_hash(user['password_hash'], data['password']):
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Set session
        session['user_id'] = user['id']
        session['user_email'] = user['email']
        session['user_name'] = f"{user['first_name']} {user['last_name']}"
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'user': {
                'id': user['id'],
                'email': user['email'],
                'name': session['user_name']
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/logout', methods=['POST'])
def logout():
    """User logout endpoint"""
    session.clear()
    return jsonify({'success': True, 'message': 'Logged out successfully'})

@app.route('/api/user/profile', methods=['GET'])
@login_required
def get_user_profile():
    """Get user profile information"""
    try:
        conn = get_db_connection()
        user = conn.execute(
            'SELECT id, email, first_name, last_name, subscription_plan, created_at FROM users WHERE id = ?',
            (session['user_id'],)
        ).fetchone()
        conn.close()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'user': {
                'id': user['id'],
                'email': user['email'],
                'firstName': user['first_name'],
                'lastName': user['last_name'],
                'subscriptionPlan': user['subscription_plan'],
                'createdAt': user['created_at']
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/cards', methods=['GET'])
@login_required
def get_user_cards():
    """Get all cards for the current user"""
    try:
        conn = get_db_connection()
        cards = conn.execute(
            '''SELECT bc.*, 
                      COUNT(ca.id) as view_count,
                      MAX(ca.created_at) as last_viewed
               FROM business_cards bc
               LEFT JOIN card_analytics ca ON bc.id = ca.card_id AND ca.event_type = 'view'
               WHERE bc.user_id = ? AND bc.is_active = 1
               GROUP BY bc.id
               ORDER BY bc.created_at DESC''',
            (session['user_id'],)
        ).fetchall()
        
        cards_list = []
        for card in cards:
            # Get card data
            card_data = conn.execute(
                'SELECT field_name, field_value FROM card_data WHERE card_id = ? AND is_visible = 1',
                (card['id'],)
            ).fetchall()
            
            # Get social links
            social_links = conn.execute(
                'SELECT platform, url FROM social_links WHERE card_id = ? AND is_visible = 1 ORDER BY sort_order',
                (card['id'],)
            ).fetchall()
            
            cards_list.append({
                'id': card['id'],
                'title': card['title'],
                'templateId': card['template_id'],
                'isActive': bool(card['is_active']),
                'createdAt': card['created_at'],
                'updatedAt': card['updated_at'],
                'viewCount': card['view_count'] or 0,
                'lastViewed': card['last_viewed'],
                'data': {row['field_name']: row['field_value'] for row in card_data},
                'socialLinks': [{'platform': row['platform'], 'url': row['url']} for row in social_links]
            })
        
        conn.close()
        return jsonify({'cards': cards_list})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/cards', methods=['POST'])
@login_required
def create_card():
    """Create a new business card"""
    try:
        data = request.get_json()
        
        if not data.get('title'):
            return jsonify({'error': 'Card title is required'}), 400
        
        conn = get_db_connection()
        cursor = conn.execute(
            '''INSERT INTO business_cards (user_id, title, template_id)
               VALUES (?, ?, ?)''',
            (session['user_id'], data['title'], data.get('templateId', 'modern'))
        )
        
        card_id = cursor.lastrowid
        
        # Add default card data
        default_data = {
            'fullName': session['user_name'],
            'email': session['user_email'],
            'jobTitle': '',
            'company': '',
            'phone': '',
            'website': '',
            'bio': '',
            'address': ''
        }
        
        for field_name, field_value in default_data.items():
            conn.execute(
                '''INSERT INTO card_data (card_id, field_name, field_value)
                   VALUES (?, ?, ?)''',
                (card_id, field_name, field_value)
            )
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Card created successfully',
            'cardId': card_id
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/cards/<int:card_id>', methods=['GET'])
def get_card(card_id):
    """Get card details (public endpoint for viewing cards)"""
    try:
        conn = get_db_connection()
        
        # Get card basic info
        card = conn.execute(
            'SELECT * FROM business_cards WHERE id = ? AND is_active = 1',
            (card_id,)
        ).fetchone()
        
        if not card:
            conn.close()
            return jsonify({'error': 'Card not found'}), 404
        
        # Get card data
        card_data = conn.execute(
            'SELECT field_name, field_value FROM card_data WHERE card_id = ? AND is_visible = 1',
            (card_id,)
        ).fetchall()
        
        # Get social links
        social_links = conn.execute(
            'SELECT platform, url FROM social_links WHERE card_id = ? AND is_visible = 1 ORDER BY sort_order',
            (card_id,)
        ).fetchall()
        
        # Get file uploads
        files = conn.execute(
            'SELECT file_type, stored_filename FROM file_uploads WHERE card_id = ?',
            (card_id,)
        ).fetchall()
        
        # Record analytics (view event)
        conn.execute(
            '''INSERT INTO card_analytics (card_id, event_type, ip_address, user_agent)
               VALUES (?, ?, ?, ?)''',
            (card_id, 'view', request.remote_addr, request.headers.get('User-Agent', ''))
        )
        
        conn.commit()
        conn.close()
        
        # Generate QR code for sharing
        card_url = f"{request.host_url}card/{card_id}"
        qr_code = generate_qr_code(card_url)
        
        return jsonify({
            'card': {
                'id': card['id'],
                'title': card['title'],
                'templateId': card['template_id'],
                'data': {row['field_name']: row['field_value'] for row in card_data},
                'socialLinks': [{'platform': row['platform'], 'url': row['url']} for row in social_links],
                'files': {row['file_type']: row['stored_filename'] for row in files},
                'qrCode': qr_code,
                'shareUrl': card_url
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/cards/<int:card_id>', methods=['PUT'])
@login_required
def update_card(card_id):
    """Update card information"""
    try:
        data = request.get_json()
        
        conn = get_db_connection()
        
        # Verify card ownership
        card = conn.execute(
            'SELECT user_id FROM business_cards WHERE id = ?',
            (card_id,)
        ).fetchone()
        
        if not card or card['user_id'] != session['user_id']:
            conn.close()
            return jsonify({'error': 'Card not found or access denied'}), 404
        
        # Update card basic info
        if 'title' in data:
            conn.execute(
                'UPDATE business_cards SET title = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
                (data['title'], card_id)
            )
        
        if 'templateId' in data:
            conn.execute(
                'UPDATE business_cards SET template_id = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
                (data['templateId'], card_id)
            )
        
        # Update card data fields
        if 'data' in data:
            for field_name, field_value in data['data'].items():
                conn.execute(
                    '''INSERT OR REPLACE INTO card_data (card_id, field_name, field_value, updated_at)
                       VALUES (?, ?, ?, CURRENT_TIMESTAMP)''',
                    (card_id, field_name, field_value)
                )
        
        # Update social links
        if 'socialLinks' in data:
            # Delete existing social links
            conn.execute('DELETE FROM social_links WHERE card_id = ?', (card_id,))
            
            # Add new social links
            for i, link in enumerate(data['socialLinks']):
                if link.get('url'):  # Only add if URL is provided
                    conn.execute(
                        '''INSERT INTO social_links (card_id, platform, url, is_visible, sort_order)
                           VALUES (?, ?, ?, ?, ?)''',
                        (card_id, link['platform'], link['url'], link.get('isVisible', True), i)
                    )
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Card updated successfully'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/cards/<int:card_id>/upload', methods=['POST'])
@login_required
def upload_card_file(card_id):
    """Upload profile or cover image for a card"""
    try:
        # Verify card ownership
        conn = get_db_connection()
        card = conn.execute(
            'SELECT user_id FROM business_cards WHERE id = ?',
            (card_id,)
        ).fetchone()
        
        if not card or card['user_id'] != session['user_id']:
            conn.close()
            return jsonify({'error': 'Card not found or access denied'}), 404
        
        file_type = request.form.get('type')  # 'profile' or 'cover'
        if file_type not in ['profile', 'cover']:
            return jsonify({'error': 'Invalid file type'}), 400
        
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type'}), 400
        
        # Generate secure filename
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        stored_filename = f"{card_id}_{file_type}_{timestamp}_{filename}"
        
        # Save file
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{file_type}s", stored_filename)
        file.save(file_path)
        
        # Delete old file of same type
        old_file = conn.execute(
            'SELECT stored_filename FROM file_uploads WHERE card_id = ? AND file_type = ?',
            (card_id, file_type)
        ).fetchone()
        
        if old_file:
            old_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{file_type}s", old_file['stored_filename'])
            if os.path.exists(old_path):
                os.remove(old_path)
            
            conn.execute('DELETE FROM file_uploads WHERE card_id = ? AND file_type = ?', (card_id, file_type))
        
        # Save file info to database
        conn.execute(
            '''INSERT INTO file_uploads (card_id, file_type, original_filename, stored_filename, file_size, mime_type)
               VALUES (?, ?, ?, ?, ?, ?)''',
            (card_id, file_type, filename, stored_filename, os.path.getsize(file_path), file.mimetype)
        )
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': f'{file_type.title()} image uploaded successfully',
            'filename': stored_filename,
            'url': f'/uploads/{file_type}s/{stored_filename}'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/cards/<int:card_id>/analytics', methods=['GET'])
@login_required
def get_card_analytics(card_id):
    """Get analytics data for a card"""
    try:
        conn = get_db_connection()
        
        # Verify card ownership
        card = conn.execute(
            'SELECT user_id FROM business_cards WHERE id = ?',
            (card_id,)
        ).fetchone()
        
        if not card or card['user_id'] != session['user_id']:
            conn.close()
            return jsonify({'error': 'Card not found or access denied'}), 404
        
        # Get analytics data
        total_views = conn.execute(
            'SELECT COUNT(*) as count FROM card_analytics WHERE card_id = ? AND event_type = "view"',
            (card_id,)
        ).fetchone()['count']
        
        # Views by date (last 30 days)
        views_by_date = conn.execute(
            '''SELECT DATE(created_at) as date, COUNT(*) as views
               FROM card_analytics
               WHERE card_id = ? AND event_type = "view" AND created_at >= date('now', '-30 days')
               GROUP BY DATE(created_at)
               ORDER BY date''',
            (card_id,)
        ).fetchall()
        
        # Recent activity
        recent_activity = conn.execute(
            '''SELECT event_type, created_at, ip_address
               FROM card_analytics
               WHERE card_id = ?
               ORDER BY created_at DESC
               LIMIT 10''',
            (card_id,)
        ).fetchall()
        
        conn.close()
        
        return jsonify({
            'analytics': {
                'totalViews': total_views,
                'viewsByDate': [{'date': row['date'], 'views': row['views']} for row in views_by_date],
                'recentActivity': [
                    {
                        'eventType': row['event_type'],
                        'createdAt': row['created_at'],
                        'ipAddress': row['ip_address']
                    } for row in recent_activity
                ]
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# File serving routes
@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    """Serve uploaded files"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Public card view route
@app.route('/card/<int:card_id>')
def view_card(card_id):
    """Public card viewing page"""
    # This would render a card viewing template
    # For now, redirect to the card preview page with the card ID
    return redirect(f'/card-preview.html?id={card_id}')

# Health check endpoint
@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

# Initialize database on startup
if __name__ == '__main__':
    init_database()
    print("JTCard Platform Backend Starting...")
    print("Database initialized successfully")
    print("Server running on http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
