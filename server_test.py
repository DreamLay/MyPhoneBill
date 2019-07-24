# -*- coding: utf-8 -*-
import sys, json, time, os, random, string, requests, traceback, logging
from flask import Flask, request, jsonify, session
from china_mobile import DriverForChinaMobile, ChinaMobile
from CMCC_main import CMCC
from datetime import timedelta
from datetime import datetime
from china_mobile import last_month_date
from redis import *
from funtion.funtions import Proxy
username = '13428278874'
# username = input("手机号：")
password = input("密码：")
operator = "0"


def send_smscode(pool=None):

    # tmp = Proxy(pool).choiceProxy()

    # proxy = tmp if pool else None
    # print(proxy)
    # proxy = None
    # 判断运营商
    proxy = input('代理1: ')
    # proxy = None
    try:
        if operator == "0":
            # result = ChinaMobile(username).send_code()
            
            result = DriverForChinaMobile(username, proxy).send_code()
            result['operator'] = operator
            return json.dumps(result)
        elif operator == "1":
            # password = request.json["password"]
            print(proxy)
            result = CMCC(username, proxy).send_code()
            result['operator'] = operator
            return json.dumps(result)
    except:
        return json.dumps(dict(
            title='发送验证码',resultCode='8',msg='未知错误',phoneNum=username
        ))



# 登录
def login():

   

    # sms_code = '526399'
    # start_date = request.json["startDate"]
    # end_date = request.json["endDate"]
    # proxy = Proxy(pool).choiceProxy() if pool else None
    # try:
        proxy = input('代理2: ')
        # proxy = None
        # proxy = None
        sms_code = input("验证码：")
        if operator == "0":
            dc = DriverForChinaMobile(username, proxy)
            # sms_code = input("验证码：")
            result = dc.login(sms_code)
            
            print(result['cookies'])
            if result['resultCode'] == '0000':
                result['info'] = {}
                result['info']['billInfo'],result['info']['valueAddedInfo'] = ChinaMobile(username, proxy).get_bill(result['cookies'],'201903','201904')
                packageInfo = ChinaMobile(username, proxy).getPlanbal(result['cookies'])
                result['info']['packageInfo'] = packageInfo

            with open('./json_data/移动所有数据（蔡玉真13824559862）版.json', 'w') as f:
                f.write(json.dumps(result))

            return json.dumps(result)
        elif operator == "1":

            valueAddedDates = [
            ('2019-02-01','2019-02-28'),
            ('2019-03-01','2019-03-31'),('2019-04-01','2019-04-30'),
            ('2019-05-01','2019-05-31'),('2019-06-01','2019-06-30'),
            # ('2019-07-01','2019-07-31'),('2019-08-01','2019-08-31'),
            # ('2019-09-01','2019-09-31'),('2019-10-01','2019-10-31'),
            # ('2019-11-01','2019-11-31'),('2019-12-01','2019-12-31')
        ]
            result = CMCC(account=username,proxy=proxy).run(
                    password, sms_code, '201901', '201906', valueAddedDates
                )
            
            with open('./json_data/联通所有数据新版15622282346v1.json', 'w') as f:
                f.write(json.dumps(result))
            return result
    # except:
    #     return json.dumps(dict(
    #         title='登录',resultCode='8999', coookies={}, info={}, msg='未知错误',phoneNum=username
    #     ))



if __name__ == '__main__':
    # pool = ConnectionPool(host='127.0.0.1', port=6379)
    send_smscode()
    login()
    # info = ChinaMobile(username).get_bill(tmpCookies,'201901','201904')
    # info = CMCC(username).get_bill(tmpCookies,'201902','201905')
    # print(info)
    # CMCC(username).getValueAdded(tmpCookies)
    # CMCC(username).getPackageDate(tmpCookies)
    # print(info)