from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Case, Alert


class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', )


class CaseForm(forms.ModelForm):
    class Meta:
        model = Case
        fields = ['file_id', 'alert_date']
        widgets = {
            'alert_date': forms.SelectDateWidget(),
        }


class AlertForm(forms.ModelForm):
    class Meta:
        model = Alert
        fields = ['deadline', 'comment']
        widgets = {
            'deadline': forms.SelectDateWidget(),
        }