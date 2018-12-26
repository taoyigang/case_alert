# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.views.generic import CreateView, DeleteView, UpdateView
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.template import loader
from django.urls import reverse_lazy
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from .models import Case, Alert, Rule
from .forms import SignUpForm, CaseForm, RuleForm, Alert_formset
from datetime import datetime, timedelta
from outlook.outlookservice import post_my_event
from outlook.authhelper import get_access_token
import random


@login_required
def index(request):
    case_list = Case.objects.filter(user=request.user).order_by('-deadline').all()
    paginator = Paginator(case_list, 50)
    page = request.GET.get('page')
    try:
        cases = paginator.page(page)
    except PageNotAnInteger:
        cases = paginator.page(1)
    except EmptyPage:
        cases = paginator.page(paginator.num_pages)
    return render(request, 'cases/index.html', {'cases': cases})


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
        day_diff = (alert.case.deadline - alert.alert_date).days
        context[alert.id] = {'start': alert.alert_date.strftime('%Y-%m-%d'),
                             'color': alert.case.color, 'deadline': alert.case.deadline.strftime('%Y-%m-%d'),
                             'id': str(alert.case.id), 'case_id': alert.case.case_id}
        if not alert.comment:
            context[alert.id]['title'] = "{}\n{} days before deadline".format(alert.case.case_id, day_diff)
        else:
            context[alert.id]['title'] = "{}\n{}".format(alert.case.case_id, alert.comment)
    for case in case_list:
        context['{}'.format(case.case_id)] = {'title': '{}({})'.format(case.case_id, case.deadline.strftime('%Y-%m-%d')),
                                              'start': case.deadline.strftime('%Y-%m-%d'), 'color': case.color,
                                              'id': str(case.id), 'case_id': case.case_id}
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
    rule_list = Rule.objects.filter(user=request.user).all()
    paginator = Paginator(rule_list, 50)
    page = request.GET.get('page')
    try:
        rules = paginator.page(page)
    except PageNotAnInteger:
        rules = paginator.page(1)
    except EmptyPage:
        rules = paginator.page(paginator.num_pages)
    return render(request, 'cases/rule_index.html', {'rules': rules})


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
        access_token = get_access_token(self.request, self.request.build_absolute_uri(reverse('outlook:gettoken')))
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

        if access_token:
            post_my_event(access_token, self.object, is_case=True)
            alerts = Alert.objects.filter(case=self.object).all()
            for alert in alerts:
                post_my_event(access_token, alert, is_case=False)
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
        color_set = ['#d32f2f', '#c62828', '#b71c1c', '#ad1457', '#880e4f', '#4a148c', '#6a1b9a', '#311b92', '#4527a0',
                     '#304ffe', '#3d5afe', '#0d47a1', '#006064', '#00838f', '#1b5e20', '#00c853', '#e65100', '#795548',
                     '#6d4c41', '#455a64']
        return random.choice(color_set)


class CaseDelete(DeleteView):
    model = Case
    template_name = 'cases/delete.html'
    success_url = reverse_lazy('cases:index')


class UpdateRule(UpdateView):
    model = Rule
    fields = ['name', 'days']
    template_name = 'cases/update_rule.html'
    success_url = reverse_lazy('cases:rule_index')

    def get_context_data(self, **kwargs):
        context = super(UpdateRule, self).get_context_data(**kwargs)
        cases = Case.objects.filter(user=self.request.user, rule=self.object).all()
        case_names = ', '.join([case.case_id for case in cases])
        context['cases'] = case_names
        return context


class RuleDelete(DeleteView):
    model = Rule
    template_name = 'cases/rule_delete.html'
    success_url = reverse_lazy('cases:rule_index')

    def get_context_data(self, **kwargs):
        context = super(RuleDelete, self).get_context_data(**kwargs)
        cases = Case.objects.filter(user=self.request.user, rule=self.object).all()
        case_names = ', '.join([case.case_id for case in cases])
        context['cases'] = case_names
        return context
