from django.forms import *

class VisitForm(Form):
    student_number = CharField(widget=TextInput(attrs={'class':'form-control'}))
    name = CharField(widget=TextInput(attrs={'class':'form-control'}))
    complaint = CharField(widget=Textarea(attrs={'class':'form-control'}))
    diagnosis = CharField(widget=Textarea(attrs={'class':'form-control'}))
    admit = ChoiceField(choices=(('Yes', 'Yes'), ('No', 'No')), widget=Select(attrs={'class':'form-control'}))

