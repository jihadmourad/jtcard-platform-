#!/bin/bash

# JTCard Platform - Railway Deployment Setup Script
# This script prepares your project for Railway deployment

echo "🚀 Setting up JTCard Platform for Railway deployment..."

# Create railway.json configuration
cat > railway.json << EOF
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "python app.py",
    "healthcheckPath": "/api/health"
  }
}
EOF

# Create .env file for environment variables
cat > .env << EOF
FLASK_ENV=production
SECRET_KEY=your-secret-key-change-this-in-production
DATABASE_URL=sqlite:///jtcard.db
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=16777216
EOF

# Update app.py for production deployment
cat >> app.py << 'EOF'

# Production configuration for Railway
if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_ENV') != 'production'
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
EOF

# Create .gitignore if it doesn't exist
if [ ! -f .gitignore ]; then
cat > .gitignore << EOF
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.venv/
pip-log.txt
pip-delete-this-directory.txt
.tox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.log
.git
.mypy_cache
.pytest_cache
.hypothesis
.DS_Store
*.sqlite3
*.db
uploads/profiles/*
uploads/covers/*
!uploads/profiles/.gitkeep
!uploads/covers/.gitkeep
EOF
fi

# Create .gitkeep files for upload directories
mkdir -p uploads/profiles uploads/covers
touch uploads/profiles/.gitkeep
touch uploads/covers/.gitkeep

echo "✅ Railway setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Initialize git repository: git init"
echo "2. Add files: git add ."
echo "3. Commit: git commit -m 'Initial commit'"
echo "4. Push to GitHub: git remote add origin YOUR_GITHUB_URL && git push -u origin main"
echo "5. Go to railway.app and deploy from GitHub"
echo ""
echo "🔧 Don't forget to:"
echo "- Change SECRET_KEY in Railway environment variables"
echo "- Set FLASK_ENV=production in Railway"
echo "- Configure custom domain if needed"
echo ""
echo "🎉 Your JTCard platform will be live on Railway!"
