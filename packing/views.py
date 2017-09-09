# encoding=utf8
import os
import json
from datetime import datetime as dt
from django.shortcuts import render

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views import generic
from packing.models import DxfModel
from irregular_packing import settings
from packing.tools import handle_uploaded_file
from packing.forms import DxfForm

from packing.no_fit_polygon.tools import input_utls
from packing.no_fit_polygon.nfp_tools import shape_num, shape_use


def home_page(request):
    return render(request, 'index.html')


class DxfModelIndexView(generic.ListView):
    model = DxfModel
    template_name = "dxf_index.html"
    paginate_by = 10   # 一个页面显示的条目
    context_object_name = "dxf_list"


def add_dxf_model(request):
    if request.method == 'POST':
        form = DxfForm(request.POST, request.FILES)
        if form.is_valid():
            dxf_model = form.save()
            try:
                s = input_utls.input_polygon(dxf_model.uploads.path)
                content = json.dumps({
                    'data': {'num_shape': len(s)},
                    'status': 0,
                    'message': 'OK'
                }, ensure_ascii=False)
                return HttpResponse(content, content_type="application/json")
            except:
                return HttpResponse(json.dumps({'info': u'读取文件出错'}), content_type="application/json")
        else:
            print form.errors
            return render(request, 'add_dxf_model.html', {'info': u'缺少文件'})
    else:
        form = DxfForm(initial={
            "material_guid":  request.GET.get('material_guid'),
            'model_guid': request.GET.get('model_guid')
        })
        content = {
            'form': form
        }
        return render(request, 'add_dxf_model.html', content)


def calc_shape_num(request):
    if request.method == 'POST':
        res = shape_num(request.POST)
        if res['is_error']:
            content = json.dumps({
                'data': '',
                'status': 0,
                'message': res['error_info']
            }, ensure_ascii=False)
        else:
            content = json.dumps({
                'data': res['data'],
                'status': 0,
                'message': 'OK'
            }, ensure_ascii=False)
        return HttpResponse(content, content_type="application/json")
    else:
        return render(request, 'calc_shape.html')


def calc_shape_use(request):
    if request.method == 'POST':
        res = shape_use(request.POST)
        if res['is_error']:
            content = json.dumps({
                'data': '',
                'status': 0,
                'message': res['error_info']
            }, ensure_ascii=False)
        else:
            content = json.dumps({
                'data': res['data'],
                'status': 0,
                'message': 'OK'
            }, ensure_ascii=False)
        return HttpResponse(content, content_type="application/json")
    else:
        return render(request, 'calc_shape.html')
