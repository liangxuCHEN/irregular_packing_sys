# -*- coding: utf-8 -*-
import json
import os
from nfp_function import Nester, content_loop_rate, set_target_loop
from tools import input_utls
from settings import BIN_WIDTH, BIN_NORMAL, BIN_CUT_BIG


def data_check(data):
    try:
        print data
        input_data = json.loads(data['job_data'])
        return {'is_error': False, 'data': input_data}
    except:
        return {'is_error': True, 'error_info': u'json结构解析出错'}


def shape_num(data):
    res = data_check(data)
    if res['is_error']:
        return res
    else:
        import django
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "irregular_packing.settings")
        django.setup()
        from packing.models import DxfModel
        total_num = 0
        for input_data in res['data']:
            dxf_model = DxfModel.objects.filter(model_guid=input_data['Guid']).first()
            total_num += len(input_utls.input_polygon(dxf_model.uploads.path)) * input_data['Amount']
        return {'is_error': False, 'total_num': total_num}


def shape_use(data):
    res = data_check(data)
    if res['is_error']:
        return res
    else:
        import django
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "irregular_packing.settings")
        django.setup()
        from packing.models import DxfModel
        n = Nester()
        for input_data in res['data']:
            dxf_model = DxfModel.objects.filter(model_guid=input_data['Guid']).first()
            shapes = input_utls.input_polygon(dxf_model.uploads.path)
            for i in range(0, input_data['Amount']):
                n.add_objects(shapes)

        # 开始排列
        if n.shapes_max_length > BIN_WIDTH:
            BIN_NORMAL[2][0] = n.shapes_max_length
            BIN_NORMAL[3][0] = n.shapes_max_length

        # 选择面布
        n.add_container(BIN_NORMAL)
        # 运行计算
        n.run()
        # 设计退出条件
        # 循环特定次数
        content_loop_rate(n.best, n, loop_time=2)

if __name__ == '__main__':
    n = Nester()
    s = input_utls.input_polygon('dxf_file/E6.dxf')
    n.add_objects(s)

    if n.shapes_max_length > BIN_WIDTH:
        BIN_NORMAL[2][0] = n.shapes_max_length
        BIN_NORMAL[3][0] = n.shapes_max_length

    # 选择面布
    n.add_container(BIN_NORMAL)
    # 运行计算
    n.run()

    # 设计退出条件
    best = n.best
    # 放置在一个容器里面
    # set_target_loop(best, n)    # T6

    # 循环特定次数
    content_loop_rate(best, n, loop_time=2)   # T7 , T4



