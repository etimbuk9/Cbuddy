from django.forms import *

class LoginForm(Form):
    username = CharField(label='User Name', widget=TextInput(attrs={'class':'form-control'}))
    password = CharField(widget=PasswordInput(attrs={'class':'form-control'}))