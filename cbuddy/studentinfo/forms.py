from django.forms import *
from datetime import datetime as dt
from datetime import timedelta as td

class StudentSearchForm(Form):
    student = CharField(widget=TextInput(attrs={'class':'form-control','list':'no_options'}))

class StudentQueryForm(Form):
    student_set = ChoiceField(choices=[(x, x) for x in ['','JSS1', 'JSS2', 'JSS3', 'SS1', 'SS2', 'SS3']], widget=Select(attrs={'class':'form-control'}), required=False)
    gender = ChoiceField(choices=[(x, x) for x in ['','M', 'F']], widget=Select(attrs={'class':'form-control'}), required=False)
    blood_group = ChoiceField(choices=[(x, x) for x in ['','A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']], widget=Select(attrs={'class':'form-control'}), required=False)
    condition = ChoiceField(choices=[(x, x) for x in ['','PUD', 'Asthma', 'HbSS', 'Allergies', 'Disabilities']], widget=Select(attrs={'class':'form-control'}), required=False)
    genotype = ChoiceField(choices=[(x, x) for x in ['','AA', 'AS', 'SS', 'AC', 'SC', 'CC']], widget=Select(attrs={'class':'form-control'}), required=False)
    vaccines = ChoiceField(choices=[(x, x) for x in ['','BCG', 'Tetanus Toxoid alone', 'Polio', 'Measles', 'Rubella', 'Triple Antigen', 'Typhoid', 'Cholera', 'Yellow Fever']], widget=Select(attrs={'class':'form-control'}), required=False)
    start_date = DateField(widget=DateInput(attrs={'class':'datepicker'}), required=False)
    end_date = DateField(widget=DateInput(attrs={'class':'datepicker'}), required=False)

class NewAllergyForm(Form):
    student = CharField(widget=TextInput(attrs={'class':'form-control','list':'no_options'}))
    allergy = CharField(widget=TextInput(attrs={'class':'form-control'}), label='Allergy (separate allergies using a comma (","))')