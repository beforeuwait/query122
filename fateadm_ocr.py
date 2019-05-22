# coding=utf-8

"""
author = wangjiawei
date = 2019.01.02

该模块用作fateadm打码平台

承担3个角色：

    1. 请求ocr

    2. 错误退款

    3. 查询余额，并提醒
"""

import os
import time
import json
import logging
import hashlib
import requests
from copy import deepcopy


# logging模块

logger = logging.getLogger(name='ocr')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(os.path.join(os.path.split(__file__)[0], './ocr_log.log'))
fmt = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(fmt)
logger.addHandler(handler)

# 账号info
# 测试账号
# 免费次数已使用完

pid = 'xxx'
passwd = 'xxxxx'

# 请求信息
# ocr地址
url_ocr = 'http://pred.fateadm.com/api/capreg'

# 退费地址
url_cancle = 'http://pred.fateadm.com/api/capjust'

# 余额查询地址
url_custval = 'http://pred.fateadm.com/api/custval'

# 参数信息
# ocr参数
payloads_ocr = {
    'user_id': '',
    'timestamp': '',
    'sign': '',
    'app_id': '',
    'asign': '',
    'predict_type': '',
    'up_type': 'mt',
}

# 退费参数
payloads_cancle = {
    'user_id': '',
    'timestamp': '',
    'sign': '',
    'request_id': ''
}

# 余额参数
payloads_custval = {
    'user_id': '',
    'timestamp': '',
    'sign': ''
}


def CalcSign(pd_id, passwd, timestamp):
    """sign加密过程"""
    md5 = hashlib.md5()
    md5.update((timestamp + passwd).encode())
    sign = md5.hexdigest()
    md5 = hashlib.md5()
    md5.update((pd_id + timestamp + sign).encode())
    sign = md5.hexdigest()
    return sign


def do_ocr(img_data) -> str:
    """执行ocr"""
    data = deepcopy(payloads_ocr)
    data.update({'user_id': pid,
                 'timestamp': int(time.time()),
                 'sign': CalcSign(pid, passwd, str(int(time.time()))),
                 'predict_type': '30400',
                 })
    # 这里需要一个验证一旦图片失效
    # 用Image去打开，能打开就是图片，不能打开就不是图片
    res = requests.post(url=url_ocr, data=data, files={'img_data': img_data})

    return res.content.decode('utf-8')


def do_cancle(RequestId) -> None:
    """执行退款"""
    data = deepcopy(payloads_cancle)
    data.update({
        'user_id': pid,
        'timestamp': int(time.time()),
        'sign': CalcSign(pid, passwd, str(int(time.time()))),
        'RequestId': RequestId
        })
    requests.post(url=url_cancle, data=data)
    logger.info('执行退款 id:\t{0}'.format(RequestId))


def do_custval() -> None:
    """查询余额，自动执行，每1小时查询一次
    当余额低于 10000 时候，报警
    """
    data = deepcopy(payloads_custval)
    data.update({
        'user_id': pid,
        'timestamp': int(time.time()),
        'sign': CalcSign(pid, passwd, str(int(time.time())))
        })
    res = requests.post(url=url_custval, data=data)
    cust_val = json.loads(json.loads(res.content.decode('utf8')).get('RspData')).get('cust_val')
    # 当cust_val 高于 10000是安全的
    if int(cust_val) > 10000:
        logger.debug('当前余额:\t{0}'.format(cust_val))
    else:
        logger.warning('当前余额不足 10000，请充值，剩余额度:\t{0}'.format(cust_val))


def executor() -> None:
    """每一小时执行一次余额查询"""
    while True:
        st = time.time()
        do_custval()
        ed = time.time()
        cost = ed-st
        time.sleep(3600 - cost)


if __name__ == '__main__':
    executor()