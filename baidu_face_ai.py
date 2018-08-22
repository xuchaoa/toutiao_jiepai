#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Xuchao
# @time: 2018/8/22 下午 03:38


import urllib, sys
import ssl
import requests
import json
from requests import RequestException

def get_access_token():   #根据AK和SK获取吧access_token
    # client_id 为官网获取的AK， client_secret 为官网获取的SK
    host = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=VRpEYoAwqjKRjSr5k2YAI71z&client_secret=zyBShGiKgZyqLmewA4ym1vPNNySjupEg'

    headers = {
        'Content-Type':'application/json; charset=UTF-8'
    }
    response = requests.post(host,headers=headers)

    content = response.text
    data = json.loads(content)
    if 'access_token' in data.keys():
        return data['access_token']
    elif 'error' in data.keys():
        print('请求token失败 ，error_description：'+data['error_description'])
        return None

def get_face_des(image_url):
    request_url = "https://aip.baidubce.com/rest/2.0/face/v3/detect"
    params = {
        'image': image_url,
        'image_type':'URL',
        'face_field':'age,beauty,gender'  #返回年龄，性别，颜值
                 }
    access_token = get_access_token()
    request_url = request_url + "?access_token=" + access_token
    headers = {
        'Content-Type': 'application/json'
    }
    response = None
    try:
        response = requests.post(url=request_url,headers=headers,data=params)
    except RequestException:
        print('request error')
    # print(response.text)
    # print(type(response.text))  #返回类型为str
    face_data = json.loads(response.text)
    # print(face_data.keys())
    try:
        # print(face_data['result']['face_list'][0]['beauty'])
        if face_data['result']['face_list'][0]['beauty'] != None:
            # print('yes')
            return  {
                'error_code':face_data['error_code'],
                'face_num':face_data['result']['face_num'],
                'age':face_data['result']['face_list'][0]['age'],
                'gender':face_data['result']['face_list'][0]['gender']['type'],
                'beauty':face_data['result']['face_list'][0]['beauty']
            }
        else:
            return None
    except BaseException:
        print('beauty is None')


# def main():
#     dic = get_face_des('https://ss0.bdstatic.com/94oJfD_bAAcT8t7mm9GUKT-xh_/timg?image&quality=100&size=b4000_4000&sec=1534924561&di=5d510a97113ce986652adc7e24e553a3&src=http://img3.iyiou.com/Picture/2017-03-08/58bf72b6cc970.jpg')
#     print(dic)




