# -*- coding: utf-8 -*-
import json


class Parse():
    
    def __init__(self, content):
        self.content = content

    
    def parse_cmcc(self):
        info = json.loads(self.content)
        try:
            billInfo = dict(
                    allFee=info['result']['allFee'],
                    billMonth=info['curDate'],
                    billList=[{'name': bill['name'],'value': bill['amount']} for bill in info['billList']]
                )
            
            # with open('./json_data/联通账单数据格式.json', 'w') as f:
            #     f.write(json.dumps(info)
            return billInfo
        except:
            return None


    def parse_mobile(self):

        userInfo = {}

        infos = json.loads(self.content)['data']

        billInfos = []
        for info in infos:
            billInfo = dict(
                allFee=info['billFee'],
                billMonth=info['billMonth']
            )

            billList = []

            for fa_bill in info['billMaterials'][:7]:

                billList.append(dict(name=fa_bill['billEntriy'], value=fa_bill['billEntriyValue']))
    
            billInfo['billList'] = billList
            billInfo.update({'billList': billList})
            billInfos.append(billInfo)
        info = dict(billInfos=billInfos)
        
        # with open('./json_data/移动11个月账单(解析后).json', 'w') as f:
        #     f.write(json.dumps(info))

        return info



    def parseFlowCmcc(self):
        
        
        content_dict = json.loads(self.content)

        flowInfo = []
        if 'fourpackage' in content_dict:
            for item in content_dict['fourpackage']:
                if item['elemType'] == '3' and '赠' not in item['addUpItemName'] and '赠' not in item['feePolicyName'] and float(item['totalValue']) > 0:
                    if '免费' not in item['addUpItemName'] and '免费' not in item['feePolicyName']:
                        totalValue = item['totalValue'] + item['totalUnitVal'] if item['totalUnitVal'] == 'MB' else "%.2fMB" % (float(item['totalValue'])*1024)
                        usedValue = item['usedValue'] + item['totalUnitVal'] if item['totalUnitVal'] == 'MB' else "%.2fMB" % (float(item['usedValue'])*1024)
                        flowInfo.append({
                                'policyName':item['feePolicyName'],
                                'typeName':item['addUpItemName'],
                                'totalValue': totalValue,
                                'usedValue':usedValue
                            })

        
        voiceInfo = []
        if 'voiceListCombo' in content_dict:
            for item in content_dict['voiceListCombo']:
                if float(item['addUpUpper']) > 0:
                    voiceInfo.append({
                        'policyName':item['addUpItemName'],
                        'totalDuration': item['addUpUpper'],
                        'usedValue': item['xusedValue'],
                        'canUseValue': item['xCanUseValue'],
                        # 'canUsedPercent': item['usedPercent']
                    })

        smsInfo = []
        if 'smsListCombo' in content_dict:
            for item in content_dict['smsListCombo']:
                if float(item['addUpUpper']) > 0:
                    smsInfo.append({
                        'totalCount': item['addUpUpper'],
                        'usedValue': item['xusedValue'],
                        'canUseValue': item['xCanUseValue'],
                        'canUsedPercent': item['usedPercent']
                    })
            
        
            

        info = dict(
            packageName=content_dict['userInfo']['packageName'],
            totalFlow='',
            totalVoice='',
            flowInfo=flowInfo,
            voiceInfo=voiceInfo,
            smsInfo=smsInfo
        )
        # print(json.dumps(info))
        return info


    def parseFamilyTypeFlowCmcc(self):

        content_dict = json.loads(self.content)
            
        flowInfo = []
        if 'flowListCombo' in content_dict:
            for item in content_dict['flowListCombo']:
                if item['elemType'] == '3' and '赠' not in item['addUpItemName'] and '赠' not in item['feePolicyName'] and float(item['addUpUpper']) > 0:
                    if '免费' not in item['addUpItemName'] and '免费' not in item['feePolicyName']:
                        flowInfo.append({
                                'policyName':item['feePolicyName'],
                                'typeName':item['addUpItemName'],
                                'totalValue': item['addUpUpper'] + 'MB',
                                'usedValue':item['xusedValue'] + 'MB'
                            })
        return flowInfo


    def parseAddValueCmcc(self):

        content_dict = json.loads(self.content)

        queryDateScope = content_dict['queryDateScope'].replace('至','/').replace('-','')
        addValueInfo = dict(queryDateScope=queryDateScope, addValueData=[])
        if 'pageMap' in content_dict:
            for item in content_dict['pageMap']['result']:
                if float(item['totalfee']) > 0 :
                    addValueInfo['addValueData'].append(
                        {
                            'workType': item['businesstype'],
                            'productName': item['businessname'],
                            'orderDate': '%s %s' % (item['begindate'], item['begintime']),
                            'useDateScope': item['capturetime'],
                            'type': item['billingmethod'],
                            'fee': item['onetotalfee']
                        }
                    )

        # print(json.dumps(addValueInfo))
        return addValueInfo



    def parseFlowChina(self):

        content_dict = json.loads(self.content)
        totalFlow = 0
        totalVoice = 0
        flowInfo = []
        voiceInfo = []
        for item in content_dict['data'][0]['arr']:

            # sum_dict = {"policyName": item['mealName'], 'items': []}
            for itemsum in item['resInfos'][0]['secResInfos']:
                if itemsum['resConInfo']['totalMeal'] != '0' and '赠' not in item['mealName'] and '免费' not in item['mealName']: 
                    # if '流量' in itemsum['resConName']:
                    if item['resInfos'][0]['resCode'] == '04':
                        flowInfo.append({
                            'policyName':item['mealName'],
                            'typeName':itemsum['resConName'],
                            'totalValue': str(int(int(itemsum['resConInfo']['totalMeal'])/1024)) + 'MB',
                            'usedValue':str(int(int(itemsum['resConInfo']['useMeal'])/1024)) + 'MB',
                            # 'canUseValue':str(int(int(itemsum['resConInfo']['balMeal'])/100)) + 'MB',
                        })
                        if itemsum['secResourcesLimitType'] == '01':
                            print(itemsum['resConInfo']['totalMeal'])
                            totalFlow += int(itemsum['resConInfo']['totalMeal'])/1024.00

                    # elif '语音' in itemsum['resConName']:
                    elif item['resInfos'][0]['resCode'] == '01':
                        voiceInfo.append({
                            'policyName': item['mealName'],
                            'totalDuration': itemsum['resConInfo']['totalMeal'],
                            'usedValue': itemsum['resConInfo']['useMeal'],
                            'canUseValue': itemsum['resConInfo']['balMeal'],
                            # 'canUsedPercent': item['usedPercent']
                        })
                        totalVoice += int(itemsum['resConInfo']['totalMeal'])

        info = dict(
            packageName='',
            totalFlow= "%.2fGB" % (totalFlow/1024.0),
            totalVoice=str(int(totalVoice)),
            flowInfo=flowInfo,
            voiceInfo=voiceInfo,
            smsInfo=[]
        )
        # print(json.dumps(info))
        return info


    def parseAddValueChina(self):
 

        infos = json.loads(self.content)['data']

        addValues = []
        for info in infos:
            addValue = {
                'queryDateScope': info['billStartDate'] + '/' + info['billEndDate'],
                'addValueData': []
                }


            for fa_bill in info['billMaterials']:
                if int(fa_bill['billEntriy']) == 5:
                    for item in fa_bill['billMaterialInfos']:
                        addValue['addValueData'].append({
                            "workType": "增值业务",
                            "productName": item['itemName'],
                            "orderDate": "",
                            "useDateScope": "",
                            "type": "",
                            "fee": item['itemValue']
                        })
            addValues.append(addValue)

        return addValues


# if __name__ == "__main__":
#     with open('./json_data/移动流量.json', 'r') as f:
#         content = f.read()

#     res = Parse(content).parseFlowChina()
#     print(json.dumps(res))