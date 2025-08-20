#!/bin/bash

# Django Trading Platform - PythonAnywhere Deployment Script
# Usage: bash deploy.sh

echo "🚀 Starting Django Trading Platform Deployment..."

# Check if we're in the right directory
if [ ! -f "manage.py" ]; then
    echo "❌ Error: manage.py not found. Please run this script from the project root."
    exit 1
fi

# Step 1: Create requirements.txt if it doesn't exist
if [ ! -f "requirements.txt" ]; then
    echo "📦 Creating requirements.txt..."
    pip freeze > requirements.txt
fi

# Step 2: Initialize git if not already done
if [ ! -d ".git" ]; then
    echo "🔧 Initializing git repository..."
    git init
    git add .
    git commit -m "Initial commit - Django trading platform"
fi

# Step 3: Check if remote exists
if ! git remote get-url origin > /dev/null 2>&1; then
    echo "⚠️  No remote repository configured."
    echo "Please run these commands manually:"
    echo "git remote add origin https://github.com/YOUR_USERNAME/capital-trading-backend-django.git"
    echo "git branch -M main"
    echo "git push -u origin main"
else
    echo "📤 Pushing to GitHub..."
    git add .
    git commit -m "Update for deployment"
    git push origin main
fi

echo "✅ Local deployment preparation complete!"
echo ""
echo "📋 Next steps:"
echo "1. Create a PythonAnywhere account at https://www.pythonanywhere.com"
echo "2. Open a bash console on PythonAnywhere"
echo "3. Run these commands:"
echo ""
echo "cd ~"
echo "git clone https://github.com/YOUR_USERNAME/capital-trading-backend-django.git"
echo "cd capital-trading-backend-django"
echo "python3 -m venv venv"
echo "source venv/bin/activate"
echo "pip install -r requirements.txt"
echo ""
echo "4. Follow the detailed instructions in DEPLOYMENT_GUIDE.md"
echo ""
echo "🌐 Your API will be available at: https://yourusername.pythonanywhere.com"
