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

app_name = 'medicalvisit'

urlpatterns = [
    path('', visit, name='visit'),
    path('check-pres', checkStudentPrescription, name='check-pres'),
    path('set-med-amount/<medname>/<amt>', setMedAmount, name='set-med-amount'),
    path('drug-chart/<medname>', drugchart, name='drug-chart'),
    path('setdrugchart/<medname>/<choices>', setdrugchart, name='setdrugchart'),
    path('labvisit', newLabVisit, name='labvisit'),
    path('submit-labvisit/<medname>', submitLabResult, name='submit-labvisit'),
    path('get-pres/<pname>/<comp>/<diag>/<drugs>/<pres>', getPres, name='get-pres'),
    path('get-pres/<pname>/<comp>/<diag>', getPresnp, name='get-presnp'),
    path('stop-meds/<medname>', stop_meds, name='stop-meds'),
]
