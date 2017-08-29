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


def upload_file(request):
    """
    上传模型文档（dxf格式）
    :param request:
    :return:
    """
    if request.method == 'POST':
        created = dt.today().strftime('-%Y_%m_%d_%H_%M_%S')
        l_file = request.FILES.get('learn_file')
        if l_file:
            path = os.path.join(settings.BASE_DIR, 'static', 'dxf_files', str(l_file)+created)
            handle_uploaded_file(l_file, path)

    return HttpResponseRedirect('/model_list')


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
            # print dxf_model.uploads.url
            # print dxf_model.uploads.path
            try:
                s = input_utls.input_polygon(dxf_model.uploads.path)
                return HttpResponse(json.dumps({'num_shape': len(s)}, ensure_ascii=False), content_type="application/json")
            except:
                return HttpResponse(json.dumps({'info': u'读取文件出错'}), content_type="application/json")
        else:
            return render(request, 'add_dxf_model.html', {'info': u'缺少文件'})
    else:
        form = DxfForm()
        return render(request, 'add_dxf_model.html', {'form': form})


def calc_shape_num(request):
    if request.method == 'POST':
        res = shape_num(request.POST)
        return HttpResponse(json.dumps(res, ensure_ascii=False), content_type="application/json")
    else:
        return render(request, 'calc_shape_num.html')


def calc_shape_use(request):
    if request.method == 'POST':
        res = shape_use(request.POST)
        return HttpResponse(json.dumps(res, ensure_ascii=False), content_type="application/json")
    else:
        return render(request, 'calc_shape_use.html')
