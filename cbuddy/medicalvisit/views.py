from django.shortcuts import render, redirect
from .forms import *
import global_vars
from datetime import datetime as dt
import numpy as np

# Create your views here.

def visit(request):
    if global_vars.get_and_set_login(request):
        stud_no_list = getStudNos()
        form = VisitForm()
        return render(request, 'medicalvisit/visit.html', context={
            'appuser': global_vars.exportUserInfo(request)[0],
            'role': global_vars.exportUserInfo(request)[1],
            'form':form,
            'nos':stud_no_list,
            'drugs': getDrugs(),
        })
    return redirect('authen:login')


def checkStudentPrescription(request):
    end_overdue(7)
    if request.method == 'GET':
        form = StudentSearchForm(request.GET)
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

    form = StudentSearchForm()
    return render(request, 'medicalvisit/dispenser.html', context={
            'appuser': global_vars.exportUserInfo(request)[0],
            'role': global_vars.exportUserInfo(request)[1],
            'form':form,
            'nos':getStudNos(),
            'drugs': getDrugs(),
        })

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
            global_vars.graph.evaluate('match (n:Medication{name:"'+name+'"}) set n.ongoing = 0')