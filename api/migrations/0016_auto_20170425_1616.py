# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2017-04-25 08:16
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0015_auto_20170425_1615'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='responsebody',
            name='max',
        ),
        migrations.RemoveField(
            model_name='responsebody',
            name='min',
        ),
    ]
