# Quick Deployment to Render.com

## 🚀 One-Click Deployment

Your Django job alert application is ready for deployment to Render.com!

### What's Included

✅ **Production-ready Django settings** (`root/settings_production.py`)  
✅ **Procfile** for Render.com  
✅ **Build script** (`build.sh`)  
✅ **Updated requirements** with production dependencies  
✅ **Environment template** (`env_template.txt`)  
✅ **Deployment helper script** (`deploy.py`)  

### Quick Start

1. **Prepare your app:**
   ```bash
   cd "projet majeur"
   python deploy.py
   ```

2. **Generate a secret key:**
   ```bash
   python deploy.py secret
   ```

3. **Deploy to Render:**
   - Go to [Render.com](https://render.com)
   - Create new Web Service
   - Connect your Git repository
   - Use these settings:
     - **Build Command:** `cd "projet majeur" && ./build.sh`
     - **Start Command:** `cd "projet majeur" && gunicorn root.wsgi:application --bind 0.0.0.0:$PORT`

4. **Set Environment Variables:**
   - `SECRET_KEY` (use the generated key from step 2)
   - `DEBUG=False`
   - `ALLOWED_HOSTS=your-app-name.onrender.com`

### Features

🎯 **Job Alert System** - Scrape and search job postings  
👤 **User Authentication** - Registration and login system  
🤖 **AI Chatbot** - Job assistance (requires Google API key)  
📊 **Dashboard** - Job statistics and visualization  
📱 **Responsive Design** - Works on all devices  

### Need Help?

Check the detailed [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for complete instructions.

### Flask Dashboard

The Flask dashboard can be deployed separately:
- Root Directory: `projet majeur/majorprojet - dashvaord`
- Start Command: `gunicorn app:app --bind 0.0.0.0:$PORT`
