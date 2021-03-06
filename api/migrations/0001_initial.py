# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2017-04-19 10:18
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ApiInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('method', models.CharField(max_length=10)),
                ('url', models.URLField()),
                ('scene', models.CharField(max_length=128)),
                ('description', models.CharField(max_length=128)),
                ('overtime', models.IntegerField(default=10)),
                ('validate_method', models.CharField(max_length=128)),
                ('modify_recently', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='CommonRequestParam',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(max_length=128)),
                ('value', models.CharField(max_length=128)),
                ('type', models.CharField(max_length=128)),
                ('position', models.CharField(max_length=128)),
                ('api_info', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.ApiInfo')),
            ],
        ),
        migrations.CreateModel(
            name='Response',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('body', models.CharField(max_length=2048)),
                ('headers', models.CharField(max_length=2048)),
                ('content_type', models.CharField(max_length=128)),
                ('status_code', models.IntegerField(default=0)),
                ('api_info', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.ApiInfo')),
            ],
        ),
    ]
