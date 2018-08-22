#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Xuchao
# @time: 2018/8/21 下午 07:57

import requests
from requests.exceptions import RequestException
import urllib
import json
from bs4 import BeautifulSoup
import re
from config import *   #引入config文件中所有变量
import pymongo
import os
from hashlib import md5
from multiprocessing import Pool
from baidu_face_ai import *



client = pymongo.MongoClient(MONGO_URL,connect=False)  #每个进程创建一个链接
db = client[MONGO_DB]



def get_page_index(offset):
    data = {
        'offset':offset,
        'format': 'json',
        'keyword': '街拍',
        'autoload': 'true',
        'count': '20',
        'cur_tab': '1',
        'from': 'search_tab'
    }
    url = 'https://www.toutiao.com/search_content/?'+urllib.parse.urlencode(data)
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        else:
            return None
    except RequestException:
        print('request error')
        return None

def parse_page_json(html):
    data = json.loads(html)  #字符串转换成json对象
    # print(data.keys())
    for item in data.get('data'):
        if  item.get('article_url') != None:
            yield item.get('article_url')

def get_image_page(url):
    proxies = {
        'http': 'http://127.0.0.1:8080',
        'https': 'http://127.0.0.1:8080',
    }
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/17.17134'
    }
    try:
        response = requests.get(url,headers=headers)  #带上headers否则返回为空
        if response.status_code == 200:
            return response.text
        else:
            return None
    except RequestException:
        print('request error')
        return None

def parse_image_page(html):

    soup = BeautifulSoup(html,'lxml')
    # print(type(soup.select('title')[0]))
    # print(soup.select('title'))
    if soup.select('title'):
        title = soup.select('title')[0].get_text()   #list带上索引变为<class 'bs4.element.Tag'>调用get_text()方法
        print(title)
        images_pattern = re.compile('gallery: JSON.parse\\((.*?)\\)',re.S)
        # 分两步看
        # 首先字符串中的\\被编译器解释为\
        # 然后作为正则表达式\(又被正则表达式引擎解释为(
        # 如果在字符串里只写\(的话，第一步就被直接解释为(，所以正则表达式中需要转义的特殊字符一般都有两个\\
        # print(html)
        image_url = re.search(images_pattern,html)
        # print(type(image_url))
        # print(image_url)
        # print(image_url.group(1))
        if image_url:
            data = json.loads(image_url.group(1))
            data = json.loads(data)  #data是字典类型
            if 'sub_images' in data.keys():
                url = [item['url'] for item in data['sub_images']]
                for url1 in url:request_iamges(url1)

                    # print(item)
                return {
                    'title':title,
                    'url': url   #url以列表形式返回
                }

def save_to_mongo(result):
    if db[MONGO_TABLE].insert(result):
        # print('存储到MongoDB 成功',result)
        return True
    return False


def request_iamges(url): #请求图片函数
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
    }
    try:
        response = requests.get(url,headers=headers)  #带上headers否则返回为空
        if response.status_code == 200:
            print('正在下载'+url)
            data = get_face_des(url)
            if data != None:
                score = data['beauty']
                print(score)
                save_images(response.content,score)
        else:
            return None
    except RequestException:  #所有异常的基类
        print('request image error')
        return None

def save_images(content,score):   #图片保存到本地

    file_path = '{0}/images/{1}~{2}/{3}.{4}'.format(os.getcwd(),str(int(score/10)*10),str(int(score/10)*10+10),md5(content).hexdigest(),'jpg') #返回摘要，作为十六进制数据字符串值
    if not os.path.exists(file_path):
        with open(file_path,'wb') as f:
            f.write(content)
            num = get_images_num('images')
            print(file_path+'  保存成功     总图片数量：'+str(num))
            f.close()

def get_images_num(path):
    count = 0
    for i in range(10):
        list = os.listdir('./images/'+str(i*10)+'~'+str(i*10+10))
        count += len(list)
    return count

def main(offset):
    html = get_page_index(offset)
    if html:
        for url in parse_page_json(html):
            print(url)
            if url:
                html = get_image_page(url)
                # print(html)
                if html:
                    images = parse_image_page(html)
                    if images:
                        save_to_mongo(images)

if __name__ == '__main__':
    # group = [i*20 for i in range(30)]
    # pool = Pool()
    # pool.map(main,group)
    for i in range(1000):
        main(str(i*20))
    # html = get_image_page('http://baidu.com')
    # print(html)
