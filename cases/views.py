# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required


@login_required
def index(request):
    return HttpResponse("Hello, world. You're at the case index.")