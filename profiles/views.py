from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth import login, logout, authenticate


from .models import Profile
from .forms import RegistrationForm, LoginForm




def home_view(request):
    return render(request, 'homePage.html')



def authenticate_view(request, state=1):
    # Ensure state is an integer (1 for login, 2 for register)
    try:
        state = int(state)
    except ValueError:
        state = 1

    # Create both forms regardless of the state.
    login_form = LoginForm(request.POST or None)
    
    registration_form = RegistrationForm(request.POST or None)

    if(request.method == 'POST'):
        if(state == 1):
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, 'You have successfully login')
                return redirect('tracker:tracker')
            else:
                messages.error(request, "Username or password is not valid")
        elif(state == 2):
            if registration_form.is_valid():
                registration_form.save()
                messages.info(request, "You have been registered successfully")
                return redirect('profile:login', state=2)
            else:
                messages.error(request, "Failed To register please try aging")    
    context = {
        "login_form": login_form,
        "register_form": registration_form,
        "state": state,
    }
    return render(request, "auth/authenticate.html", context)

# @login_required
def the_logout_view(request):
    logout(request)
    messages.warning(request, 'You have successfully logged out')
    return redirect('profile:login', state=1)

def profile_view(request):
    profile = Profile.objects.get(user=request.user)
    context = {
        'profile': profile
    }
    return render(request, 'profiles/profile.html', context)