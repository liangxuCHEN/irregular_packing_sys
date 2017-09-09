## 异形排列

添加模型
'''
POST /add_dxf_model
{
 'name': '模型名字',
 'model_guid': '模型名字',
 'material_guid': '模型名字',
 'uploads': 'dxf 文档'  //注意： 他们软件生成的dxf文档不能直接用， 需要用CAD打开，按ctrl+A（全选所有），按 x ，按回车，
 然后再全选所有，按x, 按回车，然后再保存。 这样的dxf文档程序才能识别
}
'''

返回结果


'''
# 通用数据
{
    "status": 0, //状态， 0：正确
    "message": "OK",  //消息
}
添加模型返回
{
    "data": {"total_num": 54}  //模型包含的图案数量
}
'''

## 计算模型排料

'''
POST /calc_shape_use

job_data = [
    {
        "Guid":"模型Guid",
        "Amount":1, //模型的数量
        "Route":1   // 1 = 可以旋转
    },
    {
        "Guid":"8887D88A-FB87-87AA-7677-EDF7777E78CC",
        "Amount":1,
        "Route":0
    }
]

返回结果
{
    "data":{
        "15A044CA-B840-49EF-99C7-DE5D1D9866D2":{ // 材料Guid
            "width":2800,  //用料宽度
            "unit":"m",   //单位
            "total_price":113.04240000000004, //总价
            "use_width":2479.000000000001,  // 用料长度
            "file_name":"static\imgs\1504951911.png", //排料图
            "model":[
                1
            ],
            "price":45.6, //单价
            "material_name":"JJ401G-3", //材料名字
            "areas":6941200.000000003 //用料面积
        },
    }
}
'''

