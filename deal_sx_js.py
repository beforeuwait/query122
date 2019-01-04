# coding=utf-8

"""
    针对山西这个事逼省份的反爬虫

    思路和安徽的极其相似，都是先解析拿到真实js
    然后执行真实js 写入cookie并刷新
    垃圾反爬虫 -_-!

    反反思路，先解析，拿到几个字段，然后放入事先安排好的模板里
"""

import os
import re
import time

def receive_html_and_deal(html):
    """拿到html，解析出 js"""
    js = re.findall('javascript">(.*?)</script>', html, re.S)[0].replace('return p', 'console.log(p)')
    # 拼凑js
    js_file = '{0};phantom.exit(0);'.format(js)
    js_path = os.path.abspath('./js/{0}.js'.format(int(time.time())))
    with open(js_path, 'w', encoding='utf-8') as f:
        f.write(js_file)

    cmd = 'phantomjs js_file.js'
    new_js = os.popen(cmd).read().replace('window.location=dynamicurl;', '').replace('document.cookie = cookieString',
                                                                                     'console.log(cookieString)')
    code = get_wzwschallenge_wzwschallengex(new_js)
    # 构造js
    demo_js = open('./js/demo_js.txt', 'r', encoding='utf-8').read()
    last_js_path = os.path.abspath('./js/{0}.js').format(int(time.time()))
    with open(last_js_path, 'w', encoding='utf-8') as f:
        f.write('var wzwschallenge = "RANDOMSTR{0}";\n'.format(code[0]))
        f.write('var wzwschallengex = "STRRANDOM{0}";\n'.format(code[1]))
        f.write(demo_js)

    cmd2 = 'phantomjs {0}'.format(last_js_path)
    result = os.popen(cmd2).read()
    # 开始解析2个结果
    wzwstemplate = re.findall('wzwstemplate=(.*?);', result, re.S)[0]
    wzwschallenge = re.findall('wzwschallenge=(.*?);', result, re.S)[0]
    cookie = {'wzwstemplate': wzwstemplate, 'wzwschallenge': wzwschallenge}
    return cookie


def get_wzwschallenge_wzwschallengex(js_ctx):
    wzwschallenge = re.findall('wzwschallenge="RANDOMSTR(\d{1,5})"', js_ctx)[0]
    wzwschallengex = re.findall('wzwschallengex="STRRANDOM(\d{1,5})"', js_ctx)[0]
    return (wzwschallenge,wzwschallengex)

# html = open('demo.html', 'r', encoding='utf-8').read()
#
# receive_html_and_deal(html)
