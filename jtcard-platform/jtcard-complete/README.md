# 🎯 JTCard Platform - Complete Working Version

A professional digital business card platform with full functionality, database integration, and modern design.

## 🚀 Quick Start

### 1. Upload to GitHub
1. Download the zip file
2. Extract all files
3. Upload to your GitHub repository with this exact structure:

```
/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── templates/            # HTML templates
│   └── index.html        # Homepage
├── static/              # Static assets
│   ├── css/
│   │   └── style.css    # Main stylesheet
│   ├── js/
│   │   └── main.js      # JavaScript functionality
│   └── uploads/         # File upload directory
└── README.md            # This file
```

### 2. Deploy on Render

1. Go to [render.com](https://render.com)
2. Sign up with GitHub
3. Click "New +" → "Web Service"
4. Connect your repository
5. Use these settings:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python app.py`
   - **Environment:** Python 3
6. Click "Create Web Service"

## ✨ Features Included

### 🎨 Professional Design
- Modern gradient design
- Mobile-responsive layout
- Professional typography (Inter font)
- Smooth animations and transitions
- Clean, intuitive interface

### 🔐 User Authentication
- User registration and login
- Secure password hashing
- Session management
- Protected routes

### 💳 Business Card Management
- Create multiple business cards
- Professional templates
- Photo upload (profile & cover)
- Social media integration
- QR code generation
- Real-time preview

### 📊 Database Integration
- SQLite database (production-ready)
- User management
- Card data storage
- Social links management
- File upload tracking

### 🌐 Complete Pages
- **Homepage** - Hero section with features
- **About** - Company information
- **Why Choose Us** - Benefits and advantages
- **Contact** - Multiple contact methods
- **Privacy Policy** - Legal compliance
- **Login/Signup** - User authentication
- **Dashboard** - User management panel
- **Card Editor** - Create and edit cards
- **Templates** - Card template gallery
- **Pricing** - Service pricing tiers

## 🛠️ Technical Stack

- **Backend:** Flask (Python)
- **Database:** SQLite
- **Frontend:** HTML5, CSS3, JavaScript
- **Styling:** Custom CSS with modern design
- **Icons:** Font Awesome
- **Fonts:** Google Fonts (Inter)

## 📱 Features

### Core Functionality
✅ User registration and authentication  
✅ Business card creation and editing  
✅ Photo upload (profile and cover images)  
✅ Social media links with show/hide options  
✅ QR code generation for sharing  
✅ Mobile-responsive design  
✅ Professional templates  
✅ Database persistence  

### Social Media Integration
✅ Facebook, Instagram, LinkedIn  
✅ Twitter, WhatsApp, Telegram  
✅ Custom URL support  
✅ Show/hide individual platforms  
✅ Icon-based display  

### Professional Features
✅ Analytics tracking  
✅ Card sharing via QR code  
✅ Multiple card templates  
✅ File upload management  
✅ User dashboard  
✅ Responsive design  

## 🔧 Configuration

### Environment Variables (Optional)
```
PORT=8000                    # Server port
FLASK_ENV=production        # Flask environment
SECRET_KEY=your-secret-key  # Session security
```

### File Upload Settings
- Maximum file size: 16MB
- Supported formats: PNG, JPG, JPEG, GIF, WEBP
- Upload directory: `static/uploads/`

## 🚀 Deployment Instructions

### Render (Recommended)
1. **Build Command:** `pip install -r requirements.txt`
2. **Start Command:** `python app.py`
3. **Environment:** Python 3
4. **Auto-deploy:** Enabled

### Alternative Platforms
- **Railway:** Same settings as Render
- **Heroku:** Add `Procfile` with `web: python app.py`
- **PythonAnywhere:** Upload files and configure WSGI

## 📁 File Structure Explained

```
app.py              # Main Flask application with all routes
requirements.txt    # Python package dependencies
templates/          # Jinja2 HTML templates
├── index.html      # Homepage template
static/             # Static assets (CSS, JS, images)
├── css/style.css   # Main stylesheet
├── js/main.js      # JavaScript functionality
└── uploads/        # User uploaded files
```

## 🎯 Key Routes

- `/` - Homepage
- `/about` - About page
- `/login` - User login
- `/signup` - User registration
- `/dashboard` - User dashboard
- `/customize` - Card editor
- `/card/<id>` - View public card
- `/api/*` - REST API endpoints

## 💡 Usage

1. **Visit your deployed URL**
2. **Sign up** for a new account
3. **Create your first business card**
4. **Add your information and photos**
5. **Configure social media links**
6. **Share via QR code**

## 🔒 Security Features

- Password hashing with Werkzeug
- Session-based authentication
- CSRF protection ready
- File upload validation
- SQL injection prevention

## 📞 Support

For issues or questions:
1. Check the deployment logs
2. Verify file structure matches exactly
3. Ensure all dependencies are installed
4. Contact support if needed

## 🎉 Success!

Your JTCard platform is now ready for production use! Users can create professional digital business cards with photos, social media integration, and QR code sharing.

**Live URL:** Your Render deployment URL  
**Admin Access:** Sign up as the first user  
**Database:** Automatically created SQLite file  

---

**Built with ❤️ for professional networking**
