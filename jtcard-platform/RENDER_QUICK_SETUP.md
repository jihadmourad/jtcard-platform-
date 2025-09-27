# JTCard Platform - Quick Render Setup

## 🚀 5-Minute Deployment Guide

### Prerequisites
- Render account (free signup at render.com)
- GitHub account
- The deployment zip file

### Step 1: Upload to GitHub (2 minutes)
1. Create new repository on GitHub
2. Upload all files from `jtcard-complete` folder
3. Commit and push

### Step 2: Create Database (1 minute)
1. Render Dashboard → "New +" → "PostgreSQL"
2. Name: `jtcard-db`
3. Click "Create Database"
4. **Copy the Database URL** (save for Step 4)

### Step 3: Create Web Service (1 minute)
1. Render Dashboard → "New +" → "Web Service"
2. Connect your GitHub repository
3. Settings:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python app.py`

### Step 4: Set Environment Variables (1 minute)
Add these in your web service settings:

```
DATABASE_URL = [paste your PostgreSQL URL from Step 2]
SECRET_KEY = [any random string, e.g., "your-secret-key-here"]
PORT = 10000
```

### Step 5: Deploy & Test
1. Click "Create Web Service"
2. Wait 2-3 minutes for deployment
3. Visit your app URL
4. Test registration and login

## ✅ That's it! Your JTCard platform is live!

### Your app will be available at:
`https://your-app-name.onrender.com`

### Key Features Ready:
- ✅ User registration/login
- ✅ Business card creation
- ✅ 6 professional templates
- ✅ QR code sharing
- ✅ Social media integration
- ✅ Mobile responsive design
- ✅ PostgreSQL database
- ✅ Secure authentication

### Need Help?
Check the full `RENDER_DEPLOYMENT_GUIDE.md` for detailed instructions and troubleshooting.
