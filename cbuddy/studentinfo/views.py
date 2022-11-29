from django.shortcuts import render, HttpResponse, redirect
import global_vars
from medicalvisit.views import getStudNos
from .forms import *

# Create your views here.
def landingpage(request):
    students = getStudNos()
    if global_vars.get_and_set_login(request):
        if request.method == 'GET':
            form = StudentSearchForm(request.GET)
            if form.is_valid():
                data = form.cleaned_data
                student_no = data['student'].split(' -> ')[-1]
                student_no = student_no.split('(')[0].strip()
                prev_visits = getPreviousVisits(student_no)
                return render(request, 'studentinfo/landingpage.html', context={
                    'appuser': global_vars.exportUserInfo(request)[0],
                    'role': global_vars.exportUserInfo(request)[1],
                    'form':form,
                    'nos': students,
                    'visits': prev_visits,
                })

        form = StudentSearchForm()
        return render(request, 'studentinfo/landingpage.html', context={
            'appuser': global_vars.exportUserInfo(request)[0],
            'role': global_vars.exportUserInfo(request)[1],
            'form':form,
            'nos': students,
        })
    return redirect('authen:login')


def getPreviousVisits(studentno):
    d2 = []
    query = 'MATCH(n:Person{id:' + studentno + '})-[:VISITED]->(m) ' + 'RETURN m.Complain,m.Diagnosis,m.Prescription,m.date,m.time, m.name order by m.name desc'
    d1 = global_vars.graph.run(query).to_data_frame()
    d1 = d1[['m.Complain', 'm.Diagnosis', 'm.Prescription', 'm.date', 'm.time', 'm.name']]
    if d1.shape[0] != 0:
        d2 = [list(d1.iloc[x,:]) for x in range(d1.shape[0])]
    return d2