import base64, requests, time, json
import rsa, execjs


class Encryption():


    def d_BASE64(self, origStr):

        if (len(origStr)%3 == 1): 
            origStr += "=="
        elif (len(origStr)%3 == 2): 
            origStr += "=" 
        return origStr


    def _str2key(self, s):
        # 对字符串解码
        b_str = base64.b64decode(s)

        if len(b_str) < 162:
            return False

        hex_str = ''

        # 按位转换成16进制
        for x in b_str:
            h = hex(x)[2:]
            h = h.rjust(2, '0')
            hex_str += h

        # 找到模数和指数的开头结束位置
        m_start = 29 * 2
        e_start = 159 * 2
        m_len = 128 * 2
        e_len = 3 * 2

        modulus = hex_str[m_start:m_start + m_len]
        exponent = hex_str[e_start:e_start + e_len]

        return modulus, exponent


    def rsa_encrypt(self, pubkey_str, passwd):
        '''
        rsa加密
        :param s:
        :param pubkey_str:公钥
        :return:
        '''
        key = self._str2key(pubkey_str)
        modulus = int(key[0], 16)
        exponent = int(key[1], 16)
        pubkey = rsa.PublicKey(modulus, exponent)
        return base64.b64encode(rsa.encrypt(passwd.encode(), pubkey)).decode()


    def run(self, passwd):
        key = 'MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAsgDq4OqxuEisnk2F0EJFmw4xKa5IrcqEYHvqxPs2CHEg2kolhfWA2SjNuGAHxyDDE5MLtOvzuXjBx/5YJtc9zj2xR/0moesS+Vi/xtG1tkVaTCba+TV+Y5C61iyr3FGqr+KOD4/XECu0Xky1W9ZmmaFADmZi7+6gO9wjgVpU9aLcBcw/loHOeJrCqjp7pA98hRJRY+MML8MK15mnC4ebooOva+mJlstW6t/1lghR8WNV8cocxgcHHuXBxgns2MlACQbSdJ8c6Z3RQeRZBzyjfey6JCCfbEKouVrWIUuPphBL3OANfgp0B+QG31bapvePTfXU48TYK0M5kE+8LgbbWQIDAQAB'
        # key = 'MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAsgDq4OqxuEisnk2F0EJFmw4xKa5IrcqEYHvqxPs2CHEg2kolhfWA2SjNuGAHxyDDE5MLtOvzuXjBx/5YJtc9zj2xR/0moesS+Vi/xtG1tkVaTCba+TV+Y5C61iyr3FGqr+KOD4/XECu0Xky1W9ZmmaFADmZi7+6gO9wjgVpU9aLcBcw/loHOeJrCqjp7pA98hRJRY+MML8MK15mnC4ebooOva+mJlstW6t/1lghR8WNV8cocxgcHHuXBxgns2MlACQbSdJ8c6Z3RQeRZBzyjfey6JCCfbEKouVrWIUuPphBL3OANfgp0B+QG31bapvePTfXU48TYK0M5kE+8LgbbWQIDAQAB'
        # key = self.d_BASE64(key)
        return self.rsa_encrypt(key, passwd)


def get_WT_FPC():
    now = str(int(round(time.time() * 1000)))
    jsstr = get_js()
    ctx = execjs.compile(jsstr) #加载JS文件
    value = "id=%s:lv=%s:ss=%s" % (ctx.call('test'), now, now) 
    return value  #调用js方法  第一个参数是JS的方法名，后面的data和key是js方法的参


def get_js():
    f = open("./a.js", 'r', encoding='utf-8') # 打开JS文件
    line = f.readline()
    htmlstr = ''
    while line:
        htmlstr = htmlstr + line
        line = f.readline()
    return htmlstr

    

class ChinaMobile():
    
    def __init__(self, account):
        self.account = account
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0.2 Safari/605.1.15",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Origin": "https://login.10086.cn",
            "Referer": "https://login.10086.cn/html/login/login.html",
            "X-Requested-With": "XMLHttpRequest"
        }
        self.cookies = {}

    
    def login(self, smsCode):
        s = requests.session()

        now = str(int(round(time.time() * 1000)))
        # timestamp_url = 'https://login.10086.cn/loadSendflag.htm?timestamp='
        # timestamp_url_res = s.get(timestamp_url, headers=self.headers)
        # self.cookies = {**self.cookies, **timestamp_url_res.cookies.get_dict()}


        captchazh_res = s.get('https://login.10086.cn/captchazh.htm?type=12', headers=self.headers)
        self.cookies = {**self.cookies, **captchazh_res.cookies.get_dict()}


        genqr_res = s.get('https://login.10086.cn/genqr.htm', headers=self.headers)
        self.cookies = {**self.cookies, **genqr_res.cookies.get_dict()}


        # timestamp_url_res2 = s.get(timestamp_url, headers=self.headers)
        # self.cookies = {**self.cookies, **timestamp_url_res2.cookies.get_dict()}

        # self.cookies = {**self.cookies, **cookies}
        login_url  = 'https://login.10086.cn/login.htm?%s'
        # account = '13824559862'
        # smsCode = '473940'
        getData = dict(
            accountType='01',account=self.account,password=smsCode,
            pwdType='02',smsPwd='',inputCode='',backUrl='https://shop.10086.cn/i/',
            rememberMe='0', channelID='12002',loginMode='01',protocol='https:',timestamp=now
        )

        params = '&'.join(["%s=%s" % (i, getData[i]) for i in getData])
        login_res = s.get(login_url % params, headers=self.headers, cookies=self.cookies)
        uid = json.loads(login_res.content.decode())['uid']
        artifact = json.loads(login_res.content.decode())['artifact']
        self.cookies = {**self.cookies, **login_res.cookies.get_dict()}

        now = str(int(round(time.time() * 1000)))
        self.cookies['ssologinprovince'] = '200'
        self.cookies['WT_FPC'] = "id=%s:lv=%s:ss=%s" % (artifact, now, now) 
        jsessionid_res = s.get('https://shop.10086.cn/i/v1/auth/loginfo?_=%s' % now, headers=self.headers, cookies=self.cookies)
        self.cookies = {**self.cookies, **jsessionid_res.cookies.get_dict()}
        print(self.cookies)

        # "WT_FPC=id=" + a + ":lv=" + h.getTime().toString() + ":ss=" + g.getTime().toString() + "

        self.headers['Referer'] = 'https://shop.10086.cn/i/?f=home&welcome={}'.format(now)
        bill_url = "https://shop.10086.cn/i/v1/fee/billinfo/{}?bgnMonth={}&endMonth={}&_={}"
        bill_res = requests.get(
            bill_url.format(self.account, '201903', '201905', now),
            headers=self.headers, cookies=self.cookies
        )
        print('\n\n')
        print(bill_res.content.decode())
        with open('./s.json', 'w') as f:
            f.write(bill_res.content.decode())

        return login_res.content.decode(), self.cookies




    def sendSMSCode(self):
        s = requests.session()

        now = str(int(round(time.time() * 1000)))
        timestamp_url = 'https://login.10086.cn/loadSendflag.htm?timestamp='
        timestamp_res = s.get(timestamp_url, headers=self.headers)
        self.cookies = {**self.cookies, **timestamp_res.cookies.get_dict()}


        # captchazh_res = s.get('https://login.10086.cn/captchazh.htm?type=12', headers=self.headers)
        # self.cookies = {**self.cookies, **captchazh_res.cookies.get_dict()}


        # genqr_res = s.get('https://login.10086.cn/genqr.htm',headers=self.headers)
        # self.cookies = {**self.cookies, **genqr_res.cookies.get_dict()}


        # timestamp_res2 = s.get(timestamp_url, headers=self.headers)
        # self.cookies = {**self.cookies, **timestamp_res2.cookies.get_dict()}

        # checkUidAvailable_res = s.post('https://login.10086.cn/checkUidAvailable.action',headers=self.headers, cookies=self.cookies)
        # self.cookies = {**self.cookies, **checkUidAvailable_res.cookies.get_dict()}
        # print(checkUidAvailable_res.content.decode())
        
        # self.cookies['captchatype'] = 'z'
        # self.headers.update({'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'})
        # chkNumberAction_url  = 'https://login.10086.cn/chkNumberAction.action'
        # data = dict(userName=self.account, loginMode='01', channelID='12002')
        # chkNumberAction_res = s.post(chkNumberAction_url, data=data, headers=self.headers, cookies=self.cookies)
        # self.cookies = {**self.cookies, **chkNumberAction_res.cookies.get_dict()}
        # print(chkNumberAction_res.content.decode())
        
        # loadToken_url = 'https://login.10086.cn/loadToken.action'
        # loadToken_res = s.post(loadToken_url, data=dict(userName=self.account), headers=self.headers, cookies=self.cookies)
        # self.headers['Xa-before'] = json.loads(loadToken_res.content.decode())['result']
        # self.cookies = {**self.cookies, **loadToken_res.cookies.get_dict()}
        # print(loadToken_res.content.decode())

        sendRandomCodeAction_url = 'https://login.10086.cn/sendRandomCodeAction.action'
        # print(self.headers)
        sendRandomCodeAction_res = s.post(sendRandomCodeAction_url, data=dict(userName=self.account,type='01',channelID='12002'), headers=self.headers, cookies=self.cookies)
        self.cookies = {**self.cookies, **sendRandomCodeAction_res.cookies.get_dict()}
        print(sendRandomCodeAction_res.content.decode())
        return self.cookies




if __name__ == "__main__":

    # cookies = ChinaMobile('13560046649').sendSMSCode()
    smsCode = input('验证码: ')
    s = ChinaMobile('13719246701').login(smsCode)
    # print(cookies)
    # print('----------------------------')
    # print('\n\n')
    # print(s)






# 摘要
# URL: https://shop.10086.cn/i/v1/auth/loginfo?_=1562751957716
# 状态: 200 OK
# 来源: 网络
# 地址: 221.176.60.132:443

# 请求
# GET /i/v1/auth/loginfo HTTP/1.1
# Content-Type: *
# Pragma: no-cache
# Accept: application/json, text/javascript, */*; q=0.01
# If-Modified-Since: 0
# Expires: 0
# Accept-Encoding: br, gzip, deflate
# Cache-Control: no-store, must-revalidate
# Host: shop.10086.cn
# Accept-Language: zh-cn
# User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.1.1 Safari/605.1.15
# Referer: https://shop.10086.cn/i/
# Connection: keep-alive
# Cookie: WT_FPC=id=21bf9dfbaede56df1e31562751957497:lv=1562751957497:ss=1562751957497; PHPSESSID=lrrhvhg1q4uth51n0jl8cj2e87; c=d1e2c28fc47448bea429564717d25583; cmccssotoken=d1e2c28fc47448bea429564717d25583@.10086.cn; is_login=true; verifyCode=0907106c7a89b7ccbc9a40859ee41ad0a35073fd; sendflag=20190710174517316329; CaptchaCode=OrZoIq; lgToken=7aea396ef1834eebbce682c08c572055; rdmdmd5=35A5B50E6A73AF85BF3EF337F1AA1FA9
# X-Requested-With: XMLHttpRequest

# 响应
# HTTP/1.1 200 OK
# Connection: Keep-alive
# Content-Type: application/json;charset=utf-8
# Set-Cookie: jsessionid-echd-cpt-cmcc-jt=FC0EB064039529EF1D8B0F40B4E62297;Domain=10086.cn;Path=/;HttpOnly
# Date: Wed, 10 Jul 2019 09:45:45 GMT
# Keep-Alive: timeout=15, max=100
# Transfer-Encoding: Identity
# wtlwpp-rest: 176_8712

# 查询字符串参数
# _: 1562751957716



# 联通
# http://iservice.10010.com/e3/static/check/checklogin/?_=1562752511428
# Set-Cookie: route=f6580975dacd2642305771459ba78210; Path=/
# Set-Cookie: e3route=a37bb3a7cef8d70bca838589b4ce5db9185a6d2d; Path=/; HttpOnly
# Set-Cookie: JSESSIONID=C2F0CE776E402748A0D6E51C27055473; Path=/e3; HttpOnly