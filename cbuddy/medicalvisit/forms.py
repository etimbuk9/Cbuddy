from django.forms import *

class VisitForm(Form):
    # student = CharField(widget=TextInput(attrs={'class':'form-control','list':'no_options'}))
    # name = CharField(widget=TextInput(attrs={'class':'form-control'}))
    complaint = CharField(widget=Textarea(attrs={'class':'form-control'}))
    diagnosis = CharField(widget=Textarea(attrs={'class':'form-control'}))
    # admit = ChoiceField(choices=(('Yes', 'Yes'), ('No', 'No')), widget=Select(attrs={'class':'form-control'}))

class StudentSearchForm(Form):
    student = CharField(widget=TextInput(attrs={'class':'form-control','list':'no_options'}))
