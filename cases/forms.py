from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms.models import inlineformset_factory
from .models import Case, Alert, Rule
from django.contrib.postgres.fields import ArrayField
from django.utils.translation import ugettext_lazy


class SignUpForm(UserCreationForm):
	email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')

	class Meta:
		model = User
		fields = ('username', 'email', 'password1', 'password2', )


class CaseForm(forms.ModelForm):
	class Meta:
		model = Case
		exclude = ('user', 'color',)
		# fields = ['file_id', 'deadline']


Alert_formset = inlineformset_factory(Case, Alert, form=CaseForm, extra=1)


class AlertForm(forms.ModelForm):
	class Meta:
		model = Alert
		fields = ['alert_date', 'comment']

new_errors = {
	'item_invalid': "Expected a list of integers separated by comma, get % instead",
	'invalid': 'Enter a valid value'
}


class RuleForm(forms.ModelForm):

	days = ArrayField(forms.IntegerField(), error_messages=new_errors)

	class Meta:
		model = Rule
		exclude = ('user',)
		error_messages = {
			'days': {
				'item_invalid': ugettext_lazy("Expected a list of integers separated by comma."),
				'invalid': ugettext_lazy('Please enter integers.')
			},
		}
