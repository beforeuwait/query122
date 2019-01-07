# coding=utf-8

"""
    作为122官网查询的主要web服务
    传入 车牌+发动机号
    返回检测结果
"""

import os
import time
import json
import logging
import tornado.web
import offical_122_api
from importlib import reload
from tornado.ioloop import IOLoop
from offical_122_api import receive_form_data_from_api

# logging模块

logger = logging.getLogger(name='ocr')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(os.path.join(os.path.split(__file__)[0], './web_122.log'))
fmt = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(fmt)
logger.addHandler(handler)



class MainHandler(tornado.web.RequestHandler):

    param_names = ['carNo', 'engineNo', 'vin']

    def get(self):
        self.write('welcome')

    def post(self):
        reload(offical_122_api)
        st = time.time()
        api_info = self.lets_do_spider()
        self.write(api_info)
        ed = time.time()
        logger.debug('完成请求\t {0},耗时\t{1}'.format(api_info, ed - st))
        del api_info


    def lets_do_spider(self):
        """针对2.0版本
        增加了一个参数 vin，但是不做处理
        """
        # 省略了参数验证环节
        engineNo = self.get_argument('engineNo')
        carNo = self.get_argument('carNo')
        vin = self.get_argument('vin')
        data = {
            'carNo': carNo,
            'engineNo': engineNo,
        }
        logger.debug('接受参数\t{0}'.format(data))
        result = receive_form_data_from_api(data)
        return json.dumps(result, ensure_ascii=False)




application = tornado.web.Application([(r"/122", MainHandler),])


if __name__ == "__main__":
    application.listen(24122)
    IOLoop.instance().start()