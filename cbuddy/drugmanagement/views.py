from django.shortcuts import render, HttpResponse, redirect
from .forms import *
import global_vars

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



## Utility Functions
def add_new_drug(name, category, p_unit, s_unit, amp, qty, disp):
    global_vars.graph.evaluate(
        'Merge (d:Drug{name: "' + name.upper() + '"}) SET d.category = "' + category.upper() + '" SET d.quantity = ' + qty + ' SET d.p_unit = "' + p_unit + '" set d.s_unit="' + s_unit + '" set d.ampunit = ' + amp)
    if disp == 'Yes':
        global_vars.graph.evaluate('Merge (d:Drug{name: "' + name.upper() + '"}) SET d.dispensable = ' + str(1))
    else:
        global_vars.graph.evaluate('Merge (d:Drug{name: "' + name.upper() + '"}) SET d.dispensable = ' + str(0))