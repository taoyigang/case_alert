# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField


@python_2_unicode_compatible
class Rule(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	name = models.CharField(max_length=200)
	days = ArrayField(models.IntegerField(),help_text=u"eg:\'1,3,5\' will alert you 1/3/5 day before deadline")

	def __str__(self):
		return "Rule-{}".format(self.name)


@python_2_unicode_compatible
class Case(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	rule = models.ForeignKey(Rule, blank=True, null=True)
	file_id = models.CharField(max_length=200)
	deadline = models.DateTimeField()

	def __str__(self):
		return "id-{}:{}".format(self.id, self.file_id)


@python_2_unicode_compatible
class Alert(models.Model):
	case = models.ForeignKey(Case, on_delete=models.CASCADE)
	alert_date = models.DateTimeField()
	comment = models.CharField(max_length=200, blank=True)

	def __str__(self):
		return "id-{}".format(self.id)
