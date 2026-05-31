from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import UserProfile
from notifications.email import send_welcome_email


# SIGNUP
def signup_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        email = request.POST.get('email', '')
        role = request.POST.get('role', 'student')

        if User.objects.filter(username=username).exists():
            return render(request, 'signup.html', {'error': 'Username already exists'})

        user = User.objects.create_user(
            username=username,
            password=password,
            email=email,
        )

        # Create user profile with role
        UserProfile.objects.create(user=user, role=role)

        # Send welcome email
        if email:
            send_welcome_email(user)

        return redirect('/login/')

    return render(request, 'signup.html')


# LOGIN
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(
            request,
            username=username,
            password=password,
        )

        if user:
            login(request, user)
            # Role-based redirect
            try:
                role = user.profile.role
            except UserProfile.DoesNotExist:
                role = 'student'

            if role == 'admin':
                return redirect('/dashboards/admin/')
            elif role == 'teacher':
                return redirect('/dashboards/teacher/')
            else:
                return redirect('/dashboards/student/')

    return render(request, 'login.html')


# LOGOUT
def logout_view(request):
    logout(request)
    return redirect('/login/')


# PROFILE
@login_required
def profile_view(request):
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)

    context = {
        'profile': profile,
    }
    return render(request, 'profile.html', context)


@login_required
def profile_edit_view(request):
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)

    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.save()

        profile.phone = request.POST.get('phone', profile.phone or '')
        profile.bio = request.POST.get('bio', profile.bio or '')
        profile.department = request.POST.get('department', profile.department or '')

        if 'avatar' in request.FILES:
            profile.avatar = request.FILES['avatar']

        profile.save()
        return redirect('profile')

    context = {
        'profile': profile,
    }
    return render(request, 'profile_edit.html', context)