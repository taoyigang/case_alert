# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2018-12-03 00:23
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Case',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file_id', models.CharField(max_length=200)),
                ('name', models.CharField(max_length=200)),
                ('status', models.CharField(choices=[('New', 'New'), ('Ongoing', 'Ongoing'), ('Finished', 'Finished')], default='New', max_length=10)),
                ('create_date', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Stage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('deadline', models.DateTimeField(verbose_name='date finished')),
                ('status', models.CharField(choices=[('New', 'New'), ('Ongoing', 'Ongoing'), ('Finished', 'Finished')], default='New', max_length=10)),
                ('comment', models.TextField()),
                ('case', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cases.Case')),
            ],
        ),
    ]
