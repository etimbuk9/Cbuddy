from django.shortcuts import render, HttpResponse, redirect
from django.shortcuts import reverse
from .forms import *
from .auth_functions import login as auth_login
import global_vars

# Create your views here.

def login(request):
    is_correct = False
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            if global_vars.graph:
                is_correct = auth_login(data['username'], data['password'])
            if is_correct:
                global_vars.loggedIn = is_correct
                return HttpResponse('Hello World <a href="/logout">Log Out</a>')
    form = LoginForm()
    return render(request, 'authen/login.html', context={'form':form})


def logout(request):
    global_vars.loggedIn = False
    return redirect('authen:login')
    # return render(request, 'base/sidebar.html')