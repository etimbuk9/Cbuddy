from django.shortcuts import render, redirect, reverse
from .forms import *
import global_vars
from datetime import datetime as dt
from datetime import timedelta as td
import numpy as np
from .models import Student
from authen import extras

# Create your views here.

def visit(request):
    if global_vars.get_and_set_login(request):
        if request.method == 'GET':
            form = StudentSearchForm(request.GET)
            if form.is_valid():
                data = form.cleaned_data
                student_name = str(data['student']).split(' -> ')[0]
                regno = str(data['student']).split(' -> ')[1].split('(')[0].strip()
                student_set = str(data['student']).split(' -> ')[1].split('(')[-1][:-1]

                student_model = Student(student_name,regno,student_set)
                form = VisitForm()
                attributes = extras.getAttributes(regno)
                return render(request, 'medicalvisit/visit.html', context={
                    'appuser': global_vars.exportUserInfo(request)[0],
                    'role': global_vars.exportUserInfo(request)[1],
                    'form':form,
                    'drugs': getDrugs(),
                    'qtys':global_vars.getDrugQtys(),
                    'student':student_model,
                    'atts': attributes,
                    'prev_visits':global_vars.getPreviousVisits(regno)
                })
            else:
                print(form.errors)
    return redirect('authen:login')


def checkStudentPrescription(request):
    end_overdue(7)
    form = StudentSearchForm()
    try:
        idx = list(global_vars.users['name'] == global_vars.exportUserInfo(request)[0]).index(True)
        if len(global_vars.users['inits'].iloc[idx]) != 0:
            form.initial = global_vars.users['inits'].iloc[idx]
            global_vars.users['inits'].iat[idx] = {}
    except:
        return redirect('authen:login')

    print(form)

    if request.method == 'POST':
        form = StudentSearchForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            student_no = data['student'].split(' -> ')[-1]
            student_no = student_no.split('(')[0].strip()
            return render(request, 'medicalvisit/dispenser.html', context={
                'appuser': global_vars.exportUserInfo(request)[0],
                'role': global_vars.exportUserInfo(request)[1],
                'form':form,
                'nos':getStudNos(),
                'cycles': getMedCycles(student_no),
            })

    
    return render(request, 'medicalvisit/dispenser.html', context={
            'appuser': global_vars.exportUserInfo(request)[0],
            'role': global_vars.exportUserInfo(request)[1],
            'form':form,
            'nos':getStudNos(),
            'drugs': getDrugs(),
        })


def newLabVisit(request):
    if request.method == 'GET':
        form = StudentSearchForm(request.GET)
        if form.is_valid():
            data = form.cleaned_data
            student_name = str(data['student']).split(' -> ')[0]
            regno = str(data['student']).split(' -> ')[1].split('(')[0].strip()
            student_set = str(data['student']).split(' -> ')[1].split('(')[-1][:-1]

            student_model = Student(student_name,regno,student_set)
    return render(request, 'medicalvisit/newlabvisit.html', context={
            'student': student_model,
            'appuser': global_vars.exportUserInfo(request)[0],
            'role': global_vars.exportUserInfo(request)[1],
            'elig_visits':getVisits4Labvisit(regno),
            'prev_visits':global_vars.getLabVisits(regno),
        })

def submitLabResult(request, medname):
    if request.method == 'POST':
        data = request.POST
        details = data['labdetails']
        medname = medname[:4] + '/' + medname[5:]
        add_lab_visit(
            medname,
            details,
            dt.now().strftime('%Y-%m-%d'),
            dt.now().strftime('%H:%M'),
            global_vars.exportUserInfo(request)[0],
        )
        
    return redirect('authen:login')

def getPres(request, pname, comp, diag, drugs="", pres=""):
    drugList = list(set([x for x in str(drugs).split("->")]))
    pres = pres.split(',')
    pres1 = [pres[n:n + len(drugList)] for n in range(0, len(pres), len(drugList))]

    pres1 = [[int(x) for x in y] for y in pres1]
    # d1 = dt.strptime(dt.today().strftime('%Y-%m-%d'), '%Y-%m-%d')
    # d2 = dt.today() + td(int(max(pres1[2])))

    prescr, medqry = make_med_query(pname,pres1[0],pres1[1],pres1[2], drugList, request)
    print(prescr, medqry)

    add_visit(pname, comp, diag, dt.now().strftime('%Y-%m-%d'),dt.now().strftime('%H:%M'),global_vars.exportUserInfo(request)[0], prescr, medqry)

    return redirect('authen:login')

def getPresnp(request, pname, comp, diag):
    add_visit(pname, comp, diag, dt.now().strftime('%Y-%m-%d'),dt.now().strftime('%H:%M'),global_vars.exportUserInfo(request)[0])

    return redirect('authen:login')


## Utilities
def add_visit(regno, comp, diag, date1, time, user, pres="", medqry=""):
    if medqry != "":
        query = 'MATCH(n:Person{id:' + regno + '})' + 'MERGE(v:Visit{name:"' + regno + '/' + str(dt.now()) + '"}) ' + 'SET v.Complain = "' + comp + '" ' + 'SET v.Diagnosis = "' + diag + '" ' + 'SET v.Prescription = "' + pres + '" ' + 'SET v.date = "' + date1 + '" ' + 'SET v.time = "' + time + '" SET v.doctor= "' + user +  '" ' + medqry + ' MERGE (n)-[:VISITED]->(v) MERGE (n)-[:CURRENTMEDS]->(m) MERGE (v)<-[:CYCLEFOR]-(m)'
        global_vars.graph.evaluate(query)
        print(query)
    else:
        query = 'MATCH(n:Person{id:' + regno + '})' + 'MERGE(v:Visit{name:"' + regno + '/' + str(dt.now()) + '"}) ' + 'SET v.Complain = "' + comp + '" ' + 'SET v.Diagnosis = "' + diag + '" ' + 'SET v.Prescription = "' + pres + '" ' + 'SET v.date = "' + date1 + '" ' + 'SET v.time = "' + time + '" SET v.doctor= "' + user + '" ' + medqry + ' MERGE (n)-[:VISITED]->(v)'
        global_vars.graph.evaluate(query)

def get_drug_unit(item):
    unit = global_vars.graph.run('match (n:Drug{name:"'+item+'"}) return n.p_unit')
    unit = unit.to_data_frame()
    unit = unit['n.p_unit'][0]
    return unit

def make_med_query(regno, amts, t, n, meds, request):
    st = []
    d1 = dt.strptime(dt.today().strftime('%Y-%m-%d'), '%Y-%m-%d')
    d2 = dt.today() + td(int(max(n)))
    presp = ''
    for a in range(len(meds)):
        presp += meds[a] + ', ' + str(amts[a]) + ' ' + str(get_drug_unit(meds[a])) + ', ' + str(t[a]) + ' time(s) per day, for ' + str(n[a]) + ' day(s)\n'
        states = np.full((int(t[a]), int(n[a])), False)
        dims = states.shape
        g = np.resize(states, [dims[0] * dims[1]])
        g = g.tolist()
        st.append(g)
    st = [j for i in st for j in i]
    #print(st)
    qry = 'merge(m:Medication{name: "' + str(regno) + '/' + d1.strftime(
        '%Y-%m-%d') + '-' + d2.strftime(
        '%Y-%m-%d %H:%M:%S') + '"}) set m.ongoing = 1 set m.finished=0 set m.prescription="' + presp + '" set m.state=' + str(
        st) +' set m.nurses= '+str(st)+' set m.unit='+str(amts)+' set m.times = ' + str(t) + ' set m.days = ' + str(n) + ' set m.startdate = "' + d1.strftime(
        '%Y-%m-%d') + '" set m.meds = "'+str(meds)+'" set m.doctor= "'+str(global_vars.exportUserInfo(request)[0])+'" '
    #print(qry)
    #grav.evaluate(qry)
    return presp, qry

def getVisits4Labvisit(regno):
    d2 = []
    query = 'MATCH(n:Person{id:' + regno + '})-[:VISITED]->(m) where not (m)--(:LabVisit) ' + 'RETURN m.Diagnosis,m.Prescription, m.name order by m.name desc'
    d1 = global_vars.graph.run(query).to_data_frame()
    print(d1.shape)
    if d1.shape[0] != 0:
        d2 = [(str(x).replace('/', '-'),y,z) for x,y,z in zip(d1['m.name'], d1['m.Diagnosis'], d1['m.Prescription'])]
    return d2

def add_lab_visit(visname, results, date1, time, user):
    query = 'MATCH(v:Visit{name:"' + visname + '"})' + 'CREATE(m:LabVisit{name:' + '"LabVisit/' + visname + '"}) ' + 'SET m.Results = "' + results + '" ' + 'SET m.date = "' + date1 + '" ' + 'SET m.time = "' + time + '" SET m.doctor= "' + user + '" MERGE (v)<-[:LABVISITED]-(m)'
    global_vars.graph.evaluate(query)


def getMedCycles(regno):
    d2 = []
    query = 'MATCH(n:Person{id:' + regno + '})-[:CURRENTMEDS]->(m) ' + ' where m.ongoing = 1 RETURN m.ongoing,m.state,m.times,m.days,m.prescription, m.name'
    d1 = global_vars.graph.run(query).to_data_frame()
    print(d1.shape)
    if d1.shape[0] != 0:
        d2 = [(x,y) for x,y in zip(d1['m.name'], d1['m.prescription'])]
    return d2


def getStudNos():
    if global_vars.graph:
        query = "match(n:Person)--(s:Set) return n.name+' -> '+n.id + ' ('+s.name+')' as info order by n.id"
        data = global_vars.graph.run(query).to_data_frame()
        studs = list(data['info'])
        return studs
    return []

def getDrugs():
    if global_vars.graph:
        query = "match(n:Drug) return n.name as info"
        data = global_vars.graph.run(query).to_data_frame()
        studs = list(data['info'])
        return studs
    return []


def end_overdue(no_of_days):
    g1 = global_vars.graph.run("MATCH (n:Medication) where n.ongoing=1 return n.name, n.days, n.times, n.startdate")
    g1 = g1.to_data_frame()
    dday = g1["n.days"]
    stday = g1["n.startdate"]
    mname = g1["n.name"]
    # print(dday)
    dlist = []
    for dy in dday:
        if type(dy) is list:
            dlist.append(max(dy))
        else:
            dlist.append(dy)
    dlist = np.array(dlist)+no_of_days

    for name, date,day in zip(mname, stday,dlist):
        datediff = dt.today() -  dt.strptime(date,"%Y-%m-%d")
        if datediff.days >= day:
            # print('diff dey')
            qry = 'match (n:Medication{name:"'+name+'"}) set n.ongoing = 0'
            print(qry)
            try:
                global_vars.graph.evaluate(qry)
                print('done')
            except:
                pass