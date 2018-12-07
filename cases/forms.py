from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms.models import inlineformset_factory
from .models import Case, Alert


class SignUpForm(UserCreationForm):
	email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')

	class Meta:
		model = User
		fields = ('username', 'email', 'password1', 'password2', )


class CaseForm(forms.ModelForm):
	class Meta:
		model = Case
		exclude = ('user',)
		# fields = ['file_id', 'deadline']


Alert_formset = inlineformset_factory(Case, Alert, form=CaseForm, extra=1)


class AlertForm(forms.ModelForm):
	class Meta:
		model = Alert
		fields = ['alert_date', 'comment']
