from datetime import datetime
from datetime import timedelta
from redis import Redis
import time


# 代理选择器
class Proxy():
    def __init__(self, pool):
        self.pool = pool


    def choiceProxy(self):

        r = Redis(connection_pool=self.pool)
        # r.mset({'172.18.6.199:7653': 0, '172.18.6.201:7653': 0, '172.18.6.196:7653': 0})
        proxys = ['172.18.6.199:7653', '172.18.6.201:7653', '172.18.6.196:7653']
        proxysUseCount = [int(proxyUseCount) for proxyUseCount in r.mget(proxys)]
        minUseCountIpIndex = proxysUseCount.index(min(proxysUseCount))
        currentProxy = proxys[minUseCountIpIndex]
        r.set(proxys[minUseCountIpIndex], proxysUseCount[minUseCountIpIndex]+1)
        return currentProxy


    def proxyUseCountAddOne(self, proxy):
        r = Redis(connection_pool=self.pool)


def get_cookies(content):
    return {i['name']:i['value'] for i in content}


def last_month_date(lasts=1):
    now_date_str = time.strftime("%Y%m")
    now_date = datetime.strptime(now_date_str, "%Y%m")

    last_month = now_date.month - lasts
    year = now_date.year
    if last_month <= 0:
        last_month = 12 + last_month
        year -= 1
    date = datetime.strftime(datetime(year=year,month=last_month,day=now_date.day), "%Y%m")
    return date



def get_before_month(end_date_str, lasts=1):
    end_date = datetime.strptime(end_date_str, "%Y%m")

    last_month = end_date.month - lasts
    year = end_date.year
    if last_month <= 0:
        last_month = 12 + last_month
        year -= 1
    date = datetime.strftime(datetime(year=year,month=last_month,day=end_date.day), "%Y%m")
    return date


def months(start_date, end_date, lasts=1):
    end_year, end_month = int(end_date[:4]),int(end_date[4:6])
    start_year, start_month = int(start_date[:4]),int(start_date[4:6])

    # print(end_year,end_month)
    # print(start_year,start_month)
    yield end_date
    delay_month = end_month - start_month
    if delay_month <= 0 and start_year < end_year:
        delay_month = end_month + (12 - start_month)
    for i in range(delay_month):
        # print(last_month_date(i+1))
        yield get_before_month(end_date,i+lasts)