# -*- coding: utf-8 -*-
import time, json, re, os
import requests
from funtion.parse import Parse
from datetime import datetime
from funtion.funtions import months
requests.packages.urllib3.disable_warnings()



class CMCC():

    def __init__(self, account=None, proxy=None):

        self.account = account
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
            "Referer": "https://uac.10010.com/portal/homeLoginNew",
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Origin": "http://iservice.10010.com"
        }
        self.today = time.strftime("%Y%m%d")
        if not os.path.exists('./jsonFilesTmpBak/%s/' % self.today):
            os.makedirs('./jsonFilesTmpBak/%s/' % self.today)
        self.proxy = {'http': proxy,'https': proxy} if proxy else None


    # 发送验证码
    def send_code(self,times=1,timeout=5):

        result = dict(title='发送验证码', phoneNum=self.account,proxy=self.proxy)
        s = requests.session()
        now = str(int(round(time.time() * 1000)))

        url = 'https://uac.10010.com/portal/Service/CheckNeedVerify?userName={}&pwdType=01&_={}'.format(self.account, now)
        s.get(url, headers=self.headers,proxies=self.proxy,timeout=timeout,verify=False)
        
        sendSMS_url = "https://uac.10010.com/portal/Service/SendCkMSG?req_time={}&mobile={}&_={}".format(now, self.account, now)
        sendSMS_res = s.get(sendSMS_url, proxies=self.proxy, headers=self.headers,timeout=timeout, verify=False)
        returnContent = sendSMS_res.content.decode()
        resultCode = re.findall("resultCode:\"(.*?)\",", returnContent)[0] if re.findall("resultCode:\"(.*?)\",", returnContent) else None
        if resultCode == '0000': result['resultCode'], result['msg'] =  resultCode, '发送成功'
        if resultCode and resultCode != '0000': 
            result['resultCode'] =  resultCode
            result['msg'] = re.findall("msg:\'(.*?)\',", returnContent)[0] if re.findall("msg:\'(.*?)\',", returnContent) else '未知错误类型(%s)' % returnContent
        elif not resultCode:
            result['resultCode'] =  '6'
            result['msg'] = '未知错误类型(%s)' % returnContent
        
        if result['resultCode'] == '7098': result['msg'] = '当日随机码发送次数已达上限，请明日再试！'

        return json.dumps(result)


    # 登录并获取cookies
    def loginAndGetCookise(self, password, smsCode):
        result = dict(title='登录',resultCode='',cookies={},msg='',phoneNum=self.account)
        # result = dict(title='登录',resultCode='0000',cookies={},msg='成功',phoneNum=self.account)
        cookies = {}
        s = requests.session()

        now = str(int(round(time.time() * 1000)))

        ckNeedCode_url = 'https://uac.10010.com/portal/Service/CheckNeedVerify?%s'
        ps = dict(userName=self.account, pwdType='01', _=now)
        print(ps)
        ps_str = '&'.join([i+'='+ps[i] for i in ps])
        ckNeedCode_res = s.get(ckNeedCode_url % ps_str, proxies=self.proxy, headers=self.headers,verify=False)
        cookies = {**cookies, **ckNeedCode_res.cookies.get_dict()}
        # print(ckNeedCode_res.content.decode())
        # print(cookies)


        login_url = 'https://uac.10010.com/portal/Service/MallLogin?%s'
        params = dict(
            req_time=now, redirectURL='http://www.10010.com', userName=self.account,
            password=password, pwdType='01', productType='01', redirectType='03',
            rememberMe='1',verifyCKCode=smsCode, _=now
        )
        params_str = '&'.join([i+'='+params[i] for i in params])
        login_res = s.get(login_url % params_str, proxies=self.proxy, headers=self.headers, cookies=cookies,verify=False)
        cookies = {**cookies, **login_res.cookies.get_dict()}
        # print(login_res.content.decode())

        # 验证提交登录数据
        returnContent = login_res.content.decode()
        resultCode = re.findall("resultCode:\"(.*?)\",", returnContent)[0] if re.findall("resultCode:\"(.*?)\",", returnContent) else None
        if resultCode == '0000': result['resultCode'], result['msg'] =  resultCode, '登录成功'
        if resultCode and resultCode != '0000': 
            result['resultCode'] =  resultCode
            result['msg'] = re.findall("msg:\'(.*?)\',", returnContent)[0] if re.findall("msg:\'(.*?)\',", returnContent) else '未知错误类型(%s)' % returnContent
        elif not resultCode:
            result['resultCode'] =  '6'
            result['msg'] = '未知错误类型(%s)' % returnContent


        cklogin_url = 'http://iservice.10010.com/e3/static/check/checklogin/?_=%s' % str(int(round(time.time() * 1000)))
        cklogin_res = s.post(cklogin_url,proxies=self.proxy, headers=self.headers, cookies=cookies,verify=False)
        cookies = {**cookies, **cklogin_res.cookies.get_dict()}
        # print(cklogin_res.content.decode())

        loginContent = cklogin_res.content.decode()
        loginStatus = json.loads(loginContent)['isLogin']
        # if resultCode == '0000': result['resultCode'], result['msg'] =  resultCode, '发送成功'
        
        

        return cookies, result, loginStatus


    # 获取历史账单
    def getBill(self, cookies, start_date, end_date):

        now = str(int(round(time.time() * 1000)))
        info = dict(billInfos=[])
        print(start_date, end_date)
        for month in months(start_date, end_date):
            print(month)
            try:
                url = 'http://iservice.10010.com/e3/static/wohistory/bill?dat=%s&_=%s'
                print(url % (month, now))
                res = requests.get(url % (month, now), proxies=self.proxy, headers=self.headers,cookies=cookies,data={'chargetype':''} ,verify=False)
                print('获取%s历史账单' % month)
                bill_info = Parse(res.content.decode()).parse_cmcc()
                if bill_info:
                    # print(bill_info)
                    info['billInfos'].append(bill_info)
            except:
                pass
        info['billMonthCount'] = str(len(info['billInfos']))
        return info


    # 获取套餐信息
    def getPackageData(self, cookies):
        
        now = str(int(round(time.time() * 1000)))
        self.headers['Referer'] = "https://iservice.10010.com/e4/skip.html?menuCode=000100040001"
        getPackageData_url = "https://iservice.10010.com/e3/static/query/newQueryLeavePackageData?_=%s&accessURL=https://iservice.10010.com/e4/skip.html?menuCode=000100040001" % now
        getPackageData_res = requests.post(getPackageData_url, proxies=self.proxy, headers=self.headers, cookies=cookies ,verify=False)
        data = getPackageData_res.content.decode()
        with open("./jsonFilesTmpBak/%s/%s_CMCC_PackageDataSource_%s" % (self.today, self.account, time.strftime("%H%M%S")), 'w') as f:
            f.write(data)
        packageInfo = Parse(data).parseFlowCmcc()
        if not len(packageInfo['flowInfo']):
            try:
                familyTypeUrl = "https://iservice.10010.com/e3/static/wohome/combospare?_=%s" % now
                familyTypeRes = requests.post(familyTypeUrl, proxies=self.proxy, headers=self.headers, cookies=cookies ,verify=False)
                familyTypeData = familyTypeRes.content.decode()
                with open("./jsonFilesTmpBak/%s/%s_CMCC_PackageDataSource_%s" % (self.today, self.account, time.strftime("%H%M%S")), 'w') as f:
                    f.write(familyTypeData)
                packageInfo['flowInfo'] = Parse(familyTypeData).parseFamilyTypeFlowCmcc()
            except:
                pass


        productFee_url = "https://iservice.10010.com/e3/static/query/searchPerInfo/?_=%s" % now
        productFee_res = requests.post(productFee_url, proxies=self.proxy, headers=self.headers, cookies=cookies)
        
        info = json.loads(productFee_res.content.decode())['packageInfo']['productInfo'][0]
        packageInfo['productFee'] = info['productFee'] if 'productFee' in info else '以套餐资费为准'
        
        return packageInfo


    # 获取增值业务信息
    def getValueAdded(self, cookies, timeQuantums):

        now = str(int(round(time.time() * 1000)))
        s = requests.session()
        self.headers['Referer'] = 'https://iservice.10010.com/e4/query/basic/call_value_added.html?menuId=000100030003&TipsCode=10005'
        callValueAdded_url = 'https://iservice.10010.com/e3/static/query/callValueAdded?_=%s&accessURL=https://iservice.10010.com/e4/query/basic/callValueAdded_iframe.html&menuid=000100030003' % now

        valueAddedInfos = []
        totalData = ""
        for (timeQuantumH, timeQuantumT) in timeQuantums:
            res3 = s.post(
                callValueAdded_url, proxies=self.proxy, 
                headers=self.headers, cookies=cookies, 
                data={
                    'pageNo':'1','pageSize':'20',
                    'beginDate':timeQuantumH,'endDate':timeQuantumT
                    },
                verify=False)
            data = res3.content.decode()
            totalData += data + '\n\n\n'
            valueAddedInfo = Parse(data).parseAddValueCmcc()
            valueAddedInfos.append(valueAddedInfo)
        with open("./jsonFilesTmpBak/%s/%s_CMCC_ValueAddedDataSource_%s" % (self.today, self.account, time.strftime("%H%M%S")), 'w') as f:
            f.write(data)
        
        return valueAddedInfos


    def run(self, password, smsCode, start_date, end_date, timeQuantums):
        cookies, loginResult, loginStatus = self.loginAndGetCookise(password, smsCode)
        # with open('./new_json/cookies_%s.json' % self.account, 'w') as f:
        #     f.write(json.dumps(cookies))


        result = loginResult
        result['cookies'] = cookies
        result['info'] = {}
        if loginResult['resultCode'] == '0000' and loginStatus:
            result['info']['billInfo'] = self.getBill(cookies, start_date, end_date)
            result['info']['packageInfo'] = self.getPackageData(cookies)
            result['info']['valueAddedInfo'] = self.getValueAdded(cookies, timeQuantums)

        return json.dumps(result)


    

