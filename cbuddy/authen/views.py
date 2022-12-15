from django.shortcuts import render, HttpResponse, redirect, reverse
from django.shortcuts import reverse
from .forms import *
from .auth_functions import login as auth_login
from .auth_functions import getUserInfo as auth_user_data
import global_vars
from .extras import getUserList
from datetime import datetime as dt
import calendar
import os
from cbuddy.settings import BASE_DIR

# Create your views here.

def login(request):
    send_debtors()
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
                # print(user_data)
                return redirect(reverse('dashboard:home', args=[*user_data]))
    form = LoginForm()
    return render(request, 'authen/login.html', context={'form':form})


def logout(request):
    global_vars.users['logs'][global_vars.users['ips'] == request.META['REMOTE_ADDR']] = False
    global_vars.users['ips'][global_vars.users['ips'] == request.META['REMOTE_ADDR']] = '0.0.0.0'
    global_vars.loggedIn = False
    return redirect('authen:login')
    # return render(request, 'base/sidebar.html')


def createNewUser(request):
    if request.method == 'POST':
        form = NewUserForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            add_new_user(
                data['first_name'].lower().strip()+data['surname'].lower().strip(),
                data['position'].upper().strip(),
                data['password'].strip(),
                data['first_name'].lower().strip()+ ' ' + data['surname'].lower().strip(),
                data['staff_number'],
            )
            return redirect('authen:login')
        else:
            print(form.errors)
    form = NewUserForm()
    return render(request, 'authen/newuser.html', context={
        'appuser': global_vars.exportUserInfo(request)[0],
        'role': global_vars.exportUserInfo(request)[1],
        'form':form,
    })



## Utilities
def add_new_user(username, position, password, name, staffid):
    query = 'Merge(n:User{name:"' + username + '"}) SET n.Password = "' + password + '" set n.fullname = "' + name + '" set n.id = "' + staffid + '" set n.active=True MERGE(m:Position{name:"' + position + '"}) MERGE (n)-[:STATUS]->(m)'
    global_vars.graph.evaluate(query)
    global_vars.users = getUserList()

def send_debtors():
    current_date = dt.now()
    maxday = calendar.monthrange(current_date.year, current_date.month)
    sending_date = dt(current_date.year, current_date.month, maxday[-1]-3)
    print(sending_date)

    fullpath = os.path.join(BASE_DIR, 'debts')
    folder = os.listdir(fullpath)
    folder = [str(x).lower() for x in folder]
    # print(folder)
    if current_date.date() == sending_date.date():
        print('we r in')
        filename = 'Debt '+current_date.strftime('%B %Y')+'.xlsx'
        if filename.lower() not in folder:
            generate_debt_file(os.path.join(fullpath,filename))
            global_vars.graph.evaluate('Match(n:Staffvisit{Paid:0}) set n.Paid=1')
    else:
        print('hello')

def generate_debt_file(filename):
    import pandas as p
    data = global_vars.graph.run(
        'match(n:Staffvisit)--(p:Staff) where (n.Paid=0 or n.Paid=false) and n.Collected = true return n.staffname, p.id, n.patient, n.doctor, n.payamt, n.Paid')
    data = data.to_data_frame()
    data = data[['n.staffname', 'p.id', 'n.patient', 'n.doctor', 'n.payamt', 'n.Paid']]
    data1 = data[['n.staffname', 'p.id', 'n.payamt']]
    data2 = data1.groupby(['n.staffname', 'p.id'], as_index=False).sum()
    # print(data2)
    try:
        # filename = filename
        if '.xlsx' in filename:
            fw = p.ExcelWriter(filename)
        else:
            fw = p.ExcelWriter(filename + ".xlsx")
        data2.to_excel(fw)
        fw.save()
    except Exception as err:
        print(err)