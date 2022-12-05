from django.shortcuts import render, HttpResponse, redirect
from medicalvisit.views import end_overdue
import global_vars
from medicalvisit.views import getStudNos
from .forms import *

# Create your views here.
def landingpage(request):
    if global_vars.get_and_set_login(request):
        students = getStudNos()
        form = StudentSearchForm()
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
                    'meds': getPreviousMedication(student_no),
                    'allergies': getAttributes(student_no),
                    'labs': getLabVisits(student_no),
                })

        return render(request, 'studentinfo/landingpage.html', context={
            'appuser': global_vars.exportUserInfo(request)[0],
            'role': global_vars.exportUserInfo(request)[1],
            'form':form,
            'nos': students,
        })
    return redirect('authen:login')


def queryPage(request):
    if request.method == 'POST':
        form = StudentQueryForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            print(data)
            results = searchquery(data)
            return render(request, 'studentinfo/queryPage.html', context={
                'appuser': global_vars.exportUserInfo(request)[0],
                'role': global_vars.exportUserInfo(request)[1],
                'form':form,
                'results': results,
                'no': len(results),
            })
    form = StudentQueryForm()
    return render(request, 'studentinfo/queryPage.html', context={
            'appuser': global_vars.exportUserInfo(request)[0],
            'role': global_vars.exportUserInfo(request)[1],
            'form':form,
        })

def addNewAllergy(request):
    if request.method == 'POST':
        form = NewAllergyForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            student_no = data['student'].split(' -> ')[-1]
            student_no = student_no.split('(')[0].strip()

            addAttribute(student_no, data['allergy'])

    form = NewAllergyForm()
    return render(request, 'studentinfo/newallergy.html', context={
            'appuser': global_vars.exportUserInfo(request)[0],
            'role': global_vars.exportUserInfo(request)[1],
            'form':form,
            'nos': getStudNos(),
        })

def students_on_meds(request):
    end_overdue(7)
    student_models = getStudentsOnMedication()
    return render(request, 'studentinfo/studs-on-meds.html', context={
            'appuser': global_vars.exportUserInfo(request)[0],
            'role': global_vars.exportUserInfo(request)[1],
            'studs':student_models,
        })

def moveToDispense(request, regno):
    stud = getStudbyRegno(regno)
    print(type(stud))
    idx = list(global_vars.users['name'] == global_vars.exportUserInfo(request)[0]).index(True)
    global_vars.users['inits'].iat[idx] = {'student':str(stud)}
    print(global_vars.users)
    return redirect('medicalvisit:check-pres')

## Utility Functions
def getStudentsOnMedication():
    d1 = []
    query = 'MATCH(a:Person)-[*]->(m:Medication) where m.ongoing=1 return a.name, a.id, a.gender'
    d = global_vars.graph.run(query).to_data_frame()
    if d.shape[0] != 0:
        d1 = [list(d.iloc[x,:]) for x in range(d.shape[0])]
    return d1

def getStudbyRegno(regno):
    if global_vars.graph:
        query = "match(n:Person{id:"+str(regno)+"})--(s:Set) return n.name+' -> '+n.id + ' ('+s.name+')' as info order by n.id"
        data = global_vars.graph.run(query).to_data_frame()
        studs = data['info'].iloc[0]
        return studs
    return []

def addAttribute(studentno, attribute):
    attribs = str(attribute).split(',')
    attribs = [str(x).strip() for x in attribs]
    for attr in attribs:
        query = 'match(n:Person{id:'+studentno+'}) merge(a:Attribute{name:"'+str(attr).upper().strip()+'"}) merge (n)<-[:ATTRIBUTEDTO]-(a)'
        global_vars.graph.evaluate(query)

def searchquery(data):
    frmquery, toquery, setquery = "", "", ""

    if data['student_set']:
        setquery = 'match (n:Person{status:FALSE})-[*]->(s:Set) where s.name = "'+data['student_set'].upper()+'" '
    genderquery = 'match (n:Person{status:FALSE}) where n.gender contains "'+data['gender'].upper()+'"'
    BGquery = 'match (n:Person{status:FALSE}) where n.Blood_Group contains "'+data['blood_group'].upper()+'" '
    Genoquery = 'match (n:Person{status:FALSE}) where n.Genotype contains "'+data['genotype'].upper()+'" ' 
    scasequery = 'match(n:Person{status:FALSE})-[]->(c:Condition) where c.name contains "'+ data['condition'].upper() +'" '
    vacquery = 'match (n:Person{status:FALSE})-[]->(v:Vaccine) where v.name contains "'+data['vaccines'].upper()+'" '
    if data['start_date']:
        frmquery = 'match (n:Person{status:FALSE})-[]->(q:Visit) where q.date >="'+data['start_date'].strftime('%Y-%m-%d')+'"'
    if data['end_date']:
        toquery = 'match (n:Person{status:FALSE})-[]->(q:Visit) where q.date <="'+ data['end_date'].strftime('%Y-%m-%d')+'"'
    
    Qus = [setquery, genderquery, BGquery,  scasequery, Genoquery, vacquery, frmquery, toquery]
    query = ''
    count = 0
    for i, v in enumerate(data.items()):
        print(v)
        if v[-1]:
            query += ' '+Qus[i]
    
    if not(data['student_set']):
        query = ' Match (n:Person{status:FALSE})-[*]->(s:Set) '+ query + ' optional match(n)-[]->(q:Visit) return n.name, s.name, n.id, n.gender, count(q) order by n.id'
    else:
        query += ' optional match(n)-[]->(q:Visit) return n.name, s.name, n.id, n.gender, count(q) order by n.id'
    
    print(query)
    d = global_vars.graph.run(query)
    d1 = d.to_data_frame()
    d2 = []
    if d1.shape[0]>0:
        cols = d1.columns.tolist()
        cols = ['n.name', 'n.id', 'n.gender', 's.name', 'count(q)']
        # cols = [cols[3], cols[2], cols[1], cols[4], cols[0]]
        d1 = d1[cols]
        d2 = [list(d1.iloc[x,:]) for x in range(d1.shape[0])]
    return d2

def getPreviousVisits(studentno):
    d2 = []
    query = 'MATCH(n:Person{id:' + studentno + '})-[:VISITED]->(m) ' + 'RETURN m.Complain,m.Diagnosis,m.Prescription,m.date,m.time, m.name order by m.name desc'
    d1 = global_vars.graph.run(query).to_data_frame()
    if d1.shape[0] != 0:
        d1 = d1[['m.Complain', 'm.Diagnosis', 'm.Prescription', 'm.date', 'm.time', 'm.name']]
        d2 = [list(d1.iloc[x,:]) for x in range(d1.shape[0])]
    return d2

def getPreviousMedication(studentno):
    data2 = []
    q = 'Match (n:Medication)--(v:Visit) where n.name starts with "'+str(studentno)+'" and n.ongoing=0 return n.name, n.prescription, n.ongoing, n.finished, n.startdate, n.days,n.doctor order by n.startdate desc'
    data = global_vars.graph.run(q).to_data_frame()
    data['complete'] = ""
    dimd = data.shape
    for a in range(dimd[0]):
        if data['n.finished'].iloc[a]==1:
            data['complete'].iloc[a] = 'Yes'
        else:
            data['complete'].iloc[a] = 'No'

    for a in range(dimd[0]):
        if type(data['n.days'].iloc[a]) is list:
            data['n.days'].iloc[a]=max(data['n.days'].iloc[a])
    if data.shape[0] != 0:
        data = data[["n.name", "n.days", "n.startdate","complete",'n.doctor',"n.prescription"]]
        data2 = [list(data.iloc[x,:]) for x in range(data.shape[0])]
    return data2

def getLabVisits(studentno):
    d2 = []
    query = 'MATCH(n:Person{id:' + studentno + '})-[*2]-(m:LabVisit) ' + 'RETURN m.Results,m.doctor,m.date,m.time, m.name'
    d = global_vars.graph.run(query)
    d1 = d.to_data_frame()
    if d1.shape[0] != 0:
        d1 = d1[['m.date', 'm.Results', 'm.doctor', 'm.time', 'm.name']]
        d2 = [list(d1.iloc[x,:]) for x in range(d1.shape[0])]
    return d2

def getAttributes(studentno):
    data_out = []
    query = 'match(n:Person{id:'+studentno+'})-[]-(a:Attribute) return a.name'
    data = global_vars.graph.run(query).to_data_frame()
    print(data)

    if data.shape[0] > 0:
        data_out = list(data['a.name'])
    return data_out