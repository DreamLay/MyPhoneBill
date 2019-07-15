# -*- coding: utf-8 -*-
import requests, json, time,re
from datetime import datetime
from selenium import webdriver
from http import cookiejar
# from parse import Parse
from funtion.parse import Parse
from redis import *
from selenium.webdriver.chrome.options import Options
from funtion.funtions import get_cookies, last_month_date
requests.packages.urllib3.disable_warnings()



# 浏览器驱动
class DriverForChinaMobile():

    def __init__(self, username, proxy=None):
        self.username = username
        chrome_options=Options()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('blink-settings=imagesEnabled=false')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--headless')
        if proxy:
            chrome_options.add_argument("--proxy-server=http://%s" % proxy)
            # print('登录:代理 http://%s' % proxy)
        self.driver = webdriver.Chrome(chrome_options=chrome_options)
        self.url = 'https://login.10086.cn/html/login/login.html?channelID=12002&backUrl=https://shop.10086.cn/i/'


    def send_code(self):
        result = dict(title='发送验证码',resultCode='0',cookies={},msg='成功',phoneNum=self.username)
        count = 0
        while count <= 50:
            try:
                self.driver.get(self.url)
                self.driver.find_element_by_id('sms_login_1').click()
                self.driver.find_element_by_id('sms_name').send_keys(self.username)
                self.driver.find_element_by_id('getSMSPwd1').click()
                break
            except:
                result['resultCode'] = '6'
                result['msg'] = '未能成功获取验证码链接'
                self.driver.quit()
                return result
            time.sleep(0.1)
            count += 1
        if not self.get_msg():
            result['resultCode'] = '6'
            result['msg'] = '请求失败'

        msg = self.driver.find_element_by_id('msmsendtips').text
        if '达到上限' in msg:
            result['resultCode'], result['msg'] = '2', msg
        self.driver.quit()
        return result

    def get_msg(self, times=1):
        # print('第{}次尝试'.format(times))
        if times >= 10:
            return 0
        try:
            self.driver.find_element_by_xpath("//button[@id='getSMSPwd1' and @disabled]")
            return 1
        except:
            time.sleep(1)
            self.get_msg(times=times+1)
        


    # 登录并获取cookies
    def login(self, code):
        result = dict(title='登录',resultCode='0000',cookies={},msg='登录成功',phoneNum=self.username)
        try:
            self.driver.get(self.url)
            self.driver.find_element_by_id('sms_login_1').click()
            self.driver.find_element_by_id('sms_name').send_keys(self.username)
            self.driver.find_element_by_id('sms_pwd_l').send_keys(code)
            self.driver.find_element_by_id('submit_bt').click()  
            count = 1
            while True:
                if count >= 50:
                    # 获取登录失败页面标志-------------------
                    msg = ''
                    try:
                        msg += self.driver.find_element_by_xpath("//div[@id='smspwd_err']").text
                        result['cookies'] = get_cookies(self.driver.get_cookies())
                        result['resultCode'] = '4444'
                        result['msg'] = msg
                    except:
                        pass
                    try:
                        msg += self.driver.find_element_by_xpath("//div[@id='smsphone_err']").text
                        result['cookies'] = get_cookies(self.driver.get_cookies())
                        result['resultCode'] = '4444'
                        result['msg'] = msg
                    except:
                        pass
                    if msg == "":
                        result['resultCode'], result['msg'] == '1111', '请求超时'
                    break
                time.sleep(0.1)


                # 获取登录成功后跳转页面标志-------------------
                try:
                    self.driver.find_element_by_id('charge_tel')
                    result['cookies'] = get_cookies(self.driver.get_cookies())
                    break
                except:              
                    pass
                count += 1

                
        except:
            result['cookies'] = get_cookies(self.driver.get_cookies())
            result['resultCode'], result['msg'] == '2222', '登录异常'
        
  
        self.driver.quit()
        return result




class ChinaMobile():

    def __init__(self, phone_num, proxy=None):
        self.phone_num = phone_num
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0.2 Safari/605.1.15",
            "Referer": "https://login.10086.cn/html/login/login.html?channelID=12002&backUrl=https://shop.10086.cn/i/",
        }
        self.proxy = {'http': proxy,'https': proxy} if proxy else None


    def get_bill(self, cookies, start_date, end_date):

        cookies['CmProvid'] = 'bj'

        now = str(int(round(time.time() * 1000)))
        date_end = last_month_date()
        date_start = last_month_date(12)
        
        self.headers['Referer'] = 'https://shop.10086.cn/i/?f=home&welcome={}'.format(now)
        bill_url = "https://shop.10086.cn/i/v1/fee/billinfo/{}?bgnMonth={}&endMonth={}&_={}"
        plan_url = 'https://shop.10086.cn/i/v1/busi/plan/{}?_={}'
        person_url = 'https://shop.10086.cn/i/v1/cust/info/{}?_={}'

        bill_res = requests.get(
            bill_url.format(self.phone_num, start_date, end_date, now),
            headers=self.headers, proxies=self.proxy, cookies=cookies,verify=False
            )
        # with open('./json_data/移动11个月账单.json', 'w') as f:
        #     f.write(bill_res.content.decode())
        
        data = bill_res.content.decode()
        info = Parse(data).parse_mobile()
        addValues = Parse(data).parseAddValueChina()
        info['billMonthCount'] = str(len(info['billInfos']))
        
        return info, addValues


    def getPlanbal(self, cookies):
        
        now = str(int(round(time.time() * 1000)))
        flow_url = 'https://shop.10086.cn/i/v1/fee/planbal/%s?_=%s' % (self.phone_num, now)
        package_url = 'https://shop.10086.cn/i/v1/cust/mergecust/%s?_=%s' % (self.phone_num, now)
        flow_res = requests.get(flow_url, proxies=self.proxy, headers=self.headers, cookies=cookies, verify=False)
        package_res = requests.get(package_url, proxies=self.proxy, headers=self.headers, cookies=cookies, verify=False)
        
        info = Parse(flow_res.content.decode()).parseFlowChina()
        
        try:
            data = package_res.content.decode()
            data_dict = json.loads(data)
            packageName = data_dict['data']['curPlanQryOut']['brandName'] + ' | ' + data_dict['data']['curPlanQryOut']['nextPlanName']
            info['packageName'] = packageName
        except: 
            pass
        info['productFee'] = ""
        return info