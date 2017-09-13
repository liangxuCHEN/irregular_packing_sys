# encoding=utf8
import os
import json
from datetime import datetime as dt

from django.core import serializers
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views import generic
from packing.models import DxfModel, Project, PackDetail
from packing.forms import DxfForm

from packing.no_fit_polygon.tools import input_utls
from packing.no_fit_polygon.nfp_tools import shape_num, shape_use
from tasks.package import PackingTask
from packing.no_fit_polygon.sql import jobs_list

from mrq.job import queue_job, Job


def allow_all(response):
    """
    解决跨域的问题
    :param response:
    :return:
    """
    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
    response["Access-Control-Max-Age"] = "1000"
    response["Access-Control-Allow-Headers"] = "*"
    return response


def home_page(request):
    return render(request, 'index.html')


class DxfModelIndexView(generic.ListView):
    model = DxfModel
    template_name = "dxf_index.html"
    paginate_by = 10   # 一个页面显示的条目
    context_object_name = "dxf_list"


class ProjectIndexView(generic.ListView):
    model = Project
    template_name = "projects.html"
    paginate_by = 10   # 一个页面显示的条目
    context_object_name = "project_list"


def dxf_json(request):
    query = DxfModel.objects.all()
    if request.GET.get('name'):
        query = query.filter(name__contains=request.GET.get('name'))

    if request.GET.get('material_guid'):
        query = query.filter(material_guid=request.GET.get('material_guid'))

    content = serializers.serialize("json", query)
    response = HttpResponse(content, content_type="application/json")
    return allow_all(response)


def add_dxf_model(request):
    if request.method == 'POST':
        form = DxfForm(request.POST, request.FILES)
        if form.is_valid():
            dxf_model = form.save()
            try:
                # 计算模型包含的图形数量
                s = input_utls.input_polygon(dxf_model.uploads.path)
                dxf_model.shape_num = len(s)
                dxf_model.save()

                content = json.dumps({
                    'data': {'num_shape': dxf_model.shape_num},
                    'status': 0,
                    'message': 'OK'
                }, ensure_ascii=False)
                response = HttpResponse(content, content_type="application/json")
            except:
                response = HttpResponse(json.dumps({'info': u'读取文件出错'}), content_type="application/json")
        else:
            print form.errors
            response = render(request, 'add_dxf_model.html', {'info': u'缺少文件'})
    else:
        form = DxfForm(initial={
            "material_guid":  request.GET.get('material_guid'),
            'model_guid': request.GET.get('model_guid')
        })
        content = {
            'form': form
        }
        response = render(request, 'add_dxf_model.html', content)

    return response


@csrf_exempt
def calc_shape_num(request):
    if request.method == 'POST':
        print request.POST
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
        response = HttpResponse(content, content_type="application/json")
    else:
        response = render(request, 'calc_shape.html')

    return allow_all(response)


@csrf_exempt
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
        response = HttpResponse(content, content_type="application/json")
    else:
        response = render(request, 'calc_shape.html')

    return allow_all(response)


@csrf_exempt
def shape_use_task(request):
    if request.method == 'POST':
        taskparams = dict()
        taskparams['post_data'] = request.POST
        job_id = queue_job("tasks.package.PackingTask", taskparams)
        print job_id
        response = HttpResponse(json.dumps({'job_id': str(job_id)}), content_type="application/json" )
    else:
        response = render(request, 'calc_shape.html')

    return allow_all(response)


def show_project(request, p_id):
    project = get_object_or_404(Project, pk=p_id)
    bin_list = project.products.all()
    content = {
        'created': project.created,
        'bin_list': bin_list,
        'host': request.get_host()
    }
    try:
        content['comments'] = json.loads(project.comment)
    except:
        content['comment_text'] = project.comment
    return render(request, 'project_detail.html', content)


def get_jobs_list(request):
    response = HttpResponse(jobs_list(), content_type="application/json")
    return allow_all(response)



