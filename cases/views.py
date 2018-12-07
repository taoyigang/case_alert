# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView
from django.template import loader
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from .models import Case, Alert
from .forms import SignUpForm, CaseForm, AlertForm, Alert_formset


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
def new(request):
    if request.method == 'POST':
        form = CaseForm(request.POST)
        if form.is_valid():
            new_case = form.save(commit=False)
            new_case.user = request.user
            new_case.save()
            return redirect('cases:index')
    else:
        form = CaseForm()
    return render(request, 'cases/new.html', {'form': form})


@login_required
def get_case_and_alert(request):
    start_date = request.GET.get('start')
    end_date = request.GET.get('end')
    case_list = Case.objects.filter(user=request.user, deadline__range=(start_date, end_date))
    alert_list = Alert.objects.filter(case__in=case_list, alert_date__range=(start_date, end_date))
    context = {}
    for alert in alert_list:
        if not alert.comment:
            alert.comment = 'alert for {}'.format(alert.case.file_id)
        context[alert.id] = {'title': alert.comment, 'start': alert.alert_date.strftime('%Y-%m-%d'), 'color': '#428cf4'}
    for case in case_list:
        context['case-'.format(case.id)] = {'title': case.file_id, 'start': case.deadline.strftime('%Y-%m-%d'), 'color': '#f45f42'}
    return JsonResponse(context)


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
        self.object.save()
        alert_form.instance = self.object
        alert_form.save()
        return redirect('cases:index')

    def form_invalid(self, form, alert_form):
        """
        Called if a form is invalid. Re-renders the context data with the
        data-filled forms and errors.
        """
        return self.render_to_response(
            self.get_context_data(form=form,
                                  alert_form=alert_form))