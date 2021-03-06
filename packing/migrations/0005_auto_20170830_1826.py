# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-08-30 10:26
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('packing', '0004_dxfmodel_material_guid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dxfmodel',
            name='material_guid',
            field=models.CharField(max_length=128),
        ),
        migrations.AlterField(
            model_name='dxfmodel',
            name='name',
            field=models.CharField(max_length=512, verbose_name='\u6a21\u578b\u540d\u5b57'),
        ),
        migrations.AlterField(
            model_name='dxfmodel',
            name='uploads',
            field=models.FileField(upload_to='dxf_files/', verbose_name='\u4e0a\u4f20\u6587\u4ef6'),
        ),
    ]
