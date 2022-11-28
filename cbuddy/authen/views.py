from django.shortcuts import render, HttpResponse
from .forms import *

# Create your views here.

def login(request):
    form = LoginForm()
    return render(request, )


def logout(request):
    pass