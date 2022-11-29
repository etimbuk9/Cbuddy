from django.shortcuts import render
from .forms import *
import global_vars

# Create your views here.

def visit(request):
    stud_no_list = getStudNos()
    form = VisitForm()
    return render(request, 'medicalvisit/visit.html', context={
        'appuser': global_vars.exportUserInfo(request)[0],
        'role': global_vars.exportUserInfo(request)[1],
        'form':form,
        'nos':stud_no_list,
        'drugs': getDrugs(),
    })


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