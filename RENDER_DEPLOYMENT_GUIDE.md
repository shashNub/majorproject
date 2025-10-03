# Render Deployment Guide - Job Alert System

## 🚀 Quick Deployment Steps

### 1. Prepare Your Repository
Make sure all files are committed to your Git repository:
```bash
git add .
git commit -m "Ready for Render deployment"
git push origin main
```

### 2. Create Render Web Service

1. **Go to [Render.com](https://render.com)** and sign in
2. **Click "New +"** → **"Web Service"**
3. **Connect your Git repository** (GitHub/GitLab/Bitbucket)
4. **Select your repository** containing the Django app

### 3. Configure the Service

**Basic Settings:**
- **Name**: `job-alert-system` (or your preferred name)
- **Region**: Choose closest to your users
- **Branch**: `main`
- **Root Directory**: Leave empty

**Build & Deploy:**
- **Build Command**: `pip install -r requirements.txt && python manage.py collectstatic --noinput --settings=root.settings_production`
- **Start Command**: `gunicorn root.wsgi:application --bind 0.0.0.0:$PORT --settings=root.settings_production`

### 4. Environment Variables

Add these in Render Dashboard → Environment Variables:

#### Required Variables:
```
SECRET_KEY=your-very-secure-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-app-name.onrender.com
DJANGO_SETTINGS_MODULE=root.settings_production
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

#### Firebase Configuration:
```
FIREBASE_API_KEY=your-firebase-api-key
FIREBASE_AUTH_DOMAIN=your-project-id.firebaseapp.com
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_STORAGE_BUCKET=your-project-id.appspot.com
FIREBASE_MESSAGING_SENDER_ID=your-sender-id
FIREBASE_APP_ID=your-app-id
```

#### Site Configuration:
```
SITE_URL=https://your-app-name.onrender.com
```

#### Optional - Email (for notifications):
```
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@yourdomain.com
```

### 5. Firebase Service Account Setup

1. **Download your Firebase service account JSON** from Firebase Console
2. **Upload to Render**: 
   - Go to your Render service
   - Click "Files" tab
   - Upload the JSON file as `firebase-service-account.json`
3. **Set environment variable**:
   ```
   GOOGLE_APPLICATION_CREDENTIALS=/opt/render/project/src/firebase-service-account.json
   ```

### 6. Database Setup (Optional)

**For PostgreSQL:**
1. Create a PostgreSQL database in Render
2. Add the DATABASE_URL environment variable:
   ```
   DATABASE_URL=postgresql://user:password@host:port/database
   ```

**For SQLite (default):**
- No additional setup needed, but data won't persist between deployments

### 7. Deploy

1. **Click "Create Web Service"**
2. **Monitor the build logs** for any issues
3. **Wait for deployment** to complete

### 8. Post-Deployment Setup

**Create Superuser:**
```bash
# In Render Shell or via CLI
python manage.py createsuperuser --settings=root.settings_production
```

**Run Migrations:**
```bash
python manage.py migrate --settings=root.settings_production
```

## 🔧 Troubleshooting

### Common Issues:

1. **Build Fails:**
   - Check that all dependencies are in `requirements.txt`
   - Verify Python version in `runtime.txt`

2. **Static Files Not Loading:**
   - Ensure `whitenoise` is in requirements.txt
   - Check build command includes `collectstatic`

3. **Firebase Errors:**
   - Verify all Firebase environment variables are set
   - Check service account JSON is uploaded correctly

4. **Database Errors:**
   - Ensure DATABASE_URL is set if using PostgreSQL
   - Run migrations after deployment

### Build Logs:
Monitor your deployment in Render Dashboard → Logs tab

## 🌐 Your App URL

After successful deployment, your app will be available at:
`https://your-app-name.onrender.com`

## 📋 Features Available

- ✅ User registration with Firebase email verification
- ✅ Job search and filtering
- ✅ Wishlist functionality
- ✅ AI chatbot integration
- ✅ User profiles and saved jobs
- ✅ Responsive design with Tailwind CSS

## 🔄 Updates

To update your app:
1. Push changes to your Git repository
2. Render will automatically redeploy
3. Monitor logs for any issues

## 📞 Support

If you encounter issues:
1. Check Render build logs
2. Verify all environment variables
3. Ensure Firebase configuration is correct
4. Check Django logs in Render dashboard
