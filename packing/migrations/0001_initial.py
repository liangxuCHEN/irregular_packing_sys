# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-08-28 08:21
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DxfModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('model_guid', models.CharField(max_length=128)),
                ('name', models.CharField(max_length=512)),
                ('file_path', models.FloatField()),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ('created',),
            },
        ),
    ]
