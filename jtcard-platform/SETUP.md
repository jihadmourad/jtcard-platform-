# JTCard Platform - Setup & Deployment Guide

## 🚀 Quick Start

### Prerequisites
- Python 3.11+ installed
- Modern web browser
- Internet connection for CDN resources

### Installation Steps

1. **Extract the Platform**
   ```bash
   unzip jtcard-platform-enhanced.zip
   cd jtcard-platform
   ```

2. **Install Python Dependencies**
   ```bash
   pip3 install -r requirements.txt
   ```

3. **Start the Backend Server**
   ```bash
   python3 app.py
   ```
   The Flask backend will start on `http://localhost:5000`

4. **Start the Frontend Server**
   ```bash
   # In a new terminal window
   python3 -m http.server 8080
   ```
   The frontend will be available at `http://localhost:8080`

5. **Access the Platform**
   Open your browser and navigate to `http://localhost:8080`

## 📁 Project Structure

```
jtcard-platform/
├── app.py                 # Flask backend application
├── requirements.txt       # Python dependencies
├── jtcard.db             # SQLite database (auto-created)
├── uploads/              # User uploaded files
│   ├── profiles/         # Profile photos
│   └── covers/           # Cover photos
├── assets/               # Static assets
│   ├── css/
│   │   └── framework.css # Main CSS framework
│   └── js/
│       └── common.js     # Shared JavaScript
├── index.html            # Homepage
├── about.html            # About page
├── why-choose-us.html    # Why Choose Us page
├── contact.html          # Contact page
├── privacy-policy.html   # Privacy Policy page
├── login.html            # Login page
├── signup.html           # Signup page
├── dashboard.html        # User dashboard
├── customize.html        # Card editor
├── card-preview.html     # Card preview
├── templates.html        # Template gallery
├── pricing.html          # Pricing page
└── README.md             # Project documentation
```

## 🔧 Configuration

### Backend Configuration
The Flask app uses the following default settings:
- **Host**: `0.0.0.0` (all interfaces)
- **Port**: `5000`
- **Debug Mode**: `True` (disable for production)
- **Database**: SQLite (`jtcard.db`)
- **Upload Folder**: `uploads/`
- **Max File Size**: 16MB

### Frontend Configuration
The frontend is served as static files and communicates with the backend via AJAX requests to `http://localhost:5000/api/`

## 🗄️ Database Schema

The platform uses SQLite with the following tables:

### Users Table
- `id` - Primary key
- `email` - Unique user email
- `password_hash` - Hashed password
- `first_name`, `last_name` - User names
- `subscription_plan` - User's plan (free, pro, etc.)
- `created_at`, `updated_at` - Timestamps

### Business Cards Table
- `id` - Primary key
- `user_id` - Foreign key to users
- `title` - Card title
- `template_id` - Selected template
- `is_active` - Card status

### Card Data Table
- Stores all card field data (name, email, phone, etc.)
- Flexible key-value structure
- Visibility controls per field

### Social Links Table
- Stores social media links
- Platform identification
- Show/hide controls
- Sort ordering

### File Uploads Table
- Tracks uploaded profile and cover photos
- File metadata and paths
- Linked to specific cards

### Analytics Table
- Tracks card views and interactions
- IP addresses and user agents
- Referrer information

## 🎨 Features Overview

### ✅ Completed Features

**Frontend Pages:**
- ✅ Professional Homepage with hero section
- ✅ Comprehensive About Us page
- ✅ Detailed Why Choose Us page
- ✅ Multi-method Contact page
- ✅ Legal-compliant Privacy Policy
- ✅ Modern Login/Signup pages
- ✅ Feature-rich Dashboard
- ✅ Advanced Card Editor
- ✅ Template Gallery
- ✅ Pricing Plans

**Backend Functionality:**
- ✅ User authentication (register/login)
- ✅ Card CRUD operations
- ✅ File upload handling (profile/cover photos)
- ✅ Social media link management
- ✅ QR code generation
- ✅ Analytics tracking
- ✅ RESTful API endpoints

**Card Editor Features:**
- ✅ Real-time preview
- ✅ Profile & cover photo uploads
- ✅ 10+ social media platforms
- ✅ Show/hide social controls
- ✅ 6 professional templates
- ✅ Auto-save functionality
- ✅ QR code generation
- ✅ Share link creation

## 🔐 API Endpoints

### Authentication
- `POST /api/register` - User registration
- `POST /api/login` - User login
- `POST /api/logout` - User logout

### User Management
- `GET /api/user/profile` - Get user profile

### Card Management
- `GET /api/cards` - Get user's cards
- `POST /api/cards` - Create new card
- `GET /api/cards/{id}` - Get card details (public)
- `PUT /api/cards/{id}` - Update card
- `POST /api/cards/{id}/upload` - Upload photos

### Analytics
- `GET /api/cards/{id}/analytics` - Get card analytics

### Utility
- `GET /api/health` - Health check

## 🎯 Social Media Integration

The platform supports comprehensive social media integration with show/hide controls:

**Supported Platforms:**
- Facebook
- Instagram
- LinkedIn
- Twitter
- WhatsApp
- Telegram
- YouTube
- TikTok
- Snapchat
- Pinterest

**Features:**
- Individual show/hide toggles
- Custom URL validation
- Platform-specific icons
- Responsive design
- Direct link integration

## 📱 Mobile Responsiveness

All pages are fully responsive and optimized for:
- Desktop (1200px+)
- Tablet (768px - 1199px)
- Mobile (< 768px)

## 🔒 Security Features

- Password hashing with Werkzeug
- SQL injection prevention
- File upload validation
- Session management
- CSRF protection ready
- Input sanitization

## 🚀 Production Deployment

### Environment Setup
1. Set `debug=False` in `app.py`
2. Use a production WSGI server (Gunicorn, uWSGI)
3. Configure reverse proxy (Nginx, Apache)
4. Set up SSL certificates
5. Use environment variables for secrets

### Example Production Command
```bash
# Install Gunicorn
pip install gunicorn

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Nginx Configuration Example
```nginx
server {
    listen 80;
    server_name yourdomain.com;
    
    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /api/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /uploads/ {
        proxy_pass http://127.0.0.1:5000;
    }
}
```

## 🐛 Troubleshooting

### Common Issues

**Backend won't start:**
- Check Python version (3.11+ required)
- Install dependencies: `pip3 install -r requirements.txt`
- Check port 5000 availability

**Frontend can't connect to backend:**
- Ensure backend is running on port 5000
- Check CORS settings if needed
- Verify API endpoints in browser network tab

**File uploads not working:**
- Check `uploads/` directory permissions
- Verify file size limits (16MB max)
- Ensure supported file types (png, jpg, jpeg, gif, webp)

**Database issues:**
- Delete `jtcard.db` to reset database
- Check SQLite installation
- Verify write permissions in project directory

## 📞 Support

For technical support or questions:
- Check the troubleshooting section above
- Review the API documentation
- Examine browser console for errors
- Check server logs for backend issues

## 🔄 Updates & Maintenance

### Regular Maintenance
- Monitor disk space for uploads
- Review analytics data
- Update dependencies regularly
- Backup database periodically

### Database Backup
```bash
# Backup database
cp jtcard.db jtcard_backup_$(date +%Y%m%d).db

# Restore database
cp jtcard_backup_YYYYMMDD.db jtcard.db
```

## 📈 Performance Optimization

### Frontend Optimization
- Images are optimized for web
- CSS/JS minification ready
- CDN integration for fonts/icons
- Responsive image loading

### Backend Optimization
- Database indexing implemented
- File upload size limits
- Session management
- Query optimization

## 🎉 Congratulations!

You now have a fully functional, professional digital business card platform with:
- Complete user management
- Advanced card editor
- Photo upload capabilities
- Social media integration
- Analytics tracking
- Professional design
- Mobile responsiveness
- Production-ready architecture

Enjoy building amazing digital business cards! 🚀
