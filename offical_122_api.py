# coding=utf-8

import os
import re
import json
import time
import config
import execjs
from copy import deepcopy
from HTTP.HttpApi import HttpApi
from HTTP.utils import MethodCheckError
from fateadm_ocr import do_ocr
from fateadm_ocr import do_cancle
from deal_sx_js import receive_html_and_deal

# type

_payloads = dict
_license = tuple
_response = tuple
_cookie = dict
_api = dict
_ocr = tuple
_html = str

"""
    author: wangjiawei
    date: 2018-12-20
    
    各省的接口
    验证码
        测试版，验证码，改为手动
    
    安徽省的官网，比较事儿逼
    1. js算token， 随后主动取消
    2. 现在的情况是， 反一个html，调dom加载验证码
    
    2019-01-02: 
        有时间来搞122的验证码了
        妈蛋！ 这个svm没法弄，需要上cnn
        
        引入打码平台
    
    2019-01-04:
        安徽这个事逼省搞定，根据返回的 html，访问其中的url便可通过
        
        新增加山西这个事逼儿省
        对token验证的很厉害
"""


class Http(HttpApi):
    """需要重构某方法"""

    def user_define_request(self, **kwargs) -> _response:
        """这个方法的意义在于用户自己去设计请求过程
        一般登录啊
        绕过js啊
        。。。
        都这这里自己定义
        """
        method = kwargs.get('method')
        if method not in ['get', 'GET', 'post', 'POST']:
            raise MethodCheckError
        url = kwargs.get('url')
        headers = kwargs.get('headers')
        cookies = kwargs.get('cookies')
        params = kwargs.get('params')
        payloads = kwargs.get('payloads')
        html, statuscode = self.dr.do_request(method=method,
                                              url=url,
                                              headers=headers,
                                              cookies=cookies,
                                              params=params,
                                              payloads=payloads,
                                              redirect=True)
        return (html, statuscode)

    def get_seesion_cookie_wzwsconfirm(self):
        return self.dr.session.cookies.get('wzwsconfirm')


def receive_form_data_from_api(form_data) -> _api:
    """从http server获取参数
    """
    retry = 3
    api = deepcopy(config.api_params)
    license_data = license_parser(form_data)
    # # 准备获取验证码
    http = Http()

    # 访问主页
    # 2019-01-03 不请求主页
    if license_data[-1] == 'sx':
        visit_home_page(http, license_data[-1])

    while retry > 0:
        ocr_result = get_captcha(http, license_data[-1])
        if not ocr_result[2]:
            captcha = ocr_result[0]
            result = get_violation_data(http, license_data, captcha, form_data)
            api = deal_response(result.decode('utf-8'), api)
            # 对code进行处理
            # code 499是验证码错误
            # code 500是请求参数错误
            if api.get('code') == 499:
                do_cancle(ocr_result[1])
                retry -= 1
                time.sleep(0.1)
                continue
            break
        time.sleep(0.1)
        retry -= 1

    return api

def deal_response(js_txt, api_params) -> _api:
    """处理数据
    code: 200   成功
    code: 499   验证码错误
    code: 500   参数错误

    wz_info = {
        'state': '200,499,500',
        'data': {xxxxxxx}
        'msg': '',
    }
    """
    api = deepcopy(api_params)
    js_dict = json.loads(js_txt)
    code = js_dict.get('code')
    api.update({'code': code,
                'msg': js_dict.get('message')})
    if code == 200:
        data = js_dict.get('data')
        api['data']['total'] = data.get('content').get('zs')
        api['data']['ws'] = data.get('content').get('ws')
        api['data']['bs'] = data.get('content').get('bs')
        api['data']['bd'] = data.get('content').get('bd')

    return api

def visit_home_page(http, prov) -> None:
    """访问主页，拿到cookie
    不返回任何
    """
    req_prms = request_params_switcher('home_page', prov)
    req_prms[1].update({'Host': '{0}.122.gov.cn'.format(prov),
                        'Referer': 'http://{0}.122.gov.cn/'.format(prov)})
    http.user_define_request(url=req_prms[0], headers=req_prms[1], method='get')


def deal_code_521(js_text) -> _cookie:
    """目前只有安徽省的官网需要针对 521 进行反爬虫"""
    js_ctx = re.findall('<script>(.*?)</script>', js_text.decode('utf8'))[0]
    func_return = js_ctx.replace('eval(y', 'return(y')
    content = execjs.compile(func_return)
    evaled_func = content.call('f')
    # 然后找出运算那段code
    cookie_js = re.findall('document.cookie(.*?)\+\';Expires', evaled_func)[0]
    js_file = 'cookie{0};console.log(cookie);phantom.exit(0)'.format(cookie_js)
    # 保存js_file
    file_name = os.path.abspath('./js/js_{0}.js'.format(int(time.time())))
    with open(file_name, 'w', encoding='utf8') as f:
        f.write(js_file)
    # 执行命令
    cmd = 'phantomjs {0}'.format(file_name)
    result = os.popen(cmd)
    # 拿到cookie
    cookie_ctx = result.read()
    # 将cookie转化为dict
    return {'__jsl_clearance': cookie_ctx.strip().split('=')[1]}


def deal_js(html, http):
    """针对安徽省， 这个事逼省！
    """
    """
    # 这是旧的处理思路
    # 首先保存html
    js_code = re.findall('javascript">(.*?)</script>', html, re.S)[0]
    file_name = os.path.abspath('./js/{0}.js'.format(int(time.time())))
    with open(file_name, 'w', encoding='utf8') as f:
        f.write('{0};phantom.exit(0)'.format(js_code))
    cmd = 'phantomjs {0}'.format(file_name)
    os.popen(cmd)
    """

    # 2019-01-04 直接从html把captcha_url 拿出来请求
    new_url = re.findall('href="(.*?)"</script', html, re.S)[0]

    headers = deepcopy(config.headers_captcha)
    headers.update({'Host': '{0}.122.gov.cn'.format('ah'),
                        'Referer': 'http://{0}.122.gov.cn/views/inquiry.html'.format('ah')
                        })
    http.user_define_request(url=new_url, headers=headers, method='get')



def get_captcha(http, prov) -> _ocr:
    """请求验证码
    2019-01-02: 引入第三方打码平台
    """
    req_prms = request_params_switcher('captcha', prov)
    req_prms[1].update({'Host': '{0}.122.gov.cn'.format(prov),
                        'Referer': 'http://{0}.122.gov.cn/views/inquiry.html'.format(prov)
                        })
    # 这里需要一个重试过程, 暂时重试次数为3
    retry = 3
    cookie = None
    result = None
    refresh = False
    rsp_data = ''
    request_id = ''

    while retry > 0:
        result = http.user_define_request(url=req_prms[0], headers=req_prms[1], method='get') if cookie is None \
            else http.user_define_request(url=req_prms[0], headers=req_prms[1], cookies=cookie, method='get')
        # 开始处理 code 521
        if result[1] == 521:
            # 需要重新开始
            cookie = deal_code_521(result[0])
        elif prov == 'sx' and cookie is None:
            # cookie = {'wzwstemplate': 'MQ==', 'wzwschallenge': 'V1pXU19DT05GSVJNX1BSRUZJWF9MQUJFTDExMTY1Nzc=', 'wzwsconfirm': 'f47c4ec868c0b3b6c80d5f30ea998d64'}
            cookie = receive_html_and_deal(result[0].decode('utf-8'))
            cookie.update({'wzwsconfirm': http.get_seesion_cookie_wzwsconfirm()})
            # 情况cookie
            http.dr.sh.discard_cookie_headers_params('cookies')
        else:
            break
        retry -= 1

    # 这里对验证码进行验证

    if result is not None and b'script' not in result[0]:
        img_data = result[0]
        js_dict = json.loads(do_ocr(img_data))
        request_id = js_dict.get('RequestId')
        rsp_data = json.loads(js_dict.get('RspData')).get('result')
    elif b'script' in result[0]:
        if prov == 'ah':
            deal_js(result[0].decode('utf-8'), http)
        # 然后重试
        refresh = True

    return (rsp_data, request_id, refresh)


def get_violation_data(http, license, captcha, form_data) -> _html:
    """
    1. 生成payloads
    2. 请求接口
    """
    # 拿到发动机后六位
    eng_6_last = form_data.get('engineNo')[-6::]
    req_prms = request_params_switcher('vio_page', license[-1])
    req_prms[1].update({'Host': '{0}.122.gov.cn'.format(license[-1]),
                        'Referer': 'http://{0}.122.gov.cn/views/inquiry.html'.format(license[-1])
                        })
    payloads = deepcopy(config.payloads)
    payloads.update({'hphm1b': license[1],
                     'hphm': license[0],
                     'fdjh': eng_6_last,
                     'captcha': captcha})
    result = http.user_define_request(url=req_prms[0], headers=req_prms[1], payloads=payloads, method='post')
    return result[0]


def request_params_switcher(choice, prov) -> object:
    """组装url，headers"""
    switcher = {
        'home_page': [deepcopy(config.url_query).format(prov), deepcopy(config.headers)],
        'captcha': [deepcopy(config.url_captcha).format(prov, int(time.time() * 1000)),
                    deepcopy(config.headers_captcha)],
        'vio_page': [deepcopy(config.url_violation).format(prov), deepcopy(config.headers_violation)]
    }
    return switcher.get(choice)


def license_parser(form_data) -> _license:
    """创建请求参数
    调研发现
    只需要车牌+发动机后六位即可
    返回 (车牌， 车牌号， 省份，对于code)

    2019-1-2: 针对 江苏、浙江的细分处理
    """
    prov_ids = config.car_prov_ids
    # 首先拿到prov_code
    car_no = form_data.get('carNo')
    prov_code = re.findall(prov_ids, car_no)[0]
    car_no2 = re.findall('[^{0}].*'.format(prov_ids), car_no)[0]
    if prov_code == '苏' or prov_code == '浙':
        # 需要额外处理
        city_code = car_no2[0]
        city = config.su if prov_code == '苏' else config.zhe
        prov = city.get(city_code)
    else:
        prov = config.no2prov.get(prov_code)
    return (car_no, car_no2, prov_code, prov)


if __name__ == '__main__':
    data = {
        'carNo': '晋A0001',
        'engineNo': '123456'
    }
    receive_form_data_from_api(data)