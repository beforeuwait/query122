# coding=utf-8

"""
    参数配置

    12-20 ：
        经过验证，只有 安徽一个省有cookie验证，可见该省可能是爬虫重灾区。
        策略：只有在 皖 字牌照才访问首页
"""


# 省份匹配


no2prov = {
    '渝': 'cq',
    '川': 'sc',
    '黑': 'hl',
    '京': 'bj',
    '津': 'tj',
    '冀': 'hb',
    '晋': 'sx',
    '蒙': 'nm',
    '辽': 'ln',
    '吉': 'jl',
    '沪': 'sh',
    '苏': 'nkg',
    '浙': 'hgh',
    '皖': 'ah',
    '闽': 'fj',
    '赣': 'jx',
    '鲁': 'sd',
    '豫': 'hn',
    '鄂': 'hb',
    '湘': 'hn',
    '粤': 'gd',
    '桂': 'gx',
    '琼': 'hn',
    '贵': 'gz',
    '云': 'yn',
    '藏': 'xz',
    '陕': 'sn',
    '甘': 'gs',
    '青': 'qh',
    '宁': 'nx',
    '新': 'xj'
}

car_prov_ids = '京|津|沪|川|渝|黑|辽|吉|冀|晋|蒙|新|贵|粤|桂|赣|鄂|湘|浙|苏|闽|琼|云|藏|青|鲁|甘|青|豫|皖|陕|宁'

# 针对江苏

su = {
    'A': 'ngk',
    'B': 'wux',
    'C': 'xuz',
    'D': 'czx',
    'E': 'szv',
    'F': 'ntg',
    'G': 'lyg',
    'H': 'has',
    'J': 'ynz',
    'K': 'yzo',
    'L': 'zhe',
    'M': 'tzs',
    'N': 'suq',
}

# 针对浙江
zhe = {
    'A': 'hgh',
    'B': 'ngb',
    'C': 'wnz',
    'F': 'jix',
    'E': 'hzh',
    'D': 'sgx',
    'G': 'jha',
    'H': 'quz',
    'L': 'zos',
    'J': 'tzz',
    'K': 'lss'
}



# 参数
# engine 数字代表后几位，全部 all， 不需要 null

payloads = {
    'hpzl': '02',
    'hphm1b': 'e85x6j',
    'hphm': '苏e85x6j',
    'fdjh': '005256',
    'captcha': 'riu8',
    'qm': 'wf',
    'page': '1'
}

# 查询页面

url_home = 'http://{0}.122.gov.cn'

url_query = 'http://{0}.122.gov.cn/views/inquiry.html'

url_captcha = 'http://{0}.122.gov.cn/captcha?nocache={1}'

url_violation = 'http://{0}.122.gov.cn/m/publicquery/vio'

# 请求头

import time
headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Host': 'xj.122.gov.cn',
    'Proxy-Connection': 'keep-alive',
    'Referer': 'http://xj.122.gov.cn/',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
}

headers_captcha = {
    'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Host': 'xj.122.gov.cn',
    'Proxy-Connection': 'keep-alive',
    'Referer': 'http://xj.122.gov.cn/views/inquiry.html',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'
}

headers_violation = {
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Content-Length': '80',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Host': 'sc.122.gov.cn',
    'Origin': 'http://sc.122.gov.cn',
    'Proxy-Connection': 'keep-alive',
    'Referer': 'http://sc.122.gov.cn/views/inquiry.html',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest'
}


# 接口参数

api_params = {
    'code': 0,
    'data': {
        'total': '',
        'bs': '',
        'bd': '',
        'ws': ''
    },
    'msg': ''
}