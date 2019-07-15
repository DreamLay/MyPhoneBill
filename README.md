
# 登录并获取移动联通话费数据


## 一、环境
**macOS or Linux, python3.5及以上**

**必要flask、requests、selenium、redis、chomedriver(非python库)**


## 二、运行

    source activate python3.6(激活环境，非必须)

    python server_v1.2.py
    or
    nohup  /root/anaconda3/envs/python3.6/bin/python  server_v1.2.py  -log=stdout &


## 三、结构说明
    MyPhonBill
        |____ server.py http            接口服务
        |____ server_test.py            本地测试非http直接调用函数
        |____ china_mobile.py           移动流程
        |____ CMCC_main                 联通流程
        |____ funtion
        |       |____ funtions.py       其他函数
        |       |____ parse.py          解析函数
        |____ test_china.py             新版移动流程测试
        


## 四、接口说明

### 发送验证码post参数

```json
{
    "username": "139xxxxxxxx",
    "operator": "0" //0移动，1联通
}
```


### 发送验证码post返回数据

```json
{
    "title": "发送验证码",
    "resultCode": "0", // 0成功 1发送频繁 2发送次数达到上限,4号码有误（移动包括运营商错误）,6请求失败,9请求超时(超过15秒，5秒一次)
    /*
        "needVerifyCode":"1",
        "sendSmsCode":"1",
    */
    "msg": "发送成功",
    "phoneNum": "139xxxxxxxx",
    "proxy": "172.18.6.199:7653" // 代理地址，需要在登录时提交
}
```



### 登录post请求
```json
{
    "username": "138XXXXXXXX",
    "password": "xxxxxx", // (联通)
    "smsCode": "xxxxxx",
    "operator": "0", //0移动，1联通
    "billStartDate": "201901", //字段名改变
    "billEndDate": "201906", //字段名改变
    "valueAddedDates": [ //增值业务查询日期
        ["2019-01-01","2019-01-31"],
        ["2019-02-01","2019-02-28"],
        ["2019-03-01","2019-03-30"],
        ["2019-04-01","2019-01-31"],
        ["2019-05-01","2019-01-31"],
        ["2019-06-01","2019-01-31"]
    ],
    "proxy": "172.18.6.199:7653" // 代理地址
}
```


### 登录post返回数据
```json
{
    "title":"登录",
    "resultCode":"0000",
    "cookies":{
        // 省略
    },
    "msg":"成功",
    "phoneNum":"156xxxxxxxx",
    "info":{ 
        "billInfo":{ //历史账单
            "billInfos":[
                {
                    "allFee":"42.18",
                    "billMonth":"201905",
                    "billList":[
                        {
                            "name":"月固定费",
                            "value":"36.00"
                        },
                        {
                            "name":"增值业务费",
                            "value":"0.30"
                        },
                        {
                            "name":"调增减项",
                            "value":"5.88"
                        }
                    ]
                },
                {
                    "allFee":"98.32",
                    "billMonth":"201904",
                    "billList":[
                        {
                            "name":"月固定费",
                            "value":"36.00"
                        },
                        {
                            "name":"增值业务费",
                            "value":"0.20"
                        },
                        {
                            "name":"调增减项",
                            "value":"62.12"
                        }
                    ]
                },
                {
                    "allFee":"77.88",
                    "billMonth":"201903",
                    "billList":[
                        {
                            "name":"月固定费",
                            "value":"36.00"
                        },
                        {
                            "name":"增值业务费",
                            "value":"0.20"
                        },
                        {
                            "name":"调增减项",
                            "value":"41.68"
                        }
                    ]
                },
                {
                    "allFee":"88.00",
                    "billMonth":"201902",
                    "billList":[
                        {
                            "name":"月固定费",
                            "value":"36.00"
                        },
                        {
                            "name":"增值业务费",
                            "value":"0.30"
                        },
                        {
                            "name":"调增减项",
                            "value":"51.70"
                        }
                    ]
                }
            ],
            "billMonthCount":"4"
        },
        "packageInfo":{ //套餐内信息
            "packageName":"(OCS)双4G微信沃派2.0", //套餐名
            "totalFlow":"51200MB", //总流量
            "totalVoice":"80", //总通话时长
            "flowInfo":[ //流量
                {
                    "policyName":"宽带融合专享0元包1G省内流量(已升为国内)",
                    "typeName":"省内流量(已升为国内)",
                    "totalValue":"1.00GB",
                    "usedValue":"1.00GB"
                },
                {
                    "policyName":"(OCS)双4G微信沃派2.0",
                    "typeName":"省内流量(已升为国内)",
                    "totalValue":"10.00MB",
                    "usedValue":"10.00MB"
                },
                {
                    "policyName":"(OCS)双4G微信沃派2.0",
                    "typeName":"省内闲时流量(已升为国内)",
                    "totalValue":"2.00GB",
                    "usedValue":"2.00GB"
                }
            ],
            "voiceInfo":[ //语音
                {
                    "policyName": "国内语音通话时长账本-OCS",
                    "totalDuration":"60",
                    "usedValue":"13",
                    "canUseValue":"47",
                    // "canUsedPercent":"78"
                }
            ],
            "smsInfo":[ //短信

            ],
            "productFee": "58",  //套餐资费
        },
        "valueAddedInfo":[ //增值业务信息
            {
                "queryDateScope":"20190101/20190131",
                "addValueData":[

                ]
            },
            {
                "queryDateScope":"20190201/20190228",
                "addValueData":[

                ]
            },
            {
                "queryDateScope":"20190301/20190331",
                "addValueData":[

                ]
            },
            {
                "queryDateScope":"20190401/20190430",
                "addValueData":[

                ]
            },
            {
                "queryDateScope":"20190501/20190531",
                "addValueData":[

                ]
            },
            {
                "queryDateScope":"20190601/20190630",
                "addValueData":[
                    {
                        "workType":"增值业务",
                        "productName":"VAC详单",
                        // "orderDate":"2019-06-02 11:05:33",
                        // "useDateScope":"0秒",
                        // "type":"一次使用收费（按次）",
                        "fee":"0.00"
                    },
                    {
                        "workType":"增值业务",
                        "productName":"VAC详单",
                        // "orderDate":"2019-06-02 11:05:33",
                        // "useDateScope":"0秒",
                        // "type":"一次使用收费（按次）",
                        "fee":"0.00"
                    },
                    {
                        "workType":"增值业务",
                        "productName":"VAC详单",
                        // "orderDate":"2019-06-02 11:05:33",
                        // "useDateScope":"0秒",
                        // "type":"一次使用收费（按次）",
                        "fee":"0.00"
                    }
                ]
            }
        ]
    }
}
```

## 五、其它
### ***现已成功完全使用requests模拟登录获取联通数据，不需要使用selenium***。
### ***移动还未实现纯requests模拟***