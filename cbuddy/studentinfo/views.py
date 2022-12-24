from io import BytesIO
import os
from django.contrib.staticfiles import finders
from django.conf import settings
from django.shortcuts import render, HttpResponse, redirect
from medicalvisit.views import end_overdue
import global_vars
from medicalvisit.views import getStudNos
from .forms import *
from .CDBdefaultercalc import detector
from django.template.loader import get_template
from xhtml2pdf import pisa

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

def regnewstudent(request):
    student_data = []
    vacs = []
    conds = []
    if request.method == 'GET':
        # print(request.GET)
        form = StudentSearchForm(request.GET)
        if form.is_valid():
            data = form.cleaned_data
            student_info = data['student']
            student_no = data['student'].split(' -> ')[-1]
            student_no = student_no.split('(')[0].strip()

            student_data = search_studinfo(student_no)
            student_data['student_set'] = search_set(student_no)[0]
            print(search_studinfo(student_no))
            # student_data['choice'] = search_studinfo(student_no)['']
            print(student_data)
            vacs = search_studVacinfo(student_no)
            conds = search_studCondinfo(student_no)
        else:
            print(form.errors)
        bioform = BioDataForm(initial=student_data)
        dec_form = DeclarationForm(initial=student_data)
        vaccines = ["MEASLES", "RUBELLA", "TRIPLE ANTIGEN", "TYPHOID", "YELLOW FEVER", "BCG", "TETANUS TOXOID ALONE", "POLIO", "CHOLERA"]
        conditions = ["PUD", "HBSS", "ASTHMA", "ALLERGIES", "DISABILITIES"]
        return render(request, 'studentinfo/newreg.html', context={
            'appuser': global_vars.exportUserInfo(request)[0],
            'role': global_vars.exportUserInfo(request)[1],
            'bioform':bioform,
            'decform':dec_form,
            'vacs': vacs,
            'full_vac':vaccines,
            'conds': conds,
            'conditions':conditions,

        })
    return redirect('authen:login')

def regFormSubmit(request):
    if request.method == 'POST':
        data = request.POST
        vaccines = ["MEASLES", "RUBELLA", "TRIPLE ANTIGEN", "TYPHOID", "YELLOW FEVER", "BCG", "TETANUS TOXOID ALONE", "POLIO", "CHOLERA"]
        conditions = ["PUD", "HBSS", "ASTHMA", "ALLERGIES", "DISABILITIES"]

        data_keys = list(data.keys())

        vacs =[x for x in data_keys if x in vaccines]
        conds =[x for x in data_keys if x in conditions]


        add_new_stud(data['id'], data['name'], data['address'], data['NOS'], data['NOB'], data['F_Occupation'], data['M_Occupation'], data['F_Phone'], data['M_Phone'], vacs, data['Declaration'], data['Blood_Group'], data['Genotype'], conds, data['student_set'])
        print(data_keys, vacs, conds)

    return redirect('authen:login')

def generateReport(request):
    set_dll_search_path()
    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            student_name = str(data['student']).split(' -> ')[0].strip()
            regno = str(data['student']).split(' -> ')[1].split('(')[0].strip()
            fromDate = data['start_date'].strftime('%Y-%m-%d')
            todate = data['end_date'].strftime('%Y-%m-%d')
            vis_data = searchquery_report(regno, fromDate,todate)
            vis_data = filterReport(vis_data, todate)

            new_data = [list(vis_data.iloc[x,:]) for x in range(vis_data.shape[0])]

            template = get_template('studentinfo/report-template.html')
            context_dict = {
                'name':student_name,
                'regno':regno,
                'fromdate':fromDate,
                'todate': todate,
                'all_results': new_data,
                'dets': data['details'],
                'vis_count':len(new_data),
            }

            # return render(request, 'transcripts/template.html', context=context_dict)
            html = template.render(context_dict)
            result = BytesIO()

            pdf = pisa.pisaDocument(BytesIO(html.encode("utf-8")), result, link_callback=link_callback)
            print(result)
            if not pdf.err:
                print(result)
                return HttpResponse(result.getvalue(), content_type='application/pdf')
            else:
                print(pdf.err)
            return None

    form = ReportForm()
    return render(request, 'studentinfo/gen-report.html', context={
            'appuser': global_vars.exportUserInfo(request)[0],
            'role': global_vars.exportUserInfo(request)[1],
            'form':form,
    })




## Utility Functions
def add_new_stud(regno, name, addr, NOS, NOB, FO, MO, FPH, MPH, imm, dec, BG, Bgen, cond, clazz):  # , clazz):
    graph1 = global_vars.graph
    d = graph1.run('MATCH (n:Person{id:' + regno + '})-[r]-(d) RETURN d')
    d1 = d.to_data_frame()
    d1m = d1.shape
    if d1m[0] > 0:
        graph1.evaluate('MATCH (n:Person{id:' + regno + '})-[r]-(d) DELETE r')
    graph1.evaluate(
        'MATCH (n:Person{id:' + regno + '}) MATCH(d:Visit) WHERE d.name STARTS WITH "' + regno + '" MERGE (n)-[:VISITED]->(d)')
    graph1.evaluate(
        'MATCH (n:Person{id:' + regno + '}) MATCH(d:Medication) WHERE d.name CONTAINS "' + regno + '" MERGE (n)-[:CURRENTMEDS]->(d)')
    graph1.evaluate(
        'MATCH(n:Person{id:' + regno + '}) ' + 'MERGE(m:Set{name:"' + clazz.upper() + '"}) ' + 'MERGE (n)-[:MEMBEROF]->(m)')
    graph1.evaluate(
        'MERGE (n:Person{id:' + regno + '}) ' + 'SET n.name = "' + name.upper() + '"' + ' SET n.address = "' + addr.upper() + '"' + ' SET n.NOS = "' + NOS + '" SET n.NOB = ' + NOB + ' Set n.F_Occupation = "' + FO.upper() + '"' + ' SET n.M_Occupation = "' + MO.upper() + '"')
    graph1.evaluate(
        'MERGE (n:Person{id:' + regno + '}) ' + 'SET n.F_Phone = "' + FPH + '"' + ' SET n.M_Phone = "' + MPH + '"')
    graph1.evaluate(
        'MERGE (n:Person{id:' + regno + '}) ' + ' SET n.Blood_Group = "' + BG + '"' + ' SET n.Genotype = "' + Bgen + '"' + ' SET n.Declaration = "' + dec + '"')
    # graph1.evaluate('MERGE (n:Person{id:' + regno + '}) ' + ' SET n.report = "' + report + '"')

    for im in imm:
        graph1.evaluate('MATCH(n:Person{id:' + regno + '}) ' + 'MERGE(m:Vaccine{name:"' + im.upper() + '"}) ' + 'MERGE (n)-[:IMMUNETO]->(m)')

    for con in cond:
        graph1.evaluate('MATCH(n:Person{id:' + regno + '}) ' + 'MERGE(m:Condition{name:"' + con.upper() + '"}) ' + 'MERGE (n)-[:SUFFERSFROM]->(m)')

def search_studVacinfo(regno):
    d1 = []
    d = global_vars.graph.run('MATCH (a:Person{id:' + regno + '})-[]->(m:Vaccine) RETURN m.name').to_data_frame()
    if d.shape[0] != 0:
        d1 = list(d['m.name'])
    return d1

def search_studCondinfo(regno):
    d1 = []
    d = global_vars.graph.run('MATCH (a:Person{id:' + regno + '})-[]->(m:Condition) RETURN m.name').to_data_frame()
    if d.shape[0] != 0:
        d1 = list(d['m.name'])
    return d1

def report_gen(request, data, dets):
    # print(data, dets)
    new_data = [list(data.iloc[x,:]) for x in range(data.shape[0])]

    # print(new_data)
    template = get_template('studentinfo/report-template.html')
    context_dict = {
        'all_results': new_data,
        'dets': dets,
        'vis_count':len(new_data),
    }

    # return render(request, 'transcripts/template.html', context=context_dict)
    html = template.render(context_dict)
    result = BytesIO()

    pdf = pisa.pisaDocument(BytesIO(html.encode("utf-8")), result, link_callback=link_callback)
    print(result)
    if not pdf.err:
        print(result)
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    else:
        print(pdf.err)
    return None

def filterReport(data, todate):
    row = []
    mdate = data["m.startdate"]
    vdate = data["q.date"]
    for m, v in zip(mdate, vdate):
        if m == None or v == None or m == '' or v == '':
            row.append(False)
        else:
            if dt.strptime(m, '%Y-%m-%d') == dt.strptime(v, '%Y-%m-%d'):
                row.append(True)
            else:
                row.append(False)
    # print(row)
    d1 = data[row]
    print(d1)
    d1['Remarks'] = detector(d1, dt.strptime(todate, '%Y-%m-%d'))[0]
    return d1


def searchquery_report(regno, fromdate, todate):
    global tdata, comb, A, B
    # frm = "1970-01-01 00:00:00"
    # tod = dt.strftime(dt.now(), '%Y-%m-%d %H:%M:%S')
    # graph1 = G("http://" + Globalz.hostip + ":7474/db/data/", password="medical")
    # setquery = 'match (n:Person)-[*]->(s:Set{name: "' + Queues[0].upper() + '"})'
    # genderquery = 'match (n:Person) where n.gender contains "' + Queues[1].upper() + '"'
    BGquery = 'match (n:Person) where n.id = ' + str(regno).upper()
    frmquery = 'match (n:Person)-[]->(q:Visit) where q.date >="' + str(fromdate) + '"'
    toquery = 'match (n:Person)-[]->(q:Visit) where q.date <="' + str(todate) + '"'

    Qus = [BGquery, frmquery, toquery]
    query = ''
    count = 0
    for a in range(len(Qus)):
        query += ' ' + Qus[a]

    query += ' match(m:Medication)-[]->(q:Visit)<-[]-(n:Person) return n.name, m.days, m.times, m.state, m.startdate, n.id, q.Complain, q.Diagnosis,q.Prescription, q.doctor, q.date, q.name, ID(q), ID(m) order by n.id'
    
    d = global_vars.graph.run(query)
    d1 = d.to_data_frame()
    return d1

def search_studinfo(regno):
    d = global_vars.graph.run('MATCH (a:Person{id:' + regno + '}) RETURN properties(a)')
    d = d.to_data_frame()
    da = d.iloc[0, 0]
    return da

def search_set(regno):
    d = global_vars.graph.run('MATCH (a:Person{id:' + regno + '})-[*]->(m:Set) RETURN a.name,a.id,a.gender, m.name')
    d1 = d.to_data_frame()
    d = list(d1['m.name'])
    return d

def getStudentsOnMedication():
    d1 = []
    query = 'MATCH(a:Person)-[*]->(m:Medication) where m.ongoing=1 return distinct a.name, a.id, a.gender'
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

def link_callback(uri, rel):
    """
    Convert HTML URIs to absolute system paths so xhtml2pdf can access those
    resources
    """
    result = finders.find(uri)
    if result:
        if not isinstance(result, (list, tuple)):
            result = [result]
        result = list(os.path.realpath(path) for path in result)
        path = result[0]
    else:
        sUrl = settings.STATIC_URL  # Typically /static/
        sRoot = settings.STATIC_ROOT  # Typically /home/userX/project_static/
        mUrl = settings.MEDIA_URL  # Typically /media/
        mRoot = settings.MEDIA_ROOT  # Typically /home/userX/project_static/media/

        if uri.startswith(mUrl):
            path = os.path.join(mRoot, uri.replace(mUrl, ""))
        elif uri.startswith(sUrl):
            path = os.path.join(sRoot, uri.replace(sUrl, ""))
            print(path)
        else:
            return uri

    # make sure that file exists
    if not os.path.isfile(path):
        raise Exception(
            'media URI must start with %s or %s' % (sUrl, mUrl)
        )
    return path

def set_dll_search_path():
   # Python 3.8 no longer searches for DLLs in PATH, so we have to add
   # everything in PATH manually. Note that unlike PATH add_dll_directory
   # has no defined order, so if there are two cairo DLLs in PATH we
   # might get a random one.
   if os.name != "nt" or not hasattr(os, "add_dll_directory"):
       return
   for p in os.environ.get("PATH", "").split(os.pathsep):
       try:
           os.add_dll_directory(p)
       except OSError:
           pass