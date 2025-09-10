from django.shortcuts import render, redirect, get_object_or_404 # type: ignore
from django.contrib.auth import authenticate, login, logout # type: ignore
from django.contrib import messages # type: ignore
from django.contrib.auth.forms import UserCreationForm # type: ignore
from .forms import RegisterUserForm, ProfileUpdateForm, UserUpdateForm
from django.contrib.auth.decorators import login_required  # type: ignore
from .models import ChatHistory
from home.models import WishlistItem  # Import the WishlistItem model

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
            login(request, user)
            messages.success(request, ("Registration successful"))
            return redirect('index')
    else:
        form = RegisterUserForm()

    return render(request, 'userPages/register.html' ,{'form':form})

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


