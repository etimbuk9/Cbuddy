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
from cbuddy.settings import BASE_DIR, MEDIA_ROOT

# Create your views here.

def login(request):
    send_debtors()
    internalDBsync()
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
    # print(sending_date)

    fullpath = os.path.join(BASE_DIR, 'debts')
    folder = os.listdir(fullpath)
    folder = [str(x).lower() for x in folder]
    # print(folder)
    if current_date.date() == sending_date.date():
        # print('we r in')
        filename = 'Debt '+current_date.strftime('%B %Y')+'.xlsx'
        if filename.lower() not in folder:
            generate_debt_file(os.path.join(fullpath,filename))
            global_vars.graph.evaluate('Match(n:Staffvisit{Paid:0}) set n.Paid=1')
    else:
        print('Not in')

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

def syncDBs(filepath):
    import pyodbc
    import pandas as p

    conn_str = (r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=' + filepath + 'PWD=etimbuk12')
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    for table_info in cursor.tables(tableType='TABLE'):
        if table_info.table_name == 'Students':
            name = table_info.table_name
            break

    cursor.execute('SELECT * FROM ' + name)
    data = []
    # graph1 = G("http://localhost:11038/db/data/", password="timbuk2")

    for row in cursor:
        data.append(list(row))

    df1 = p.DataFrame(data,
                      columns=['Reg_No', 'Lastname', 'Firstname', 'Middlename', 'Gender', 'Class', 'Set', 'Not_Present',
                               'Scholarship', 'Tag', 'Applicant'])
    df1['Firstname'][df1['Firstname'].isna()] = " "
    df1['Lastname'][df1['Lastname'].isna()] = " "
    df1['Middlename'][df1['Middlename'].isna()] = " "
    # print(df1[df1['Firstname'].isna()])
    df1['Name'] = df1['Lastname'] + ', ' + df1['Firstname'] + ' ' + df1['Middlename']
    # print(df1[['Name','Reg_No']])
    df1 = df1[df1['Name'].notna()]
    conn.close()
    outs = str(filepath).split('\\')

    print(df1)
    output_path = '/'.join(outs[:-1])

    df1.to_csv(output_path+'/bursary_data.csv')
    # print(output_path)
    # print('hello World')

    df1 = df1[df1['Tag'] == 0]
    #
    dimd = df1.shape
    if dimd[0] > 0:
        df1 = df1.sort_values(by=['Name'], ascending=False)
    nam = df1['Name']
    oi = df1[['Reg_No', 'Set', 'Gender', 'Not_Present']]
    new_list = list(df1['Reg_No'])

    # print(oi)

    graph1 = global_vars.graph
    current_list = graph1.run('match (n:Person) return n.id')
    current_list = current_list.to_data_frame()
    current_list = list(current_list['n.id'])

    import numpy as np
    # print(current_list)
    # print(sorted(new_list))

    diff = np.setdiff1d(new_list, current_list)
    diff1 = []
    print(diff)

    # df1 = df1[df1['Reg_No'].isin(diff)]
    # print(df1)

    res_data = graph1.run('match(n:Person)-[r:MEMBEROF]-(d:Set) return n.id, n.name, d.name, n.gender, n.status').to_data_frame()
    res_data = res_data[['d.name', 'n.gender', 'n.id', 'n.name', 'n.status']]
    # print(res_data)
    burs_data = df1[['Set','Gender','Reg_No','Name','Not_Present']]
    
    # print(burs_data)
    count = 0
    for regno in res_data['n.id']:
        # try:
        #     print(list(burs_data[burs_data['Reg_No']==regno].iloc[0,:]))
        #     print(list(res_data[res_data['n.id']==regno].iloc[0,:]))
        # except:
        #     count+=1
        #     print(regno)
        try:
            if list(res_data[res_data['n.id']==regno].iloc[0,:])==list(burs_data[burs_data['Reg_No']==regno].iloc[0,:]):
                pass
            else:
                # print(list(res_data[res_data['n.id']==regno].iloc[0,:]))
                # print(list(burs_data[burs_data['Reg_No']==regno].iloc[0,:]))
                diff1.append(regno)
        except Exception as e:
            print(e)
    print(len(diff1))
    diff2 = diff.tolist()+ diff1
    print(diff2)
    # if len(diff) != 0:
    #     df1 = df1[df1['Reg_No'].isin()]
    # else:
    #     df2 = df1[df1['Reg_No'].isin(diff1)]
    df1 = burs_data[df1['Reg_No'].isin(diff2)]

    print(df1)
    for regno, name, claz, gender, status in zip(df1['Reg_No'], df1['Name'], df1['Set'], df1['Gender'],
                                                 df1['Not_Present']):
        graph1.evaluate('MATCH (n:Person{id:' + str(regno) + '})-[r:MEMBEROF]-(d) DELETE r')
        graph1.evaluate('Merge (n:Person{id:' + str(
            regno) + '}) SET n.name = "' + name.upper() + '" SET n.gender= "' + gender.upper() + '" set n.status=' + str(
            status) + ' merge(s:Set{name:"' + claz.upper() + '"}) merge (n)-[:MEMBEROF]->(s)')
    # print(count)

def internalDBsync():
    db_path = os.path.join(MEDIA_ROOT, 'topfaith_database_dist_v1_be.accdb')
    db_path += ';'

    log_path = os.path.join(MEDIA_ROOT, 'sync_log.txt')
    if os.path.exists(log_path):
        with open(log_path, 'r+') as file:
            f = file.readlines()
            f = [str(x).strip() for x in f]
            if dt.now().strftime('%Y-%m-%d') not in f:
                syncDBs(db_path)
                file.write(dt.now().strftime('%Y-%m-%d')+'\n')
    else:
        syncDBs(db_path)
        with open(log_path, 'w') as file:
            file.write(dt.now().strftime('%Y-%m-%d')+'\n')