"""cbuddy URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from .views import *

app_name = 'studentinfo'

urlpatterns = [
    path('', landingpage, name='landingpage'),
    path('query/', queryPage, name='query'),
    path('new-reg/', regnewstudent, name='new-reg'),
    path('submit-reg/', regFormSubmit, name='submit-reg'),
    path('add-new-allergy/', addNewAllergy, name='add-new-allergy'),
    path('students-on-meds/', students_on_meds, name='students-on-meds'),
    path('move-to-dispense/<regno>', moveToDispense, name='move-to-dispense'),
    path('gen-report', generateReport, name='gen-report'),
]
