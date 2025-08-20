# 🚀 Django Deployment Guide - PythonAnywhere

This guide will help you deploy your Django application to PythonAnywhere using GitHub.

## 📋 Prerequisites

1. **GitHub Account** - To host your code
2. **PythonAnywhere Account** - Free tier is sufficient
3. **Git installed** on your local machine

## 🔧 Step 1: Prepare Your Local Project

### 1.1 Update Settings for Production

Edit `core/settings_production.py` and replace:
- `yourusername.pythonanywhere.com` with your actual PythonAnywhere domain
- Update CORS settings if needed

### 1.2 Create Requirements File

```bash
pip freeze > requirements.txt
```

### 1.3 Initialize Git Repository

```bash
git init
git add .
git commit -m "Initial commit - Django trading platform"
```

## 🔗 Step 2: Push to GitHub

### 2.1 Create GitHub Repository

1. Go to [GitHub.com](https://github.com)
2. Click "New repository"
3. Name it: `capital-trading-backend-django`
4. Make it **Public** (for free tier)
5. Don't initialize with README

### 2.2 Push Your Code

```bash
git remote add origin https://github.com/YOUR_USERNAME/capital-trading-backend-django.git
git branch -M main
git push -u origin main
```

## 🌐 Step 3: PythonAnywhere Setup

### 3.1 Create PythonAnywhere Account

1. Go to [PythonAnywhere.com](https://www.pythonanywhere.com)
2. Sign up for a free account
3. Note your username (e.g., `yourusername`)

### 3.2 Open Bash Console

1. Log into PythonAnywhere
2. Go to "Consoles" tab
3. Click "Bash" to open a new console

## 📥 Step 4: Clone and Setup Project

### 4.1 Clone Repository

```bash
cd ~
git clone https://github.com/YOUR_USERNAME/capital-trading-backend-django.git
cd capital-trading-backend-django
```

### 4.2 Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 4.3 Install Dependencies

```bash
pip install -r requirements.txt
```

### 4.4 Update Settings

```bash
# Edit the production settings file
nano core/settings_production.py
```

Replace `yourusername.pythonanywhere.com` with your actual domain.

### 4.5 Run Migrations

```bash
python manage.py migrate --settings=core.settings_production
```

### 4.6 Create Superuser

```bash
python manage.py createsuperuser --settings=core.settings_production
```

### 4.7 Collect Static Files

```bash
python manage.py collectstatic --settings=core.settings_production
```

## ⚙️ Step 5: Configure Web App

### 5.1 Create Web App

1. Go to "Web" tab in PythonAnywhere
2. Click "Add a new web app"
3. Choose "Manual configuration"
4. Select Python version (3.9 or higher)

### 5.2 Configure WSGI File

1. Click on the WSGI configuration file link
2. Replace the content with:

```python
import os
import sys

# Add your project directory to the sys.path
path = '/home/yourusername/capital-trading-backend-django'
if path not in sys.path:
    sys.path.append(path)

# Set environment variable for Django settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'core.settings_production'

# Serve Django application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

**Important**: Replace `yourusername` with your actual PythonAnywhere username.

### 5.3 Configure Virtual Environment

1. Go to "Web" tab
2. In "Virtual environment" section, enter:
   ```
   /home/yourusername/capital-trading-backend-django/venv
   ```

### 5.4 Configure Static Files

1. In "Static files" section, add:
   - URL: `/static/`
   - Directory: `/home/yourusername/capital-trading-backend-django/staticfiles`

2. Add media files:
   - URL: `/media/`
   - Directory: `/home/yourusername/capital-trading-backend-django/media`

### 5.5 Reload Web App

Click the "Reload" button to apply changes.

## 🗄️ Step 6: Setup Database

### 6.1 Create Sample Data

```bash
# In the bash console
cd ~/capital-trading-backend-django
source venv/bin/activate

# Create sample products
python manage.py create_sample_products --settings=core.settings_production

# Create sample users (if needed)
python manage.py create_user --settings=core.settings_production
```

## 🔍 Step 7: Test Your Application

### 7.1 Test API Endpoints

Your API will be available at:
- **Base URL**: `https://yourusername.pythonanywhere.com`
- **Admin**: `https://yourusername.pythonanywhere.com/admin/`
- **API Docs**: `https://yourusername.pythonanywhere.com/api/docs/`
- **Products**: `https://yourusername.pythonanywhere.com/products/`
- **Categories**: `https://yourusername.pythonanywhere.com/categories/`
- **Users**: `https://yourusername.pythonanywhere.com/users/`

### 7.2 Test with cURL

```bash
# Test categories endpoint
curl https://yourusername.pythonanywhere.com/categories/

# Test products endpoint
curl https://yourusername.pythonanywhere.com/products/

# Test suppliers endpoint
curl https://yourusername.pythonanywhere.com/users/suppliers/
```

## 🔄 Step 8: Update Deployment

### 8.1 Pull Latest Changes

When you make changes locally:

```bash
# Local machine
git add .
git commit -m "Update description"
git push origin main

# PythonAnywhere bash console
cd ~/capital-trading-backend-django
git pull origin main
source venv/bin/activate
python manage.py migrate --settings=core.settings_production
python manage.py collectstatic --settings=core.settings_production
```

### 8.2 Reload Web App

Go to "Web" tab and click "Reload".

## 🛠️ Troubleshooting

### Common Issues:

1. **Import Errors**: Make sure virtual environment is activated
2. **Static Files Not Found**: Check static files configuration
3. **Database Errors**: Run migrations
4. **Permission Errors**: Check file permissions

### Check Logs:

```bash
# View error logs
tail -f /var/log/yourusername.pythonanywhere.com.error.log

# View access logs
tail -f /var/log/yourusername.pythonanywhere.com.access.log
```

## 🔒 Security Notes

1. **Change SECRET_KEY** in production
2. **Use HTTPS** (automatic on PythonAnywhere)
3. **Keep DEBUG=False** in production
4. **Regular backups** of your database

## 📞 Support

- **PythonAnywhere Help**: [help.pythonanywhere.com](https://help.pythonanywhere.com)
- **Django Documentation**: [docs.djangoproject.com](https://docs.djangoproject.com)

---

## 🎉 Congratulations!

Your Django trading platform is now live on PythonAnywhere!

**Your API Base URL**: `https://yourusername.pythonanywhere.com`

**Available Endpoints**:
- `GET /categories/` - All product categories
- `GET /products/` - All products with role-based pricing
- `GET /users/suppliers/` - All supplier users
- `POST /users/` - Register new users
- `POST /auth/login/` - User login
- `GET /admin/` - Django admin interface
