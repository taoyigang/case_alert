# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView, DeleteView
from django.template import loader
from django.urls import reverse_lazy
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from .models import Case, Alert, Rule
from .forms import SignUpForm, CaseForm, RuleForm, Alert_formset
from datetime import datetime, timedelta
import random


@login_required
def index(request):
    latest_case_list = Case.objects.filter(user=request.user).order_by('-deadline')[:5]
    context = {
        'latest_case_list': latest_case_list,
    }
    return render(request, 'cases/index.html', context)


@login_required
def home(request):
    return render(request, 'cases/home.html')


@login_required
def case_detail(request, case_id):
    case = Case.objects.filter(user=request.user, id=case_id)
    get_object_or_404(case)
    alert_list = Alert.objects.filter(case_id=case_id).all()
    context = {
        'alert_list': alert_list,
        'case_id': case_id,
        'case': case.last()
    }
    return render(request, 'cases/alert_index.html', context)


@login_required
def get_case_and_alert(request):
    start_date = request.GET.get('start')
    end_date = request.GET.get('end')
    case_list = Case.objects.filter(user=request.user, deadline__range=(start_date, end_date))
    alert_list = Alert.objects.filter(case__in=case_list, alert_date__range=(start_date, end_date))
    context = {}
    for alert in alert_list:
        if not alert.comment:
            alert.comment = 'alert for {}'.format(alert.case.case_id)
        day_diff = (alert.case.deadline - alert.alert_date).days
        context[alert.id] = {'title': "{} days before deadline".format(day_diff),
                             'start': alert.alert_date.strftime('%Y-%m-%d'),
                             'color': alert.case.color, 'deadline': alert.case.deadline.strftime('%Y-%m-%d')}
    for case in case_list:
        context['{}'.format(case.case_id)] = {'title': '{}({})'.format(case.case_id, case.deadline.strftime('%Y-%m-%d')),
                                              'start': case.deadline.strftime('%Y-%m-%d'), 'color': case.color}
    return JsonResponse(context)


@login_required
def new_rule(request):
    if request.method == 'POST':
        form = RuleForm(request.POST)
        if form.is_valid():
            n_rule = form.save(commit=False)
            n_rule.user = request.user
            n_rule.save()
            return redirect('cases:rule_index')
    else:
        form = RuleForm()
    return render(request, 'cases/rule_form.html', {'form': form})


@login_required
def rule_index(request):
    latest_rule_list = Rule.objects.filter(user=request.user).order_by('-id')[:5]
    context = {
        'latest_rule_list': latest_rule_list,
    }
    return render(request, 'cases/rule_index.html', context)


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


class CaseCreateView(CreateView):
    template_name = 'cases/create.html'
    model = Case
    form_class = CaseForm

    def get_initial(self):
        initial = super(CaseCreateView, self).get_initial()
        initial['user'] = self.request.user
        return initial

    def get(self, request, *args, **kwargs):
        """
        Handles GET requests and instantiates blank versions of the form
        and its inline formsets.
        """
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        form.fields["rule"].queryset = Rule.objects.filter(user=request.user)
        alert_form = Alert_formset()
        return self.render_to_response(
            self.get_context_data(form=form,
                                  alert_form=alert_form))

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests, instantiating a form instance and its inline
        formsets with the passed POST variables and then checking them for
        validity.
        """
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        alert_form = Alert_formset(self.request.POST)
        if form.is_valid() and alert_form.is_valid():
            return self.form_valid(form, alert_form)
        else:
            return self.form_invalid(form, alert_form)

    def form_valid(self, form, alert_form):
        """
        Called if all forms are valid. Creates a Recipe instance along with
        associated Ingredients and Instructions and then redirects to a
        success page.
        """

        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.color = self.__get_color_code()
        self.object.save()
        alert_form.instance = self.object
        alert_form.save()
        if self.object.rule:
            for day in self.object.rule.days:
                alert_date = self.object.deadline - timedelta(days=day)
                new_alert = Alert(alert_date=alert_date, case=self.object)
                new_alert.save()
        return redirect('cases:home')

    def form_invalid(self, form, alert_form):
        """
        Called if a form is invalid. Re-renders the context data with the
        data-filled forms and errors.
        """
        return self.render_to_response(
            self.get_context_data(form=form,
                                  alert_form=alert_form))

    def __get_color_code(self):
        color_set = ['#f44336', '#ffebee', '#ffcdd2','#ef9a9a','#e57373','#ef5350','#f44336','#e53935','#d32f2f','#c62828','#b71c1c',
                    '#ff8a80','#ff5252','#ff1744','#d50000','#9c27b0','#f3e5f5','#e1bee7','#ce93d8','#ba68c8','#ab47bc','#9c27b0',
                    '#8e24aa','#7b1fa2','#6a1b9a','#4a148c','#ea80fc','#e040fb','#d500f9','#aa00ff','#2196f3','#e3f2fd',
                    '#bbdefb','#90caf9','#64b5f6','#42a5f5','#2196f3','#1e88e5','#1976d2','#1565c0','#0d47a1','#82b1ff','#448aff',
                    '#2979ff','#2962ff','#00bcd4','#e0f7fa','#b2ebf2', '#80deea', '#4dd0e1', '#26c6da', '#00bcd4', '#00acc1',
                    '#0097a7', '#00838f', '#006064', '#84ffff', '#18ffff', '#00e5ff', '#00b8d4', '#4caf50', '#e8f5e9', '#c8e6c9',
                    '#a5d6a7', '#81c784', '#66bb6a', '#4caf50', '#43a047', '#388e3c', '#2e7d32', '#1b5e20', '#b9f6ca', '#69f0ae',
                    '#00e676', '#00c853', '#795548', '#efebe9', '#d7ccc8', '#bcaaa4', '#a1887f', '#8d6e63', '#795548', '#6d4c41',
                    '#5d4037', '#4e342e', '#3e2723', '#ffff8d', '#ffff00', '#ffea00', '#ffd600']
        return random.choice(color_set)


class CaseDelete(DeleteView):
    model = Case
    template_name = 'cases/delete.html'
    success_url = reverse_lazy('cases:index')
