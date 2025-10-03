from django.shortcuts import render, redirect, get_object_or_404 # type: ignore
from django.contrib.auth import authenticate, login, logout # type: ignore
from django.contrib import messages # type: ignore
from django.contrib.auth.forms import UserCreationForm # type: ignore
from .forms import RegisterUserForm, ProfileUpdateForm, UserUpdateForm
from django.contrib.auth.decorators import login_required  # type: ignore
from django.http import JsonResponse
from .models import ChatHistory
from home.models import WishlistItem  # Import the WishlistItem model
from .models import UserOTP
from datetime import timedelta
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
import random
import json
import os

# Optional Firebase Admin for email-link verification
try:
import firebase_admin
from firebase_admin import credentials, auth as fb_auth
import json
import os
    if not firebase_admin._apps:
        # Try environment variable first (for Render)
        service_account_json = os.environ.get('FIREBASE_SERVICE_ACCOUNT_JSON')
        if service_account_json:
            try:
                service_account_info = json.loads(service_account_json)
                cred = credentials.Certificate(service_account_info)
                firebase_admin.initialize_app(cred)
            except (json.JSONDecodeError, ValueError):
                pass
        
        # Fallback to file path (for local development)
        if not firebase_admin._apps:
            cred_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
            if cred_path and os.path.exists(cred_path):
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred)
except Exception:
    firebase_admin = None

# Create your views here.

def loginUser(request):
    if request.method=="POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username = username, password = password)
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            messages.success(request, ("There was an error logging in."))
            return redirect('login')
    else:
        return render(request, 'userPages/login.html', {})
    
def logoutUser(request):
    logout(request)
    messages.success(request, ("Logged out successfully."))
    return redirect('index')

def registerUser(request):
    if request.method == "POST":
        print("POST request received for registration")
        form = RegisterUserForm(request.POST)
        print(f"Form is valid: {form.is_valid()}")
        if not form.is_valid():
            print(f"Form errors: {form.errors}")
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(username = username, password = password)
            # Email OTP: deactivate until verified
            user.is_active = False
            user.save()

            # Generate and email OTP
            code = f"{random.randint(100000, 999999)}"
            expires = timezone.now() + timedelta(minutes=10)
            UserOTP.objects.filter(user=user, purpose="signup").delete()
            UserOTP.objects.create(user=user, code=code, purpose="signup", expires_at=expires)
            try:
                send_mail(
                    subject="Your verification code",
                    message=f"Your OTP is {code}. It expires in 10 minutes.",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=False,
                )
            except Exception as e:
                messages.error(request, "Could not send OTP email. Please try again.")
                return redirect('register')

            # Option A: Django OTP flow (kept) — or Firebase email link flow (auto-send page)
            request.session['otp_user_id'] = user.id
            request.session['pending_email'] = user.email
            # Redirect to Firebase start page to send email link automatically (preferred)
            return redirect('firebase_start_verify')
    else:
        form = RegisterUserForm()

    return render(request, 'userPages/register.html' ,{'form':form})


def verify_otp(request):
    user_id = request.session.get('otp_user_id')
    if not user_id:
        messages.error(request, "Session expired. Please register/login again.")
        return redirect('register')

    if request.method == 'POST':
        code = request.POST.get('code', '').strip()
        try:
            otp = UserOTP.objects.filter(user_id=user_id, purpose='signup').latest('created_at')
        except UserOTP.DoesNotExist:
            messages.error(request, "No OTP found. Please resend.")
            return redirect('verify_otp')

        if not otp.is_valid:
            messages.error(request, "OTP expired or too many attempts. Please resend.")
            return redirect('verify_otp')

        if otp.code == code:
            user = otp.user
            user.is_active = True
            user.save()
            UserOTP.objects.filter(user=user, purpose='signup').delete()
            # Login and cleanup
            login(request, user)
            request.session.pop('otp_user_id', None)
            messages.success(request, "Email verified. You are now logged in.")
            return redirect('index')
        else:
            otp.attempts += 1
            otp.save()
            messages.error(request, "Invalid OTP. Please try again.")
            return redirect('verify_otp')

    return render(request, 'userPages/verify_otp.html')


def resend_otp(request):
    user_id = request.session.get('otp_user_id')
    if not user_id:
        messages.error(request, "Session expired. Please register/login again.")
        return redirect('register')
    user = get_object_or_404(User, pk=user_id)
    # Rate limit: allow resend after 60 seconds (optional)
    code = f"{random.randint(100000, 999999)}"
    expires = timezone.now() + timedelta(minutes=10)
    UserOTP.objects.filter(user=user, purpose="signup").delete()
    UserOTP.objects.create(user=user, code=code, purpose="signup", expires_at=expires)
    try:
        send_mail(
            subject="Your verification code",
            message=f"Your OTP is {code}. It expires in 10 minutes.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        messages.success(request, "OTP resent. Check your email.")
    except Exception:
        messages.error(request, "Could not resend OTP. Please try again.")
    return redirect('verify_otp')

@login_required
def showProfile(request):
    u_form = UserUpdateForm(instance=request.user)
    p_form = ProfileUpdateForm(instance=request.user.profile)
    
    if request.method == "POST":
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, ("Profile updated successfully."))
            return redirect('yourProfile')
    
    chat_history = ChatHistory.objects.filter(user=request.user)
    wishlist_items = WishlistItem.objects.filter(user=request.user)  # Get wishlist items
    
    context = {
        'u_form': u_form,
        'p_form': p_form,
        'chat_history': chat_history,
        'wishlist_items': wishlist_items,  # Add wishlist items to context
    }
    
    return render(request, 'userPages/yourProfile.html', context)


def firebase_verify_email_page(request):
    # Render a page that finalizes Firebase email verification on the client
    return render(request, 'userPages/verify_email.html', { 'firebase_config': settings.FIREBASE_CONFIG })


def firebase_start_verify(request):
    # Page that initializes Firebase and triggers sendEmailVerification for the current (matching) email
    email = request.session.get('pending_email') or getattr(request.user, 'email', '')
    return render(
        request,
        'userPages/start_verify.html',
        { 'firebase_config': settings.FIREBASE_CONFIG, 'email': email }
    )


def firebase_email_verified(request):
    if request.method != 'POST':
        return JsonResponse({'ok': False, 'error': 'invalid method'}, status=405)
    try:
        if firebase_admin is None:
            return JsonResponse({'ok': False, 'error': 'firebase not configured'}, status=500)
        data = json.loads(request.body.decode())
        id_token = data.get('idToken')
        decoded = fb_auth.verify_id_token(id_token)
        email = decoded.get('email')
        email_verified = decoded.get('email_verified', False)
        if not (email and email_verified):
            return JsonResponse({'ok': False, 'error': 'unverified'}, status=400)

        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.filter(email=email).first()
        if not user:
            return JsonResponse({'ok': False, 'error': 'user not found'}, status=404)

        user.is_active = True
        user.save()
        login(request, user)
        return JsonResponse({'ok': True})
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)}, status=400)

