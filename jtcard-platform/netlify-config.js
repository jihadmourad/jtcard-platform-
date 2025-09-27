// JTCard Platform - Netlify Frontend Configuration
// This file configures the frontend to work with a separate backend

// Backend API Configuration
const API_CONFIG = {
    // Change this to your deployed backend URL
    BASE_URL: 'https://your-backend-app.railway.app/api',
    // Alternative options:
    // BASE_URL: 'https://your-app.onrender.com/api',
    // BASE_URL: 'https://your-app.herokuapp.com/api',
    
    // API Endpoints
    ENDPOINTS: {
        REGISTER: '/register',
        LOGIN: '/login',
        LOGOUT: '/logout',
        CARDS: '/cards',
        UPLOAD: '/upload',
        ANALYTICS: '/analytics',
        HEALTH: '/health'
    }
};

// Update all API calls to use the backend URL
function updateApiCalls() {
    // Replace localhost references in all HTML files
    const files = [
        'login.html',
        'signup.html', 
        'dashboard.html',
        'customize.html',
        'card-preview.html'
    ];
    
    console.log('Update these files to use:', API_CONFIG.BASE_URL);
    console.log('Replace http://localhost:5000/api with your backend URL');
}

// CORS Configuration for Backend
const CORS_CONFIG = {
    // Add your Netlify domain to backend CORS settings
    origins: [
        'https://your-site.netlify.app',
        'https://your-custom-domain.com'
    ]
};

// Netlify Build Configuration
const NETLIFY_CONFIG = {
    build: {
        publish: ".",
        command: "echo 'Static site ready'"
    },
    headers: [
        {
            for: "/*",
            values: {
                "X-Frame-Options": "DENY",
                "X-XSS-Protection": "1; mode=block",
                "X-Content-Type-Options": "nosniff"
            }
        }
    ],
    redirects: [
        {
            from: "/api/*",
            to: "https://your-backend-app.railway.app/api/:splat",
            status: 200,
            force: true
        }
    ]
};

// Instructions for deployment
console.log(`
🌐 NETLIFY DEPLOYMENT INSTRUCTIONS:

1. PREPARE FRONTEND:
   - Copy all .html files to a new 'netlify-frontend' folder
   - Copy assets/ folder to netlify-frontend/
   - Update API URLs in JavaScript code

2. UPDATE API CALLS:
   Replace all instances of:
   'http://localhost:5000/api'
   
   With your backend URL:
   '${API_CONFIG.BASE_URL}'

3. DEPLOY BACKEND FIRST:
   - Deploy Flask app to Railway/Render/Heroku
   - Get your backend URL
   - Update CORS settings to allow your Netlify domain

4. DEPLOY FRONTEND TO NETLIFY:
   - Drag and drop netlify-frontend folder to Netlify
   - Or connect GitHub repository
   - Configure custom domain if needed

5. UPDATE CORS ON BACKEND:
   Add this to your Flask app:
   
   from flask_cors import CORS
   CORS(app, origins=['https://your-site.netlify.app'])

6. TEST DEPLOYMENT:
   - Visit your Netlify site
   - Test login/signup functionality
   - Verify card creation works
   - Check file uploads

🎉 Your JTCard platform will be split across:
   - Frontend: Netlify (Static files)
   - Backend: Railway/Render (API + Database)
`);

export { API_CONFIG, CORS_CONFIG, NETLIFY_CONFIG };
