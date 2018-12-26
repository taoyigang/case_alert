from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.contrib.auth.hashers import make_password
from django.views.generic import CreateView, DeleteView, UpdateView
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.template import loader
from django.urls import reverse_lazy
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from outlook.authhelper import *
from outlook.outlookservice import *
from .forms import OutlookKeyForm
from .models import OutlookKey


@login_required
def home(request):
	redirect_uri = request.build_absolute_uri(reverse('outlook:gettoken'))
	# sign_in_url = get_signin_url(redirect_uri)
	sign_in_url = '#'
	context = {'signin_url': sign_in_url}
	return render(request, 'outlook/home.html', context)


def gettoken(request):
	auth_code = request.GET['code']
	redirect_uri = request.build_absolute_uri(reverse('outlook:gettoken'))
	outlook_key = OutlookKey.objects.filter(user=request.user, valid=False).first()
	token = get_token_from_code(auth_code, redirect_uri, outlook_key.outlook_app_id, outlook_key.outlook_app_key)
	access_token = token['access_token']
	user = get_me(access_token)
	refresh_token = token['refresh_token']
	expires_in = token['expires_in']

	# expires_in is in seconds
	# Get current timestamp (seconds since Unix Epoch) and
	# add expires_in to get expiration time
	# Subtract 5 minutes to allow for clock differences
	expiration = int(time.time()) + expires_in - 300
	outlook_key.access_token = access_token
	outlook_key.id_token = token['id_token']
	outlook_key.refresh_token = refresh_token
	outlook_key.expires = expires_in
	outlook_key.valid = True
	outlook_key.save()
	# Save the token in the session
	request.session['access_token'] = access_token
	request.session['refresh_token'] = refresh_token
	request.session['token_expires'] = expiration
	return HttpResponseRedirect(reverse('outlook:key_index'))


def events(request):
	access_token = get_access_token(request, request.build_absolute_uri(reverse('outlook:gettoken')))
	# If there is no token in the session, redirect to home
	if not access_token:
		return HttpResponse('something goes really wrong')
	else:
		messages = get_my_events(access_token)
		return HttpResponse('Messages: {0}'.format(messages))


@login_required
def new_outlook_key(request):
	if request.method == 'POST':
		form = OutlookKeyForm(request.POST)
		if form.is_valid():
			n_key = form.save(commit=False)
			# n_key.outlook_app_key = make_password(form.cleaned_data['outlook_app_key'])
			n_key.user = request.user
			n_key.save()
			return redirect('outlook:key_index')
	else:
		key_list = OutlookKey.objects.filter(user=request.user).all()
		if key_list:
			return redirect('outlook:key_index')
		else:
			form = OutlookKeyForm()
	return render(request, 'outlook/outlook_key_form.html', {'form': form})


@login_required
def key_index(request):
	redirect_uri = request.build_absolute_uri(reverse('outlook:gettoken'))
	key_list = OutlookKey.objects.filter(user=request.user).all()
	paginator = Paginator(key_list, 50)
	page = request.GET.get('page')
	keys = None
	create_access = False
	try:
		keys = paginator.page(page)
	except PageNotAnInteger:
		keys = paginator.page(1)
	except EmptyPage:
		keys = paginator.page(paginator.num_pages)
	finally:
		if keys:
			for key in keys:
				key.sign_in_url = get_signin_url(redirect_uri, key.outlook_app_id)
				key.outlook_app_key = key.outlook_app_key[:3] + '*******************'
			for key in keys:
				if not key.valid:
					create_access = True
					break
		else:
			create_access = True

	return render(request, 'outlook/key_index.html', {'keys': keys, 'create_access': create_access})


@login_required
def tutorial(request):
	return render(request, 'outlook/tutorial.html')


class KeyDelete(DeleteView):
	model = OutlookKey
	template_name = 'outlook/delete.html'
	success_url = reverse_lazy('outlook:key_index')
