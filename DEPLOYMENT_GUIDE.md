# Deployment Guide for Render.com

This guide will help you deploy your Django job alert application to Render.com.

## Project Structure

Your project contains:
- **Django Application**: Main job alert system with user authentication and chatbot
- **Flask Application**: Dashboard for job data visualization (separate deployment)

## Prerequisites

1. A Render.com account
2. Your project code in a Git repository (GitHub, GitLab, or Bitbucket)

## Deployment Steps

### 1. Prepare Your Repository

Make sure all the production files are committed to your repository:
- `Procfile`
- `requirements.txt` (updated with production dependencies)
- `runtime.txt`
- `build.sh`
- `root/settings_production.py`
- `env_template.txt`

### 2. Create a New Web Service on Render

1. Go to [Render.com](https://render.com) and sign in
2. Click "New +" and select "Web Service"
3. Connect your Git repository
4. Choose the repository containing your Django app

### 3. Configure the Web Service

**Basic Settings:**
- **Name**: Choose a name for your app (e.g., "job-alert-system")
- **Region**: Choose the closest region to your users
- **Branch**: `main` or `master` (depending on your default branch)
- **Root Directory**: Leave empty (or set to `projet majeur` if deploying from root)

**Build & Deploy:**
- **Build Command**: `cd "projet majeur" && ./build.sh`
- **Start Command**: `cd "projet majeur" && gunicorn root.wsgi:application --bind 0.0.0.0:$PORT`

**Environment Variables:**
Add these environment variables in the Render dashboard:

```
SECRET_KEY=your-very-secure-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-app-name.onrender.com
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

### 4. Add PostgreSQL Database (Optional but Recommended)

1. In your Render dashboard, click "New +" and select "PostgreSQL"
2. Choose a name and plan
3. Once created, copy the database URL
4. Add it as an environment variable:
   ```
   DATABASE_URL=postgresql://user:password@host:port/database
   ```

### 5. Deploy

1. Click "Create Web Service"
2. Render will automatically build and deploy your application
3. Monitor the build logs for any issues

## Post-Deployment

### 1. Create Superuser
After deployment, you can create a superuser by running:
```bash
render run --service your-service-name python manage.py createsuperuser --settings=root.settings_production
```

### 2. Access Your Application
Your app will be available at: `https://your-app-name.onrender.com`

## Features Available

- **User Registration/Login**: Users can create accounts and log in
- **Job Scraping**: Automatic job data collection
- **Job Search**: Filter jobs by qualification and name
- **Chatbot**: AI-powered job assistance (if Google API key is configured)
- **Dashboard**: Job statistics and visualization

## Troubleshooting

### Common Issues:

1. **Static Files Not Loading**:
   - Ensure `whitenoise` is in requirements.txt
   - Check that `STATICFILES_STORAGE` is configured in production settings

2. **Database Connection Issues**:
   - Verify `DATABASE_URL` environment variable is set
   - Check that `dj-database-url` is in requirements.txt

3. **Build Failures**:
   - Check build logs in Render dashboard
   - Ensure all dependencies are in requirements.txt
   - Verify Python version in runtime.txt

4. **Permission Denied on build.sh**:
   - The build script should be executable
   - If issues persist, try: `chmod +x build.sh`

## Environment Variables Reference

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `SECRET_KEY` | Django secret key | Yes | - |
| `DEBUG` | Debug mode | Yes | False |
| `ALLOWED_HOSTS` | Allowed hosts (comma-separated) | Yes | - |
| `DATABASE_URL` | Database connection string | No | SQLite |
| `SESSION_COOKIE_SECURE` | Secure session cookies | No | True |
| `CSRF_COOKIE_SECURE` | Secure CSRF cookies | No | True |
| `GOOGLE_API_KEY` | Google AI API key (for chatbot) | No | - |

## Flask Dashboard Deployment (Separate)

If you want to deploy the Flask dashboard separately:

1. Create a new Web Service
2. Set Root Directory to: `projet majeur/majorprojet - dashvaord`
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `gunicorn app:app --bind 0.0.0.0:$PORT`

## Support

If you encounter any issues during deployment, check:
1. Render build logs
2. Application logs
3. Environment variables are correctly set
4. All dependencies are properly installed

For additional help, refer to [Render's documentation](https://render.com/docs).
