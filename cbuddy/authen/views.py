from django.shortcuts import render, HttpResponse, redirect, reverse
from django.shortcuts import reverse
from .forms import *
from .auth_functions import login as auth_login
from .auth_functions import getUserInfo as auth_user_data
import global_vars

# Create your views here.

def login(request):
    if global_vars.get_and_set_login(request):
        return redirect(reverse('dashboard:home', args=[global_vars.user, global_vars.role]))

    is_correct = False
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            if global_vars.graph:
                is_correct = auth_login(data['username'], data['password'])
            if is_correct:
                user_data = auth_user_data(data['username'])
                global_vars.user, global_vars.role = user_data
                state = global_vars.users['logs'][global_vars.users['name'] == data['username']].iloc[0]
                global_vars.users['ips'][global_vars.users['name'] == data['username']] = request.META['REMOTE_ADDR']
                global_vars.users['logs'][global_vars.users['name'] == data['username']] = not(state)
                print(user_data)
                return redirect(reverse('dashboard:home', args=[*user_data]))
    form = LoginForm()
    return render(request, 'authen/login.html', context={'form':form})


def logout(request):
    global_vars.users['logs'][global_vars.users['ips'] == request.META['REMOTE_ADDR']] = False
    global_vars.users['ips'][global_vars.users['ips'] == request.META['REMOTE_ADDR']] = '0.0.0.0'
    global_vars.loggedIn = False
    return redirect('authen:login')
    # return render(request, 'base/sidebar.html')