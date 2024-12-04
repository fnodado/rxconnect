from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect

from .forms import CustomUserCreationForm, ProfileForm
from .models import Profile


# Create your views here.
def users(request):
    profile_user = request.user
    # profiles = Profile.objects.all()
    print(profile_user)
    return render(request, 'users/account.html')

def user_profile(request, pk):
    print("user profile method")
    profile = Profile.objects.get(id=pk)
    context = {'profile': profile}
    return render(request, 'users/account.html', context)

def login_page(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'Username does not exits')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            #Create session id
            login(request, user)
            print("login user: ", user)
            profile_user = user.profile
            print("profile_user user: ", profile_user.id)
            messages.success(request, "User logged in")
            return redirect('dashboard')
        else:
            messages.error(request, "Username OR Password is incorrect")

    return render(request, 'users/login_register.html')

def logout_user(request):
    logout(request)
    messages.error(request, 'User was logged out!')
    return redirect('login')

def register_user(request):
    page = 'register'
    form = CustomUserCreationForm()

    if request.method == 'POST':
        print("here1")
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            print("here2")
            user = form.save(commit=False)
            print("user: ", user)
            user.username = user.username.lower()
            user.save()

            messages.success(request, 'User account was created!')
            login(request, user)
            print("here4")
            return redirect('edit-account')
        else:
            print("here3")
            messages.error(
                request, 'An error has occurred during registration')

    context = {'page': page, 'form': form}
    return render(request, 'users/login_register.html', context)

@login_required(login_url='login')
def edit_account(request):
    profile = request.user.profile
    form = ProfileForm(instance=profile)

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()

            return redirect('user-profile', pk=request.user.profile.id)


    context = {'form': form}
    return render(request, 'users/profile_form.html', context)
