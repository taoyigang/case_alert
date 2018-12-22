from django import forms
from .models import OutlookKey


class OutlookKeyForm(forms.ModelForm):
	outlook_app_key = forms.CharField(widget=forms.PasswordInput)

	class Meta:
		model = OutlookKey
		exclude = ('user', 'valid', 'access_token', 'id_token', 'refresh_token', 'expires')
