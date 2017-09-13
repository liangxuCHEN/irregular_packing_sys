# encoding=utf-8
import json
import os
from packing.no_fit_polygon.nfp_tools import shape_use
from packing.no_fit_polygon.sql import has_same_job, copy_same_job, insert_new_job,\
    update_job_status, insert_job_result

FINISH_STATUS = u'运算结束'
HOST_URL = 'http://127.0.0.1:8000'


def save_project(Project_model, PackDetail_model, result, input_data):
    """
    结算结果保存
    :param input_data:
    :return:
    """
    project = Project_model(
        comment=input_data['comment'],
        data_input=input_data['data']
    )
    project.save()
    # save product
    total_price = 0
    for material, value in result.items():
        total_price += value['total_price']
        pack_detail = PackDetail_model(
            material_guid=material,
            material_name=value['material_name'],
            material_code=value['material_code'],
            unit=value['unit'],
            total_price=value['total_price'],
            pic_path=value['file_name'],
            dxf_models=str(value['model'])[1:-1],
            use_width=value['use_width'],
            price=value['price'],
            width=value['width'],
            areas=value['areas'],
        )
        pack_detail.save()
        project.products.add(pack_detail)

    project.save()
    return project, total_price


class BaseTask(object):

    def connect(self):
        """
        load django settings for using the model
        :return:
        """
        import django
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "irregular_packing.settings")
        django.setup()

    def run(self, params):
        pass


class PackingTask(BaseTask):

    def run(self, params):
        print params
        # 项目是否已经存在
        same_job = has_same_job(params)
        print 'same:', same_job
        if same_job:
            if same_job['status'] == FINISH_STATUS and same_job['url'] != '' and same_job['total_price'] != '':
                # 拷贝一份
                same_job['new_guid'] = copy_same_job(same_job, params)
                return {'data': same_job, 'message': 'has the same job', 'status': 0}

        # 添加新任务
        job_guid = insert_new_job(params)
        print job_guid
        self.connect()
        from packing.models import Project, PackDetail

        # 查看是否有重复计算
        project = Project.objects.filter(data_input=params['data']).last()
        if project:
            total_price = 0
            all_products = project.products.all()
            if project.comment != params['comment']:
                # 描述不一样，新增一个
                project.comment = params['project_comment']

                project.pk = None
                project.save()
                for product in all_products:
                    total_price += total_price + product.total_price
                    project.products.add(product)
            else:
                for product in all_products:
                    total_price += total_price + product.total_price

            url = '%s/product_detail/%d' % (HOST_URL, project.id)
            # 更新任务状态
            update_job_status(
                job_guid,
                FINISH_STATUS,
                url=url,
                price=total_price
            )
            insert_job_result(job_guid, all_products)

            return {
                'data': {
                    'project_id': project.id,
                    'url': url,
                    'price': total_price
                },
                'message': 'the project had been done',
                'status': 0
            }

        res = shape_use(params)
        if res['is_error']:
            update_job_status(job_guid, res['error_info'])
            return {
                'data': '',
                'status': 0,
                'message': res['error_info']
            }
        else:
            # 保存结果
            # 更新任务中间状态
            # update_job_status(job_guid, u'正在保存结果')
            #try:
            project, total_price = save_project(Project, PackDetail, res['data'], params)
            #except Exception as e:
                #print e
                ## 更新任务失败状态
                # update_job_status(job_guid, u'保存结果失败')
                #return {'data': res, 'message': 'error in save the result into project', 'status': 100}

            # 完结任务状态
            url = '%s/product_detail/%d' % (HOST_URL, project.id)
            # 更新任务状态
            update_job_status(
                job_guid,
                FINISH_STATUS,
                url=url,
                price=total_price
            )
            insert_job_result(job_guid, project.products.all())

            if project:
                res['new_project_id'] = project.id
                res['total_price'] = total_price

            return {'data': res, 'message': 'OK', 'status': 0}


