from django.shortcuts import render, redirect, reverse, HttpResponse
from .forms import *
import global_vars
from datetime import datetime as dt
from datetime import timedelta as td
import numpy as np
from .models import Student, OrderedSet
from authen import extras
import pandas as pd
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
    drugs1 = str(drugs).split("->")
    drugList = []
    for item in drugs1:
        if item not in drugList:
            drugList.append(item)
    print(drugList)
    pres = pres.split(',')
    pres1 = [pres[n:n + len(drugList)] for n in range(0, len(pres), len(drugList))]

    pres1 = [[int(x) for x in y] for y in pres1]
    diag = str(diag).replace('Q->', '?')
    # d1 = dt.strptime(dt.today().strftime('%Y-%m-%d'), '%Y-%m-%d')
    # d2 = dt.today() + td(int(max(pres1[2])))

    prescr, medqry = make_med_query(pname,pres1[0],pres1[1],pres1[2], drugList, request)
    print(prescr, medqry)

    add_visit(pname, comp, diag, dt.now().strftime('%Y-%m-%d'),dt.now().strftime('%H:%M'),global_vars.exportUserInfo(request)[0], prescr, medqry)

    return redirect('authen:login')

def getPresnp(request, pname, comp, diag):
    add_visit(pname, comp, diag, dt.now().strftime('%Y-%m-%d'),dt.now().strftime('%H:%M'),global_vars.exportUserInfo(request)[0])

    return redirect('authen:login')

def setMedAmount(request, medname, amt):
    medname1 = medname.replace('->', '/')

    query = 'match(n:Medication{name: "'+str(medname1)+'"}) set n.amount = '+str(amt)
    global_vars.graph.evaluate(query)
    return redirect(reverse('medicalvisit:drug-chart', args=[medname]))

def drugchart(request, medname):
    medname1 = medname.replace('->', '/')
    # print(getPrescriptionfromMedname(medname1))
    visit_diag, visit_pres = getPrescriptionfromMedname(medname1)

    tab = getMedInfo(medname1)
    print(tab)

    for num in range(len(tab)):
        if len(tab[num][-1]) == 1:
            if type(tab[num][-1][0]) is tuple:
                tab[num][-1][0] = [(tab[num][-1][0][0], str(tab[num][-1][0][1]).lower())]
                # tab[num][-1] = [tab[num][-1]]
    print(tab)
    return render(request, 'medicalvisit/drugchart.html', context={
            'appuser': global_vars.exportUserInfo(request)[0],
            'role': global_vars.exportUserInfo(request)[1],
            'medname':medname1,
            'medname_':medname,
            'diag':visit_diag,
            'pres':visit_pres,
            'tab': tab,
        })

def stop_meds(request, medname):
    medname1 = medname.replace('->', '/')
    global_vars.graph.evaluate('match (m:Medication{name: "'+str(medname1)+'"}) set m.ongoing= 0')
    return redirect('medicalvisit:check-pres')

def setdrugchart(request, medname, choices):
    medname1 = medname.replace('->', '/')
    regno = medname.split('->')[0]
    unis1 = global_vars.graph.run('match (m:Medication{name:"'+medname1+'"}) return m.unit')
    unis1 = unis1.to_data_frame()
    unis1 = unis1.iloc[0,0]

    meds = search_meds(regno, medname1)[-1]
    states = [eval(str(x).capitalize()) for x in str(choices).split(',')]
    states = prep_state_matrix(regno, medname1, states)[0]
    statesold = search_meds(regno, medname1)[0]
    nstates = createNurses(request, regno, medname1, choices, states, statesold)
    # nstates = prep_state_matrix(medname[:4], medname1, states)[1]
    # print(meds)
    qmeds = []
    st = []
    nst = []
    for a in range(len(meds)):
        st1 = states[a]
        nst1 = nstates[a]
        dims = st1.shape
        if len(dims) == 1:
            g = st1
            g1 = nst1.to_numpy()
        else:
            g = np.resize(st1, [dims[0] * dims[1]])
            g1 = np.resize(nst1, [dims[0] * dims[1]])
        g = g.tolist()
        print('G1 is: ', g1)
        g1 = g1.tolist()
        if len(g1) == 1:
            g1 = g1[0]
        st.append(g)
        nst.append(g1)
    st = [j for i in st for j in i]
    nst = [j for i in nst for j in i]
    nst = [str(x) for x in nst]
    
    # nst = [global_vars.exportUserInfo(request)[0] for x,y in zip(st, nst) if x if not y]
    # print(st)
    # print(nst)
    
    unis = np.zeros((1, len(unis1)))
    for a in range(len(meds)):
        dd = global_vars.graph.run('match (d:Drug{name:"'+meds[a]+'"}) return d.quantity')
        dd = dd.to_data_frame()
        dd = dd.iloc[0,0]
        qmeds.append(float(dd))
        HH = states[a] == statesold[a]

        if len(HH.shape) == 1:
            HH = np.reshape(HH, (-1,1))


        for i in range(HH.shape[0]):
            for j in range(HH.shape[1]):
                if HH[i, j] == False:
                    unis[0,a] += unis1[a]
                else:
                    unis[0,a] = unis[0,a]
                # elif HH[i, j] == True and statesold[a][i, j] == 0:
                #     nst1.iloc[i, j] = '0'
                # else:
                #     nst1.iloc[i, j] = str(nst1.iloc[i, j])
    # print(unis)
    # print(qmeds)
    newstock = np.array(qmeds) - unis
    # print(newstock)
    for a1 in range(len(meds)):
        try:
            global_vars.graph.evaluate('Match(n:User{name:"' + global_vars.exportUserInfo(request)[0] + '"}) Match(d:Drug{name:"' + meds[
                a1] + '"}) Create(n)-[r:DISPENSED {date:"' + str(dt.now()) + '"}]->(d) SET r.AMOUNT = ' + str(
                unis[0,a1]))
            disp = chkdispense(meds[a1]).iloc[0,0]
            print(disp)
            if disp==1:
                global_vars.graph.evaluate(
                    'MERGE (n:Drug{name:"' + meds[a1] + '"})' + ' SET n.quantity = toInteger(' + str(newstock[0,a1]) + ') ')
            else:
                print(qmeds[a1])
                global_vars.graph.evaluate(
                    'MERGE (n:Drug{name:"' + meds[a1] + '"})' + ' SET n.quantity =' + str(int(qmeds[a1])) + ' ')
        except Exception as err:
            print(meds[a1], 'The error is: ' ,err)
            pass
    qry = 'match (m:Medication{name: "' + medname1 + '"}) set m.state=' + str(st) +' set m.nurses='+ str(nst)
    print(qry)
    #qry = 'match (n:Person{id:'+str(regno)+'}) merge(m:Medication{name: "'+str(regno)+'/'+d1.strftime('%Y-%m-%d')+'-'+d2.strftime('%Y-%m-%d')+'"}) set m.state='+str(g.tolist())+' merge (n)-[:CURRENTMEDS]->(m)'
    global_vars.graph.evaluate(qry)
    if all(st):
        global_vars.graph.evaluate('match (m:Medication{name: "' + medname1 + '"}) set m.ongoing=0 set m.finished = 1')
    return redirect('medicalvisit:check-pres')


## Utilities

def createNurses(request, regno, medname, choices, states, statesold):
    nstatesnew = []
    nstates = prep_state_matrix(regno, medname, choices)[1]
    print(nstates)
    for a in range(len(states)):
        nst1 = nstates[a]
        # print('')
        # print(states[a], statesold[a], nst1)
        HH = states[a]==statesold[a]
        # HH = pd.DataFrame(HH)
        
        if len(HH.shape) == 1:
            HH = np.reshape(HH, (-1,1))

        # print('')
        # print(HH.shape)
        if HH.shape[0]*HH.shape[1]!=1:
            for i in range(HH.shape[0]):
                for j in range(HH.shape[1]):
                    if HH[i,j]==False:
                        nst1.iloc[i,j] = str(global_vars.exportUserInfo(request)[0])+' '+ dt.strftime(dt.today(),'%Y-%m-%d %H:%M:%S')
                    elif HH[i,j]==True and statesold[a][i,j]==0:
                        nst1.iloc[i, j] = '0'
                    else:
                        nst1.iloc[i, j] = str(nst1.iloc[i, j])

        nstatesnew.append(nst1)
    return nstatesnew
    

def chkdispense(drug):
    data = global_vars.graph.run('Match (n:Drug{name:"'+str(drug)+'"}) return n.dispensable')
    data = data.to_data_frame()
    return data

def search_meds(regno, cyc):
    import pandas as pd

    # grph1 = G("http://" + Globalz.hostip + ":7474/db/data", user='neo4j', password="medical")
    data = global_vars.graph.run('match (n{id:' + str(regno) + '})-[*]->(m:Medication{name:"' + cyc + '"})-[]->(v:Visit) return m.nurses, m.state,m.times,m.days, m.prescription, m.meds, v.Diagnosis')
    data = data.to_data_frame()
    pre = data['m.prescription'][0]
    dig = data['v.Diagnosis'][0]
    ptext = 'Diagnosis\n'+dig+'\n'+'Prescription\n'+pre
    st = data['m.state']
    nst = data['m.nurses']

    # print(data)
    # print(data.iloc[0,1])

    st = st[0]
    nst = nst[0]
    hu = []
    hu1 = []
    count = 0
    for a, b in zip(data['m.times'], data['m.days']):
        for c in range(len(a)):
            A = a[c]*b[c]
            if c+1!=len(a):
                h = st[count:count+A]
                h1 = nst[count:count+A]
            else:
                h = st[count:]
                h1 = nst[count:]
            h = np.array(h)
            h1 = pd.DataFrame(h1)
            print(h)
            if a[c]*b[c] > 1:
                h = np.resize(h, [a[c], b[c]])
                h1 = h1.values.reshape((a[c], b[c]))
            
            count+=A
            hu.append(h)
            hu1.append(pd.DataFrame(h1))
    # print(data)
    # print(data.iloc[0,1])
    return hu,hu1, data['m.times'][0], data['m.days'][0], ptext, eval(data['m.meds'][0])

def prep_state_matrix(regno, medname, choices):
    import pandas as pd
    data = global_vars.graph.run('match (n{id:' + str(regno) + '})-[*]->(m:Medication{name:"' + medname + '"})-[]->(v:Visit) return m.nurses, m.state,m.times,m.days, m.prescription, m.meds, v.Diagnosis')
    data = data.to_data_frame()

    st = data['m.state']
    nst = data['m.nurses']

    # print(data)
    # print(data.iloc[0,1])

    st = choices
    print('State List: ',st)
    nst = nst[0]
    hu = []
    hu1 = []
    count = 0
    for a, b in zip(data['m.times'], data['m.days']):
        for c in range(len(a)):
            A = a[c]*b[c]
            if c+1!=len(a):
                h = st[count:count+A]
                h1 = nst[count:count+A]
            else:
                h = st[count:]
                h1 = nst[count:]
            print('H type is: ',h)
            h = np.array(h)
            h1 = pd.DataFrame(h1)
            # print(h)
            if a[c]*b[c] > 1:
                h = np.resize(h, [a[c], b[c]])
                h1 = h1.values.reshape((a[c], b[c]))
            print(h)
            count+=A
            hu.append(h)
            hu1.append(pd.DataFrame(h1))
    # print(data)
    # print(data.iloc[0,1])
    return hu, hu1

def getPrescriptionfromMedname(medname):
    query = 'match(n:Medication{name:"'+medname+'"})--(v:Visit) return v.Diagnosis, v.Prescription'
    data = global_vars.graph.run(query).to_data_frame()

    if data.shape[0] != 0:
        d2 = list(data.iloc[0,:])
        return d2
    return []

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

def get_drug_price(item):
    output = 0
    unit = global_vars.graph.run('match (n:Drug{name:"'+item+'"}) return n.unit_price')
    unit = unit.to_data_frame()
    if unit.shape[0] != 0:
        output = unit['n.unit_price'][0]
    return output

def make_med_query(regno, amts, t, n, meds, request):
    st = []
    d1 = dt.strptime(dt.today().strftime('%Y-%m-%d'), '%Y-%m-%d')
    d2 = dt.today() + td(int(max(n)))
    presp = ''
    total_cost = 0
    for a in range(len(meds)):
        presp += meds[a] + ', ' + str(amts[a]) + ' ' + str(get_drug_unit(meds[a])) + ', ' + str(t[a]) + ' time(s) per day, for ' + str(n[a]) + ' day(s)\n'
        total_cost += (amts[a]*t[a]*n[a]*get_drug_price(meds[a]))
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
        '%Y-%m-%d') + '" set m.meds = "'+str(meds)+'" set m.doctor= "'+str(global_vars.exportUserInfo(request)[0])+'" set m.amount='+str(total_cost)
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
    query = 'MATCH(n:Person{id:' + regno + '})-[:CURRENTMEDS]->(m) ' + ' where m.ongoing = 1 RETURN m.ongoing,m.state,m.times,m.days,m.prescription, m.name, m.amount'
    d1 = global_vars.graph.run(query).to_data_frame()
    d1.fillna('', inplace=True)
    print(d1)
    if d1.shape[0] != 0:
        d2 = [(x,y, str(x).replace('/', '->'), z) for x,y,z in zip(d1['m.name'], d1['m.prescription'], d1['m.amount'])]
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

    if g1.shape[0] != 0:
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

def getMedInfo(medname):
    medName = str(medname)
    medName.replace('%20', ' ')
    query = 'Match(n:Medication{name:"' + str(medName) + '"}) return n.meds, n.times, n.days, n.unit, n.state, n.nurses'
    data = global_vars.graph.run(query).to_data_frame()
    newdata = []
    output = []
    # try:
    st = data['n.state']
    nst = data['n.nurses']

    print('ST is here: ',type(st.iloc[0]))

    try:
        st = st[0]
        nst = nst[0]
        combo = []
        for i in range(len(st)):
            combo.append((st[i], nst[i]))
        hu = []
        hu1 = []
        hu2 = []
        count = 0
        for a, b in zip(data['n.times'], data['n.days']):
            for c in range(len(a)):
                A = int(a[c]) * int(b[c])
                if c + 1 != len(a):
                    h = st[count:count + A]
                    h1 = nst[count:count + A]
                    h2 = combo[count:count + A]
                else:
                    h = st[count:]
                    h1 = nst[count:]
                    h2 = combo[count:]
                h = np.array(h)
                h1 = pd.DataFrame(h1)
                # print(h1)
                if int(a[c]) * int(b[c]) > 1:
                    h = np.resize(h, [int(a[c]), int(b[c])])
                    h1 = h1.values.reshape((int(a[c]), int(b[c])))
                    h2 = [h2[i:i + int(b[c])] for i in range(0, len(h2), int(b[c]))]
                count += A
                hu.append(h.tolist())
                hu1.append(pd.DataFrame(h1))
                hu2.append(h2)
        print(hu2)
        n = zip(tuple(eval(data.iloc[0, 0])), tuple(map(lambda x: int(x), data.iloc[0, 1])),
                tuple(map(lambda x: int(x), data.iloc[0, 2])), tuple(map(lambda x: int(x), data.iloc[0, 3])),
                tuple(data.iloc[0, 4]), tuple(data.iloc[0, 5]), hu2)
        print(n)
        for a, b, c, e, f, g, d in n:
            # print(d)
            newdata.append([a, list(range(b)), list(range(1, c + 1)), e, getMedUnit(a), f, g, d])
    except Exception as err:
        print(err)
    # print(newdata)
    return newdata

def getMedUnit(drugname):
    d1 = ''
    query = 'Match (n:Drug{name:"'+drugname+'"}) return n.p_unit'
    data = global_vars.graph.run(query).to_data_frame()
    if data.shape[0] != 0:
        d1 = data.iloc[0,0]
    return d1
