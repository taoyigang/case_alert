# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.template import loader
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from .models import Case, Alert
from .forms import SignUpForm, CaseForm, AlertForm


@login_required
def index(request):
    latest_case_list = Case.objects.order_by('-alert_date')[:5]
    context = {
        'latest_case_list': latest_case_list,
    }
    return render(request, 'cases/index.html', context)


@login_required
def home(request):
    return render(request, 'cases/home.html')


@login_required
def case_detail(request, case_id):
    alert_list = Alert.objects.filter(case_id=case_id).all()
    context = {
        'alert_list': alert_list,
    }
    return render(request, 'cases/alert_index.html', context)


@login_required
def new(request):
    if request.method == 'POST':
        form = CaseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('cases:index')
    else:
        form = CaseForm()
    return render(request, 'cases/new.html', {'form': form})


@login_required
def new_alert(request, case_id):
    if request.method == 'POST':
        form = AlertForm(request.POST)
        if form.is_valid():
            new_s = form.save(commit=False)
            new_s.case_id = case_id
            new_s.save()
            return HttpResponseRedirect('/'+case_id)
    else:
        case = Case.objects.get(id=case_id)
        form = AlertForm()
    return render(request, 'cases/new_alert.html', {'form': form, 'case': case})


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('cases:index')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})
