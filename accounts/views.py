from django.contrib.auth import logout
from django.shortcuts import redirect, render


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    return render(request, 'accounts/login.html')


def logout_view(request):
    logout(request)
    return redirect('home')
