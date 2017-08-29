# encoding=utf8
from __future__ import unicode_literals

from django.db import models


class DxfModel(models.Model):
    model_guid = models.CharField(max_length=128)
    name = models.CharField(max_length=512)
    uploads = models.FileField(upload_to='dxf_files/')
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('created',)


