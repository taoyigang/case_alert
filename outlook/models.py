# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.contrib.auth.models import User


@python_2_unicode_compatible
class OutlookKey(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	outlook_app_id = models.CharField(max_length=200, unique=True)
	outlook_app_key = models.CharField(max_length=200, unique=True)
	access_token = models.CharField(max_length=2000, blank=True)
	id_token = models.CharField(max_length=2000, blank=True)
	refresh_token = models.CharField(max_length=2000, blank=True)
	expires = models.IntegerField(default=0)
	valid = models.BooleanField(default=False)

	def __str__(self):
		return "OutlookKey:{}".format(self.id)
