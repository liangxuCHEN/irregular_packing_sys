# encoding=utf8
from __future__ import unicode_literals

import uuid
import json
from django.db import models

from packing.no_fit_polygon import sql


class DxfModel(models.Model):
    model_guid = models.CharField(max_length=128)
    material_guid = models.CharField(max_length=128)
    material_name = models.CharField(u'材料名称', max_length=256, null=True)
    material_code = models.CharField(u'材料编码', max_length=18, null=True)
    rotation = models.BooleanField(u'可旋转')
    shape_num = models.IntegerField(u'包含图形', null=True)
    name = models.CharField(u'模型名字', max_length=128)
    uploads = models.FileField(u'上传文件', upload_to='dxf_files/')
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('created',)

    def __unicode__(self):
        return '%s' % self.name

    def save(self, *args, **kwargs):
        self.model_guid = str(uuid.uuid4())
        material = sql.material_info(self.material_guid)
        if material:
            self.material_name = material['material_name']
            self.material_code = material['material_code']

        super(DxfModel, self).save(*args, **kwargs)

    def to_json(self):
        d = {}
        for field in self._meta.fields:
            d[field.name] = getattr(self, field.name)

        d['created'] = d['created'].strftime('%Y-%m-%d %H:%M:%S')
        return json.dumps(d)


class PackDetail(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    material_guid = models.CharField(max_length=128)
    material_name = models.CharField(u'材料名称', max_length=256, null=True)
    material_code = models.CharField(u'材料编码', max_length=18, null=True)
    unit = models.CharField(max_length=10)
    total_price = models.FloatField(u'用料总价')
    pic_path = models.CharField(max_length=64)
    dxf_models = models.CharField('dxf_ID', max_length=256)
    use_width = models.FloatField(u'使用长度')
    price = models.FloatField(u'单价')
    width = models.FloatField(u'材料宽度')
    areas = models.FloatField(u'用料面积')

    def __unicode__(self):
        return '%s' % self.created.strftime('%Y-%m-%d %H:%M:%S')


class Project(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    products = models.ManyToManyField(PackDetail)
    data_input = models.TextField(null=True)
    comment = models.TextField()

    def __unicode__(self):
        return '%s' % self.created.strftime('%Y-%m-%d %H:%M:%S')



