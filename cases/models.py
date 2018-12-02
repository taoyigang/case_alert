# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.forms import ModelForm
from django import forms


@python_2_unicode_compatible
class Case(models.Model):
    file_id = models.CharField(max_length=200)
    name = models.CharField(max_length=200)
    STATUS_CHOICES = (
        ('New', 'New'),
        ('Ongoing', 'Ongoing'),
        ('Finished', 'Finished'),
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='New',
    )
    create_date = models.DateTimeField(auto_now=True,)

    def __str__(self):
        return "Case {} is {}".format(self.id, self.status)


class CaseForm(ModelForm):
    class Meta:
        model = Case
        fields = ['file_id', 'name']


@python_2_unicode_compatible
class Stage(models.Model):
    case = models.ForeignKey(Case, on_delete=models.CASCADE)
    deadline = models.DateTimeField('date finished')
    STATUS_CHOICES = (
        ('New', 'New'),
        ('Ongoing', 'Ongoing'),
        ('Finished', 'Finished'),
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='New',
    )
    comment = models.TextField()

    def __str__(self):
        return "Stage {} is {}, belong to Case {}".format(self.id, self.status, self.case.id)


class DateInput(forms.DateInput):
    input_type = 'date'


class StageForm(ModelForm):
    class Meta:
        model = Stage
        fields = ['deadline', 'comment']
        widgets = {
            'deadline': DateInput()
        }


