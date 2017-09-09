# encoding=utf8
import pymssql
import uuid
import json
import settings as default

import sys
reload(sys)
sys.setdefaultencoding("utf-8")


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


def material_info(guid):
    conn = Mssql()
    sql_text = "SELECT ChargeUnit,UnitPrice,MaterialName,WideWidth FROM V_PRT_SoftMaterialMain where Guid='{guid}'".format(guid=guid)
    res = conn.exec_query(sql_text)
    if res:
        return {'unit': res[0][0], 'price': float(res[0][1]), 'material_name': res[0][2], 'width': int(res[0][3]*1000)}
    return None

if __name__ == '__main__':
    print material_info('F36FC853-5938-45E1-AE95-0DD31E032EF4')