from django.shortcuts import render, HttpResponse, redirect
from .forms import *
import global_vars
import pandas as pd

# Create your views here.

def addNewDrug(request):
    if request.method == 'POST':
        form = NewDrugForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            add_new_drug(data['name'].upper(), data['category'].upper(), data['prescription_unit'], data['store_unit'], str(data['amount_per_unit']), str(data['quantity']), data['directly_dispensable'],)
        else:
            print(form.errors)

    form = NewDrugForm()
    return render(request, 'drugmanagement/newdrug.html', context={
            'appuser': global_vars.exportUserInfo(request)[0],
            'role': global_vars.exportUserInfo(request)[1],
            'form':form,
        })


def restockDrugs(request):
    if request.method == 'POST':
        print(request.POST)

    return render(request, 'drugmanagement/restock.html', context={
            'appuser': global_vars.exportUserInfo(request)[0],
            'role': global_vars.exportUserInfo(request)[1],
            'drugs': global_vars.getDrugs(),
            'qtys':global_vars.getDrugQtys(),
            # 'form':form,
        })

def checkoutDrugs(request):
    if request.method == 'POST':
        print(request.POST)

    return render(request, 'drugmanagement/checkout.html', context={
            'appuser': global_vars.exportUserInfo(request)[0],
            'role': global_vars.exportUserInfo(request)[1],
            'drugs': global_vars.getDrugs(),
            'qtys':global_vars.getDrugQtys(),
            # 'form':form,
        })

def restockDrugs_submit(request, drugs, amts):
    import numpy as np
    from datetime import datetime as dt
    drugList = list(set([x for x in str(drugs).split("->")]))
    print(drugList)
    amtList = [float(x.strip()) for x in str(amts).split(",")]

    old_stock = []
    for item in drugList:
        data = get_drugs_gtys(item)
        old_stock.append(data['a.quantity'].iloc[0])
    print(old_stock)
    new_stock = np.array(old_stock) + np.array(amtList)

    for item, amt, nAmt in zip(drugList, amtList,new_stock):
        global_vars.graph.evaluate('Match(n:User{name:"'+str(global_vars.exportUserInfo(request)[0])+'"}) Match(d:Drug{name:"'+item+'"}) Create(n)-[r:STOCKEDBY {date:"'+str(dt.now())+'"}]->(d) SET r.AMOUNT = '+str(amt))
        global_vars.graph.evaluate('MERGE (n:Drug{name:"'+ item+ '"})'+' SET n.quantity = toInteger('+str(nAmt)+') ')

    return redirect('drugmanagement:restock-drug')


def checkoutDrugs_submit(request, drugs, amts):
    import numpy as np
    from datetime import datetime as dt
    drugList = list(set([x for x in str(drugs).split("->")]))
    print(drugList)
    amtList = [float(x.strip()) for x in str(amts).split(",")]

    old_stock = []
    for item in drugList:
        data = get_drugs_gtys(item)
        old_stock.append(data['a.quantity'].iloc[0])
    print(old_stock)
    new_stock = np.array(old_stock) - np.array(amtList)

    for item, amt, nAmt in zip(drugList, amtList,new_stock):
        global_vars.graph.evaluate('Match(n:User{name:"'+str(global_vars.exportUserInfo(request)[0])+'"}) Match(d:Drug{name:"'+item+'"}) Create(n)-[r:CHECKEDOUT {date:"'+str(dt.now())+'"}]->(d) SET r.AMOUNT = '+str(amt))
        global_vars.graph.evaluate('MERGE (n:Drug{name:"'+ item+ '"})'+' SET n.quantity = toInteger('+str(nAmt)+') ')

    return redirect('drugmanagement:checkout-drug')

## Utility Functions
def add_new_drug(name, category, p_unit, s_unit, amp, qty, disp):
    global_vars.graph.evaluate(
        'Merge (d:Drug{name: "' + name.upper() + '"}) SET d.category = "' + category.upper() + '" SET d.quantity = ' + qty + ' SET d.p_unit = "' + p_unit + '" set d.s_unit="' + s_unit + '" set d.ampunit = ' + amp)
    if disp == 'Yes':
        global_vars.graph.evaluate('Merge (d:Drug{name: "' + name.upper() + '"}) SET d.dispensable = ' + str(1))
    else:
        global_vars.graph.evaluate('Merge (d:Drug{name: "' + name.upper() + '"}) SET d.dispensable = ' + str(0))

def get_drugs_gtys(name):
    d = global_vars.graph.run('MATCH (a:Drug{name:"'+str(name)+'"}) RETURN a.name, a.quantity ORDER BY a.name ASC').to_data_frame()
    if d.shape[0] != 0:
        return d
    return pd.DataFrame()