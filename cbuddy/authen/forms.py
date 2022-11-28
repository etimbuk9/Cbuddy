from django.forms import *

class LoginForm(Form):
    username = CharField(label='User Name')
    password = CharField(widget=PasswordInput())