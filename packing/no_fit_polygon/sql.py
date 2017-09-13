# encoding=utf8
import pymssql
import uuid
import json
import settings as default
import pandas as pd
from datetime import datetime as dt

import sys
reload(sys)
sys.setdefaultencoding("utf-8")


JOB_STATE_TABLE = 'T_PRT_PackingJobState'
JOB_DETAIL_TABLE = 'T_PRT_PackingJobDetail'


class Mssql:
    def __init__(self):
        self.host = default.BOM_HOST
        self.user = default.BOM_HOST_USER
        self.pwd = default.BOM_HOST_PASSWORD
        self.db = default.BOM_DB

    def __get_connect(self):
        if not self.db:
            raise (NameError, "do not have db information")
        self.conn = pymssql.connect(
            host=self.host,
            user=self.user,
            password=self.pwd,
            database=self.db,
            charset="utf8"
        )
        cur = self.conn.cursor()
        if not cur:
            raise (NameError, "Have some Error")
        else:
            return cur

    def exec_query(self, sql):
        cur = self.__get_connect()
        cur.execute(sql)
        res_list = cur.fetchall()

        # the db object must be closed
        self.conn.close()
        return res_list

    def exec_non_query(self, sql):
        cur = self.__get_connect()
        cur.execute(sql)
        self.conn.commit()
        self.conn.close()

    def exec_many_query(self, sql, param):
        cur = self.__get_connect()
        try:
            cur.executemany(sql, param)
            self.conn.commit()
        except Exception as e:
            print e
            self.conn.rollback()

        self.conn.close()


def init_sql_253():
    """
    为了pandas连接数据库的设置
    :return:
    """
    conn = pymssql.connect(
        host=default.BOM_HOST,
        user=default.BOM_HOST_USER,
        password=default.BOM_HOST_PASSWORD,
        database=default.BOM_DB,
        charset="utf8"
    )
    return conn


def material_info(guid):
    conn = Mssql()
    sql_text = "SELECT ChargeUnit,UnitPrice,MaterialName,WideWidth,MaterialCode FROM V_PRT_SoftMaterialMain where Guid='{guid}'".format(guid=guid)
    res = conn.exec_query(sql_text)
    if res:
        return {
            'unit': res[0][0],
            'price': float(res[0][1]),
            'material_name': res[0][2],
            'width': int(res[0][3]*1000),
            'material_code': res[0][4]
        }
    return None


def material_list():
    conn = init_sql_253()
    sql_text = """SELECT Guid, MaterialCode,MaterialName FROM T_PRT_SoftMaterialMain(nolock) WHERE IsDisable=0"""
    df = pd.io.sql.read_sql(sql_text, con=conn)
    df['Guid'] = df['Guid'].astype(str)
    return df.to_json(orient='records')


def jobs_list():
    conn = init_sql_253()
    sql_text = """SELECT Guid, Url, Status, TotalPrice, CreateDate, UpdateDate FROM %s""" % JOB_STATE_TABLE
    df = pd.io.sql.read_sql(sql_text, con=conn)
    df['Guid'] = df['Guid'].astype(str)
    return df.to_json(orient='records')


def has_same_job(data):
    conn = Mssql()
    sql_text = """SELECT Guid, Status, Url, TotalPrice FROM {table} WHERE Comment='{c}'
    and Data='{d}'""".format(c=data['comment'], d=data['data'], table=JOB_STATE_TABLE)
    res = conn.exec_query(sql_text)
    if res:
        return {
            'guid': res[0][0],
            'status': res[0][1],
            'url': res[0][2],
            'total_price': float(res[0][3])
        }
    return None


def copy_same_job(old_job, new_data):
    created = dt.today()
    conn = Mssql()
    new_guid = uuid.uuid4()
    sql_text = "insert into %s values ('%s','%s','%s','%s','%s','%s','%s', '%f')" % (
        JOB_STATE_TABLE, new_guid, new_data['comment'], old_job['url'], new_data['data'],
        old_job['status'], created.strftime('%Y-%m-%d %H:%M:%S'), created.strftime('%Y-%m-%d %H:%M:%S'),
        old_job['total_price'])
    conn.exec_non_query(sql_text)

    # 更新详细内容
    sql_text = "SELECT * FROM {table} WHERE Guid='{Guid}'".format(
        table=JOB_DETAIL_TABLE, Guid=old_job['guid'])
    details = conn.exec_query(sql_text)

    insert_data = list()
    for d in details:
        insert_data.append((new_guid, d[2], d[3]))

    sql_text = "insert into " + JOB_DETAIL_TABLE + " values (%s, %s, %s)"
    conn.exec_many_query(sql_text, insert_data)
    return str(new_guid)


def insert_new_job(new_data):
    created = dt.today()
    conn = Mssql()
    new_guid = uuid.uuid4()
    sql_text = "insert into %s values ('%s','%s','%s','%s','%s','%s','%s', '%f')" % (
        JOB_STATE_TABLE, new_guid, new_data['comment'], '', new_data['data'],
        default.NEW_JOB, created.strftime('%Y-%m-%d %H:%M:%S'), created.strftime('%Y-%m-%d %H:%M:%S'),
        0)
    conn.exec_non_query(sql_text)
    return str(new_guid)


def update_job_status(guid, status, url=None, price=None):
    conn = Mssql()
    update_time = dt.today()
    # 结束状态
    if url and price:
        sql_text = """UPDATE {table} SET UpdateDate='{update_time}', Status='{status}',
        Url='{url}', TotalPrice='{price}' WHERE Guid='{guid}'""".format(
            guid=guid, status=status, url=url, price=price,
            update_time=update_time.strftime('%Y-%m-%d %H:%M:%S'), table=JOB_STATE_TABLE)
    else:
        # 一般状态
        sql_text = "UPDATE {table} SET UpdateDate='{update_time}', Status='{status}' WHERE Guid='{guid}'".format(
            guid=guid, status=status, update_time=update_time.strftime('%Y-%m-%d %H:%M:%S'), table=JOB_STATE_TABLE)
    conn.exec_non_query(sql_text)


def insert_job_result(guid, details):
    conn = Mssql()
    insert_data = list()
    for d in details:
        insert_data.append((guid, d.material_code, d.total_price))

    sql_text = "insert into " + JOB_DETAIL_TABLE + " values (%s, %s, %s)"
    conn.exec_many_query(sql_text, insert_data)

if __name__ == '__main__':
    # print material_info('F36FC853-5938-45E1-AE95-0DD31E032EF4')
    #r = [(data['Guid'], "{} {}".format(data['MaterialCode'], data['MaterialName'])) for data in material_list()]
    # material_list = [(data['Guid'], "{} {}".format(data['MaterialCode'], data['MaterialName']))
    #                  for data in json.loads(material_list())]
    update_job_status('77857C3D-367E-4DA6-A2B3-17FE1BCAB7F7', u'正在保存结果')
    print material_list

