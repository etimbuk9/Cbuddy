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

app_name = 'drugmanagement'

urlpatterns = [
    path('add-new-drug', addNewDrug, name='add-new-drug'),
    path('restock-drug', restockDrugs, name='restock-drug'),
    path('checkout-drug', checkoutDrugs, name='checkout-drug'),
    path('restock-drug/<drugs>/<amts>', restockDrugs_submit, name='restock-drug-sbumit'),
    path('checkout-drug/<drugs>/<amts>', checkoutDrugs_submit, name='restock-drug-sbumit'),
    # path('check-pres', checkStudentPrescription, name='check-pres'),
]
