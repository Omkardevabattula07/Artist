from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth import authenticate, login,logout
from django_ratelimit.decorators import ratelimit
from django.http import HttpResponseForbidden
from .models import Profile,Room,Message
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

@ratelimit(key='ip', rate='5/m', method='GET', block=True)
def base_art(request):
    if getattr(request, 'limited', False):
        return HttpResponseForbidden("Too many requests. Please try again after a minute.")
    return render(request, 'base_artist.html')


@ratelimit(key='ip', rate='5/m', method='GET', block=True)
def log_reg_art(request):
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == "register":
            username = request.POST.get("username")
            password = request.POST.get("password")
            confirm = request.POST.get("confirm")
            security = request.POST.get("security")
            bio = request.POST.get("bio")
            pic = request.FILES.get("pic")

            if password != confirm:
                messages.error(request, "Passwords do not match")
                return redirect("log_reg_art")

            if User.objects.filter(username=username).exists():
                messages.error(request, "Username already taken")
                return redirect("log_reg_art")
            
            if len(password) < 10:
                messages.error(request, "Password must be at least 10 characters long.")
                return redirect( 'log_reg_art')
            if not any(c.isupper() for c in password):
                messages.error(request, "Password must contain at least one lowercase letter.")
                return redirect( 'log_reg_art')           
            if not any(c.islower() for c in password):
                messages.error(request, "Password must contain at least one lowercase letter.")
                return redirect( 'log_reg_art')

            if not any(c.isdigit() for c in password):
                messages.error(request, "Password must contain at least one number.")
                return redirect( 'log_reg_art')

            # ✅ Create Profile manually
            user = User.objects.create_user(username=username, password=password)
            Profile.objects.create(user=user, bio=bio, security_question=security, pic=pic)
            messages.success(request, "Registered successfully! Wait for admin approval.")
            return redirect("log_reg_art")

        elif action == 'login':
            username = request.POST.get('login_username')
            password = request.POST.get('login_password')
            security = request.POST.get('login_security')

            user = authenticate(username=username, password=password)
            if user:
                if user.is_superuser:
                    login(request, user)
                    return redirect('superuser_art')
                else:
                    profile = user.profile
                    if not profile.is_approved:
                        messages.error(request, "Account not approved by admin.")
                        return redirect('log_reg_art')
                    if profile.security_question != security:
                        messages.error(request, "Incorrect security answer.")
                        return redirect('log_reg_art')
                    login(request, user)
                    return redirect('user_art')
            else:
                messages.error(request, "Invalid login credentials.")
                return redirect('log_reg_art')

    return render(request, 'log_reg_artist.html')

@login_required
def superuser_art(request):
    if not request.user.is_superuser:
        return redirect('log_reg_art')

    # Pending and Approved Users
    pending_users = Profile.objects.filter(is_approved=False)
    approved_users = Profile.objects.filter(is_approved=True)

    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        action = request.POST.get('action')
        user_profile = get_object_or_404(Profile, user_id=user_id)

        if action == 'approve':
            user_profile.is_approved = True
            user_profile.save()
            messages.success(request, f"User '{user_profile.user.username}' approved.")
        elif action == 'delete':
            user_profile.user.delete()
            messages.success(request, f"User '{user_profile.user.username}' deleted.")

        return redirect('superuser_art')

    return render(request, 'superuser_artist.html', {
        'pending_users': pending_users,
        'approved_users': approved_users,
    })


@login_required
def user_art(request):
    if request.user.is_superuser:
        return redirect('superuser_art')

# View for the user page.Displays all approved users except the superuser.
# Fetch all approved users excluding the superuser
    approved_users = Profile.objects.filter(is_approved=True).exclude(user__is_superuser=True)
    
    context = {
        'approved_users': approved_users,
    }
    return render(request, 'user_artist.html', context)
@login_required
def logout_art(request):
# Logs out the user and redirects to the login page.

    logout(request)
    return redirect('log_reg_art') 


@login_required
def chat_art(request, username):
    try:
        other_user = User.objects.get(username=username)
    except User.DoesNotExist:
        return redirect('user_list')

    room_name = Room.get_room_name(request.user, other_user)
    room, created = Room.objects.get_or_create(name=room_name)
    room.participants.add(request.user, other_user)

    messages = Message.objects.filter(room=room).order_by('timestamp')
    return render(request, 'chat_artist.html', {
        'room_name': room_name,
        'messages': messages,
        'other_user': other_user,
    })
