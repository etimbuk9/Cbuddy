from django.shortcuts import render
from .forms import *
import global_vars

# Create your views here.

def visit(request):
    form = VisitForm()
    return render(request, 'medicalvisit/visit.html', context={
        'appuser': global_vars.exportUserInfo(request)[0],
        'role': global_vars.exportUserInfo(request)[1],
        'form':form,
    })