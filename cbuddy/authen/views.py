from django.shortcuts import render, HttpResponse
from .forms import *
from .auth_functions import login as auth_login
from global_vars import graph

# Create your views here.

def login(request):
    is_correct = False
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            if graph:
                is_correct = auth_login(data['username'], data['password'])
            if is_correct:
                return HttpResponse('Hello World')
    form = LoginForm()
    return render(request, 'authen/login.html', context={'form':form})


def logout(request):
    pass