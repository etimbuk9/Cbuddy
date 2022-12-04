from django.forms import *

class LoginForm(Form):
    username = CharField(label='User Name', widget=TextInput(attrs={'class':'form-control'}))
    password = CharField(widget=PasswordInput(attrs={'class':'form-control'}))

class NewUserForm(Form):
    first_name = CharField(widget=TextInput(attrs={'class':'form-control'}))
    surname = CharField(widget=TextInput(attrs={'class':'form-control'}))
    staff_number = CharField(widget=TextInput(attrs={'class':'form-control'}), required=False)
    password = CharField(widget=PasswordInput(attrs={'class':'form-control'}))
    confirm_password = CharField(widget=PasswordInput(attrs={'class':'form-control'}))
    position = ChoiceField(choices=[(x,x) for x in ['Doctor', 'Nurse']], widget=Select(attrs={'class':'form-control'}))

    def clean(self):
        cleaned_data = super(NewUserForm, self).clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")


        if password != confirm_password:
            self.add_error('confirm_password', "Password does not match")
        else:
            if len(password) < 6:
                self.add_error('password', "Password needs to be longer than 6 characters")
