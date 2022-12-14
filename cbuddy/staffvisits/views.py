from django.shortcuts import render, HttpResponse, redirect
from .forms import VisitForm, StaffSearchForm
import global_vars
from .models import Staff
from medicalvisit.views import get_drug_unit
from drugmanagement.views import get_drugs_gtys

# Create your views here.

def visit(request):
    if request.method == 'GET':
        form = StaffSearchForm(request.GET)
        if form.is_valid():
            data = form.cleaned_data
            print(data)

            staff_info = str(data['staff']).split(' -> ')
            staff = Staff(staff_info[0].strip(), staff_info[1].strip())
            # print(global_vars.show_previous_staffvisits(staff.staff_id))

            form = VisitForm()
            return render(request, 'staffvisits/visit.html', context={
                'appuser': global_vars.exportUserInfo(request)[0],
                'role': global_vars.exportUserInfo(request)[1],
                'drugs':getDrugs(),
                'prev_visits':global_vars.show_previous_staffvisits(staff.staff_id),
                'qtys':global_vars.getDrugQtys(),
                'student': staff,
                'form':form,
            })


def createStaffVisit(request,staff_id, patient, complain, diag, meds, amt):
    _amt = amt.split(',')
    _meds = meds.split('->')
    _meds = _meds[-len(_amt):]
    
    staff_name = getStaffNamefromID(staff_id)
    pres_components = [f'{x}, {y} {get_drug_unit(x)} ' for x,y in zip(_meds, _amt)]
    pres = '\n'.join(pres_components)
    print(pres_components)
    print(pres)

    writeStaffVisittoDB(request, staff_id, staff_name, patient, complain, diag, pres, _meds, _amt)
    checkoutDrugsinStaffVisit(request, _meds, _amt)

    return redirect('authen:login')

def showStaffTransactions(request):
    transactions = showDebtors()
    return render(request, 'staffvisits/record_pyts.html', context={
                'appuser': global_vars.exportUserInfo(request)[0],
                'role': global_vars.exportUserInfo(request)[1],
                'transactions':transactions,
            })

def submitAmt(request, visit_id):
    id_visit = str(visit_id).replace('->', '/')
    print(id_visit)

    data = request.POST
    # print(data['amt'])

    setVisitAmt(id_visit, data['amt'])

    return redirect('staffvisits:transactions')



## Utilities
def setVisitAmt(visit_id, amt):
    global_vars.graph.evaluate('match(n:Staffvisit{name:"'+visit_id+'"}) set n.payamt = '+str(amt)+' set n.charged = true')

def showDebtors():
    d1 = []
    data = global_vars.graph.run('match(n:Staffvisit) where (n.Paid = 0 or n.Paid=false) and n.Collected = true and not exists(n.charged) return n.staffname, n.Prescription, n.doctor, n.payamt, n.Paid, n.name')
    data = data.to_data_frame()
    dimd = data.shape
    if dimd[0] > 0:
        data = data[['n.staffname', 'n.Prescription', 'n.doctor', 'n.payamt', 'n.Paid', 'n.name']]
        data['n.name'] = data['n.name'].apply(lambda x: str(x).replace('/', '->'))
        d1 = [list(data.iloc[x,:]) for x in range(dimd[0])]
    return d1
        

def getDrugs():
    if global_vars.graph:
        query = "match(n:Drug) return n.name as info"
        data = global_vars.graph.run(query).to_data_frame()
        studs = list(data['info'])
        return studs
    return []

def getStaffNamefromID(staff_id):
    d1 = ''
    query = 'Match(n:Staff{id:"'+staff_id+'"}) return n.name'
    data = global_vars.graph.run(query).to_data_frame()
    if data.shape[0] != 0:
        d1 = data.iloc[0,0]
    return d1

def writeStaffVisittoDB(request, staff_id, staff_name, patient, complain, diag, pres, meds, amt):
    from datetime import datetime as dt
    num = staff_id.strip()

    qry = 'match(m:Staff{id:"'+num.upper()+'"}) merge (n:Staffvisit{name:"'+num.upper()+'/'+str(dt.now())+'"})<-[:STAFFVISITED]-(m) set n.staffname = "'+staff_name.upper()+'" set n.patient="'+patient.upper()+'" set n.doctor="'+str(global_vars.exportUserInfo(request)[0])+'"'
    qry1 = ' set n.Complain="'+complain+'" set n.Diagnosis="'+str(diag)+'" set n.Prescription="'+pres+'" set n.date="'+dt.strftime(dt.now(),'%Y-%m-%d')+'" set n.time = "'+dt.strftime(dt.now(),'%H:%M:%S')+'"'
    qry2 = ' set n.Paid = '+str(False).lower()+' set n.payamt = '+str(0) +' set n.Collected = '+str(True).lower()
    if num!="" and staff_name.strip()!="" and patient.strip()!="":
        Qry = qry+qry1+qry2
        print(Qry)
        global_vars.graph.evaluate(Qry)

def checkoutDrugsinStaffVisit(request, drugs, amts):
    import numpy as np
    from datetime import datetime as dt

    amtList = [float(x) for x in amts]

    old_stock = []
    for item in drugs:
        data = get_drugs_gtys(item)
        old_stock.append(data['a.quantity'].iloc[0])
    print(old_stock)
    new_stock = np.array(old_stock) - np.array(amtList)

    for item, amt, nAmt in zip(drugs, amtList,new_stock):
        qry1 = 'Match(n:User{name:"'+str(global_vars.exportUserInfo(request)[0])+'"}) Match(d:Drug{name:"'+item+'"}) Create(n)-[r:CHECKEDOUT {date:"'+str(dt.now())+'"}]->(d) SET r.AMOUNT = '+str(amt)
        qry2 = 'MERGE (n:Drug{name:"'+ item+ '"})'+' SET n.quantity = toInteger('+str(nAmt)+') '

        try:
            global_vars.graph.evaluate(qry1)
            global_vars.graph.evaluate(qry2)
        except:
            pass