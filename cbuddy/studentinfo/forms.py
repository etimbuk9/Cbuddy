from django.forms import *

class StudentSearchForm(Form):
    student = CharField(widget=TextInput(attrs={'class':'form-control','list':'no_options'}))