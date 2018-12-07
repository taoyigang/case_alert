# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.contrib.auth.models import User


@python_2_unicode_compatible
class Case(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
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
