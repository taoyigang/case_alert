# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.template import loader
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from .models import Case, CaseForm, Stage
from .forms import SignUpForm


@login_required
def index(request):
    latest_case_list = Case.objects.order_by('-create_date')[:5]
    context = {
        'latest_case_list': latest_case_list,
    }
    return render(request, 'cases/index.html', context)


@login_required
def case_detail(request, case_id):
    return HttpResponse("You're looking at case %s." % case_id)


@login_required
def new(request):
    if request.method == 'POST':
        form = CaseForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/cases/')
    else:
        form = CaseForm()
    return render(request, 'cases/new.html', {'form': form})


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('/cases/')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})
