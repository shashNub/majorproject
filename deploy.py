#!/usr/bin/env python3
"""
Deployment helper script for Render.com
This script helps prepare the Django application for deployment
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(command, cwd=None):
    """Run a shell command and return the result"""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            cwd=cwd, 
            capture_output=True, 
            text=True, 
            check=True
        )
        print(f"✅ {command}")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running: {command}")
        print(f"Error: {e.stderr}")
        return None

def check_requirements():
    """Check if all required files exist"""
    required_files = [
        'Procfile',
        'requirements.txt',
        'runtime.txt',
        'build.sh',
        'root/settings_production.py',
        'manage.py'
    ]
    
    missing_files = []
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if missing_files:
        print("❌ Missing required files:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    
    print("✅ All required files present")
    return True

def prepare_deployment():
    """Prepare the application for deployment"""
    print("🚀 Preparing Django application for Render.com deployment...")
    
    # Check requirements
    if not check_requirements():
        print("❌ Please ensure all required files are present")
        return False
    
    # Make build script executable
    print("📝 Making build script executable...")
    run_command("chmod +x build.sh")
    
    # Check if we're in a git repository
    if not Path('.git').exists():
        print("⚠️  Warning: Not in a git repository. Please initialize git and commit your changes.")
        print("   Run: git init && git add . && git commit -m 'Initial commit'")
        return False
    
    print("✅ Deployment preparation complete!")
    print("\n📋 Next steps:")
    print("1. Commit all changes to git")
    print("2. Push to GitHub/GitLab/Bitbucket")
    print("3. Create a new Web Service on Render.com")
    print("4. Follow the deployment guide in DEPLOYMENT_GUIDE.md")
    
    return True

def generate_secret_key():
    """Generate a new Django secret key"""
    from django.core.management.utils import get_random_secret_key
    return get_random_secret_key()

if __name__ == "__main__":
    print("🔧 Django Render.com Deployment Helper")
    print("=" * 50)
    
    if len(sys.argv) > 1 and sys.argv[1] == "secret":
        print("🔑 Generated Django secret key:")
        print(generate_secret_key())
    else:
        prepare_deployment()
