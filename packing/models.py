# encoding=utf8
from __future__ import unicode_literals

from django.db import models


class DxfModel(models.Model):
    model_guid = models.CharField(max_length=128)
    material_guid = models.CharField(max_length=128)
    name = models.CharField(u'模型名字', max_length=512)
    uploads = models.FileField(u'上传文件', upload_to='dxf_files/')
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('created',)




