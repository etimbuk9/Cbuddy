from django.forms import *

class DBSelectForm(Form):
    filename = FileField(widget=FileInput(attrs={'class':'form-control', 'accept':'.accdb'}))