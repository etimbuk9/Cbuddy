from django.forms import *

class VisitForm(forms.Form):
    patient = CharField(widget=TextInput(attrs={'class':'form-control'}))
    complaint = CharField(widget=Textarea(attrs={'class':'form-control'}))
    diagnosis = CharField(widget=Textarea(attrs={'class':'form-control'}))


class StaffSearchForm(Form):
    staff = CharField(widget=TextInput(attrs={'class':'form-control','list':'staff_options'}))