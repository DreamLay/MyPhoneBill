# -*- coding: utf-8 -*-
import sys, json, time, os, random, string, traceback, logging
from flask import Flask, request
from china_mobile import DriverForChinaMobile, ChinaMobile
from CMCC_main import CMCC
from datetime import timedelta
from datetime import datetime
from china_mobile import last_month_date
from redis import *
# from funtion import Proxy
from funtion.funtions import Proxy


app = Flask(__name__,static_url_path='')


logger = logging.getLogger()
logger.setLevel(logging.INFO)
fh = logging.FileHandler('./BillServer.log', mode='a+')
fh.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(levelname)s: *thread-> %(thread)d* %(module)s.%(funcName)s[line:%(lineno)d]: %(message)s")
fh.setFormatter(formatter)
logger.addHandler(fh)


# 发送验证码
@app.route("/send_smscode", methods=['POST'])
def send_smscode():

    proxy = Proxy(pool).choiceProxy()
    username = request.json["username"]
    operator = request.json["operator"]
    
    # 判断运营商
    try:
        if operator == "0":
            # result = ChinaMobile(username).send_code()
            logger.info("移动号码[%s]发起验证码请求" % username)
            result = DriverForChinaMobile(username, proxy).send_code()
            result['operator'] = operator
            result['proxy'] = proxy
            
            result_json = json.dumps(result)
            logger.info(result_json)
            return result_json
        elif operator == "1":
            logger.info("联通号码[%s]发起验证码请求" % username)
            result = CMCC(username, proxy).send_code()
            logger.info(result)
            return result
    except:
        logger.error(traceback.format_exc())
        logger.error(json.dumps(request.json))
        logger.error(proxy)
        return json.dumps(dict(
            title='发送验证码',resultCode='8',msg='未知错误',phoneNum=username,proxy=proxy
        ))


# 登录
@app.route("/login", methods=['POST'])
def login():

    username = request.json["username"]
    sms_code = request.json["smsCode"]
    operator = request.json["operator"]
    billStartDate = request.json["billStartDate"]
    billEndDate = request.json["billEndDate"]

    # 新参数
    proxy = request.json["proxy"]
    valueAddedDates = request.json['valueAddedDates']

    try:
        if operator == "0":
            logger.info("移动号码[%s]发起登录请求" % username)
            result = DriverForChinaMobile(username, proxy).login(sms_code)

            if result['resultCode'] == '0000':
                result['info'] = {}
                result['info']['billInfo'], result['info']['valueAddedInfo'] = ChinaMobile(username, proxy).get_bill(result['cookies'],billStartDate,billEndDate)
                result['info']['packageInfo'] = ChinaMobile(username, proxy).getPlanbal(result['cookies'])
                # result['plan_info'] = json.loads(plan_info)
                # result['person_info'] = json.loads(person_info)
            result_json = json.dumps(result)
            logger.info(result_json)
            return result_json

        elif operator == "1":
            logger.info("联通号码[%s]发起登录请求" % username)
            password = request.json["password"]
            result = CMCC(account=username,proxy=proxy).run(password, sms_code, billStartDate, billEndDate, valueAddedDates)
            logger.info(result)
            return result
    except:
        logger.error(traceback.format_exc())
        logger.error(json.dumps(request.json))
        logger.error(proxy)
        return json.dumps(dict(
            title='登录',resultCode='8999', coookies={}, info={}, msg='未知错误',phoneNum=username
        ))


# http://localhost:5000/apidocs/index.html
if __name__ == '__main__':
    pool = ConnectionPool(host='127.0.0.1', port=6379)
    # app.run(host='127.0.0.1', port=8086,threaded=True, ssl_context='adhoc')
    app.run(host='127.0.0.1', port=8086, threaded=True,debug=True)
