# -*- coding: utf-8 -*-
import json
import os
from nfp_function import Nester, content_loop_rate, set_target_loop
from tools import input_utls
from settings import BIN_WIDTH, BIN_NORMAL, BIN_CUT_BIG
from sql import material_info


def data_check(data):
    try:
        # 前端控制输入的字段
        input_data = json.loads(data['data'])
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
            # TODO: 参数的值合理性判断
            if input_data.get('Guid') and input_data.get('Amount'):
                dxf_model = DxfModel.objects.filter(model_guid=input_data['Guid']).first()
                # print 'rotation', dxf_model.rotation
                if dxf_model:
                    total_num += len(input_utls.input_polygon(dxf_model.uploads.path)) * int(input_data['Amount'])
                else:
                    return {'is_error': True, 'error_info': u'模型{}没有找到'.format(input_data['Guid'])}
            else:
                return {'is_error': True, 'error_info': u'数据缺少参数 Guid 或 Amount'}
        return {'is_error': False, 'data': {'total_num': total_num}}


def shape_use(data):
    res = data_check(data)
    if res['is_error']:
        return res
    else:
        import django
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "irregular_packing.settings")
        django.setup()
        from packing.models import DxfModel

        # 循环特定次数 TODO: 用户去选择优化时间
        type_loop = data.get('loop') or 'primary'

        if type_loop == 'primary':
            loop_time = 1
            routing = 4
        elif type_loop == 'middle':
            loop_time = 30
            routing = 8
        else:
            loop_time = 90
            routing = 16

        # 间距
        border = data.get('border')
        if border:
            border = int(data.get('border'))

        material_dict = dict()
        for input_data in res['data']:
            # 确保整形
            amount = input_data.get('Amount') or 0
            if amount == 0:
                return {'is_error': True, 'data': input_data, 'error_info': u'Without Amount'}
            input_data['Amount'] = int(amount)

            dxf_model = DxfModel.objects.filter(model_guid=input_data['Guid']).first()
            shapes = input_utls.input_polygon(dxf_model.uploads.path)

            # 相同材料一起排料，新的材料就创建一个新材料信息
            if material_dict.get(dxf_model.material_guid):
                material_dict[dxf_model.material_guid]['model'].append(str(dxf_model.id))
                for i in range(0, input_data['Amount']):
                    material_dict[dxf_model.material_guid]['nesting'].add_objects(shapes)
            else:
                # TODO:通过材料Guid 找 材料的信息：单价,单位--> 米 平方英尺, pcs--> limited or not
                material = material_info(dxf_model.material_guid)
                material_dict[dxf_model.material_guid] = {
                    'model': [dxf_model.id],
                }
                if dxf_model.rotation:
                    # 默认是不旋转图形，True 可以旋转图形
                    material_dict[dxf_model.material_guid]['nesting'] = Nester(border=border, rotations=routing)
                else:
                    material_dict[dxf_model.material_guid]['nesting'] = Nester(border=border)
                # 载入图形
                for i in range(0, input_data['Amount']):
                    material_dict[dxf_model.material_guid]['nesting'].add_objects(shapes)

                if material:
                    material_dict[dxf_model.material_guid].update(material)

                    # TODO:需要选择尺寸
                    if material_dict[dxf_model.material_guid]['nesting'].shapes_max_length > BIN_WIDTH:
                        # 预测长度
                        BIN_NORMAL[2][0] = material_dict[dxf_model.material_guid]['nesting'].shapes_max_length
                        BIN_NORMAL[3][0] = material_dict[dxf_model.material_guid]['nesting'].shapes_max_length

                    if material['width'] > 0:
                        # 宽度
                        BIN_NORMAL[1][1] = material['width']
                        BIN_NORMAL[2][1] = material['width']

                    # 选择bin, 单位是米==无限长，平方或其他==固定大小的面料
                    #print BIN_NORMAL
                    if material['unit'] == '米':
                        material_dict[dxf_model.material_guid]['nesting'].add_container(BIN_NORMAL, limited=False)
                    else:
                        material_dict[dxf_model.material_guid]['nesting'].add_container(BIN_CUT_BIG)

        # 设计退出条件
        for key, value in material_dict.items():
            # 启动运算
            value['nesting'].run()
            # 固定循环次数，找最优解
            value.update(content_loop_rate(value['nesting'].best, value['nesting'],
                                           loop_time=int(loop_time), save_img=True))
            value.pop('nesting')
            if value['unit'] == '米':
                value['unit'] = 'm'
                value['total_price'] = float(value['use_width']) / 1000 * value['price']
            else:
                value['unit'] = 'psc'
                # 1英尺平方 == 92903.04毫米平方
                value['total_price'] = (int(value['areas'] / 92903.04)+1) * value['price']
        return {'is_error': False, 'data': material_dict}

if __name__ == '__main__':
    n = Nester(border=None, rotations=4)
    s = input_utls.input_polygon('dxf_file/E6.dxf')
    n.add_objects(s)

    if n.shapes_max_length > BIN_WIDTH:
        BIN_NORMAL[2][0] = n.shapes_max_length
        BIN_NORMAL[3][0] = n.shapes_max_length

    # 选择面布
    n.add_container(BIN_NORMAL, limited=False)
    # 运行计算
    n.run()

    # 设计退出条件
    best = n.best
    # 放置在一个容器里面
    # set_target_loop(best, n)    # T6
    # 循环特定次数
    print content_loop_rate(best, n, loop_time=2, save_img=False)   # T7 , T4




