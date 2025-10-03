from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import os
import csv
import json
import pandas as pd
from .chatbot import get_gemini_response
from .scrape import scrape_and_save
from django.db.models import Count
from django.db.models.functions import TruncDate
from users.models import ChatHistory
from .models import WishlistItem
from datetime import datetime

def first(request):
    """
    Render the first page with a welcome message.
    """
    return render(request, 'index.html')

def index(request):
    """
    Render the home page with job data scraped from the target website.
    """
    # Scrape and save the latest data to CSV (if not already present or always refresh)
    csv_file = os.path.join(os.path.dirname(__file__), "freejobalert_latest_notifications.csv")
    if not os.path.exists(csv_file):
        jobs = scrape_and_save(csv_file)
    else:
        jobs = []
        with open(csv_file, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                jobs.append(row)

    # Normalize keys so templates and links can reliably access values
    # Adds friendly aliases without altering original keys from CSV
    for job in jobs:
        # Common aliases
        if 'Post Date' in job and 'Post_Date' not in job:
            job['Post_Date'] = job.get('Post Date', '')
        if 'Recruitment Board' in job and 'Name' not in job:
            # Treat recruitment board as organization/bank name
            job['Name'] = job.get('Recruitment Board', '')
        if 'Exam / Post Name' in job and 'Post' not in job:
            # Treat exam/post name as job title/description
            job['Post'] = job.get('Exam / Post Name', '')
        # Explicit fields requested by user
        if 'Recruitment Board' in job and 'Bank' not in job:
            job['Bank'] = job.get('Recruitment Board', '')
        if 'Exam / Post Name' in job and 'Job_Description' not in job:
            job['Job_Description'] = job.get('Exam / Post Name', '')

    # Build Qualification options dynamically from CSV
    qualification_set = set()
    for job in jobs:
        raw = str(job.get("Qualification", "")).strip()
        if not raw:
            continue
        # Split on commas and normalize spacing/case
        parts = [p.strip() for p in raw.split(',') if p.strip()]
        for p in parts:
            qualification_set.add(p)
    qualifications = sorted(qualification_set)

    # Extract unique companies from the "Name" column
    companies = sorted({job.get("Name", "").strip() for job in jobs if job.get("Name", "").strip()})

    # Filtering based on GET params
    qualification = request.GET.get("qualification", "")
    company = request.GET.get("company", "")
    if qualification:
        jobs = [job for job in jobs if qualification.lower() in str(job.get("Qualification", "")).lower()]
    if company:
        jobs = [job for job in jobs if company == job.get("Name", "")]

    # Get user's wishlist items and build signatures for quick template checks
    wishlist_signatures = []
    if request.user.is_authenticated:
        try:
            wishlist_qs = WishlistItem.objects.filter(user=request.user)
            for item in wishlist_qs:
                details = item.job_details or {}
                sig = f"{details.get('Name','')}|{details.get('Post','')}|{details.get('Qualification','')}|{details.get('Last Date','')}|{details.get('Advt No','')}"
                wishlist_signatures.append(sig)
        except Exception:
            wishlist_signatures = []

    context = {
        "jobs": jobs,
        "qualifications": qualifications,
        "companies": companies,
        "selected_qualification": qualification,
        "selected_company": company,
        "wishlist_signatures": wishlist_signatures,
    }
    return render(request, 'home.html', context)

def chatbot(request):
    initial_message = ''
    
    # Check if we're coming from the Get Details button
    if request.GET.get('job_details') == 'true':
        # Construct the job details message
        job_details = {
            'Post Date': request.GET.get('post_date', ''),
            'Name': request.GET.get('name', ''),
            'Post': request.GET.get('post', ''),
            'Bank': request.GET.get('bank', ''),
            'Job Description': request.GET.get('job_description', ''),
            'Qualification': request.GET.get('qualification', ''),
            'Last Date': request.GET.get('last_date', ''),
            'Advt No': request.GET.get('advt_no', '')
        }
        
        # Filter out empty values
        job_details = {k: v for k, v in job_details.items() if v}
        
        if job_details:
            # Create a formatted message for the chatbot
            initial_message = "Roadmap for:\n\n" + \
                            "\n".join([f"\n{k}: {v}" for k, v in job_details.items()])

    if request.method == "POST":
        message = request.POST.get('message', '')
        response = get_gemini_response(message)
        
        if request.user.is_authenticated:
            ChatHistory.objects.create(
                user=request.user,
                query=message,
                response=response,
                job_details=job_details if 'job_details' in locals() else ''
            )
            
        return JsonResponse({'response': response})
    
    return render(request, 'chatbot.html', {'initial_message': initial_message})

@login_required
def dashboard(request):
    """
    Render the dashboard with job data from CSV
    """
    csv_file = os.path.join(os.path.dirname(__file__), "freejobalert_latest_notifications.csv")
    
    try:
        # Read CSV file into a pandas DataFrame
        df = pd.read_csv(csv_file)
        
        # Basic statistics
        total_jobs = len(df)
        
        # Jobs by date - handle different date formats
        df['Post Date'] = pd.to_datetime(df['Post Date'], errors='coerce', dayfirst=True)
        # Remove rows with invalid dates
        df = df.dropna(subset=['Post Date'])
        jobs_by_date = df['Post Date'].value_counts().sort_index()
        # Convert Timestamp keys to strings
        jobs_by_date = {str(k.date()): int(v) for k, v in jobs_by_date.items()}
        
        # Qualification distribution
        qualification_distribution = df['Qualification'].value_counts().to_dict()
        
        # Prepare data for charts
        data = {
            'total_jobs': total_jobs,
            'jobs_by_date': json.dumps(jobs_by_date, indent=2, sort_keys=True, default=str),
            'qualification_distribution': json.dumps(qualification_distribution, indent=2, sort_keys=True, default=str),
        }
        
        return render(request, 'dashboard.html', {'data': data})
    
    except Exception as e:
        return render(request, 'dashboard.html', {'error': str(e)})

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import WishlistItem
from django.db import IntegrityError
import traceback

@csrf_exempt
def toggle_wishlist(request):
    if request.method == 'POST' and request.user.is_authenticated:
        job_details_str = request.POST.get('job_details')

        if not job_details_str:
            return JsonResponse({'status': 'error', 'message': 'Job details missing'})

        try:
            job_details = json.loads(job_details_str)
        except json.JSONDecodeError as e:
            return JsonResponse({'status': 'error', 'message': 'Invalid job details format'})

        # Check if the item is already in the wishlist (backend-agnostic)
        # Some DB backends (e.g., SQLite) may not support JSON containment reliably.
        # Fallback to manual comparison with a normalized JSON string.
        try:
            def _normalize(obj):
                return json.dumps(obj, sort_keys=True, ensure_ascii=False)

            target_sig = _normalize(job_details)
            existing_item = None
            for item in WishlistItem.objects.filter(user=request.user):
                if _normalize(item.job_details) == target_sig:
                    existing_item = item
                    break
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': 'Error checking wishlist'})

        if existing_item:
            # Remove from wishlist
            try:
                existing_item.delete()
                return JsonResponse({'status': 'removed', 'message': 'Removed from wishlist'})
            except Exception as e:
                return JsonResponse({'status': 'error', 'message': 'Error removing from wishlist'})
        else:
            # Add to wishlist
            try:
                WishlistItem.objects.create(user=request.user, job_details=job_details)
                return JsonResponse({'status': 'added', 'message': 'Added to wishlist'})
            except IntegrityError as e:
                return JsonResponse({'status': 'error', 'message': 'Item already exists in wishlist'})
            except Exception as e:
                return JsonResponse({'status': 'error', 'message': 'Error adding to wishlist'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request'})

