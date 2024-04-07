

import base64
import hashlib
import hmac
import json
from datetime import datetime

import requests

def 多空(posSide):
    if posSide == "long":
        return "多"
    elif posSide == "short":
        return "空"
    else:
        return ""


def 查看账户余额(UserInfo):

    api_key = UserInfo['api_key']
    secret_key = UserInfo['secret_key']
    passphrase = UserInfo['passphrase']

    timestamp = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
    method = 'GET'
    request_path = '/api/v5/account/balance'
    body = ''

    message = timestamp + method + request_path + body
    print(message)
    signature = base64.b64encode(hmac.new(secret_key.encode('utf-8'), message.encode('utf-8'), hashlib.sha256).digest())
    # print(timestamp)
    # print(signature)

    base_url = 'https://www.okx.com'

    headers = {
        "OK-ACCESS-KEY": api_key,
        "OK-ACCESS-SIGN": signature.decode('utf-8'),
        "OK-ACCESS-TIMESTAMP": timestamp,
        "OK-ACCESS-PASSPHRASE": passphrase,
        "Content-Type": "application/json",
    }

    url = base_url + request_path
    # print(url)

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = json.loads(response.text)['data'][0]
        # print(data)
        print("数据产生时间：", datetime.fromtimestamp(int(data['uTime']) / 1000).strftime('%m/%d %H:%M:%S'))
        print(f'美金层面权益：{data["totalEq"]}')
        print(f'仓位美金价值：{data["notionalUsd"]}')
        for details in data['details']:
            print(f'币种类型：{details["ccy"]}')
            print(f'币种余额：{details["cashBal"]}')
            print(f'可用余额：{details["availBal"]}')
            print(f'冻结金额：{details["fixedBal"]}')


def 查看持仓信息(UserInfo):

    api_key = UserInfo['api_key']
    secret_key = UserInfo['secret_key']
    passphrase = UserInfo['passphrase']

    timestamp = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'

    print(datetime.utcnow())

    timestamp = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S') + ".000Z"

    print(timestamp)

    method = 'GET'
    request_path = '/api/v5/account/positions?instType=SWAP'
    body = ''

    message = timestamp + method + request_path + body

    signature = base64.b64encode(hmac.new(secret_key.encode('utf-8'), message.encode('utf-8'), hashlib.sha256).digest())

    print(signature.decode('utf-8'))

    # print(timestamp)
    # print(signature)

    base_url = 'https://www.okx.com'

    headers = {
        "OK-ACCESS-KEY": api_key,
        "OK-ACCESS-SIGN": signature.decode('utf-8'),
        "OK-ACCESS-TIMESTAMP": timestamp,
        "OK-ACCESS-PASSPHRASE": passphrase,
        "Content-Type": "application/json",
    }

    url = base_url + request_path
    # print(url)

    response = requests.get(url, headers=headers)
    print(response.text)
    if response.status_code == 200:
        data = json.loads(response.text)['data']
        print(data)
        # print("数据产生时间：", datetime.fromtimestamp(int(data['uTime']) / 1000).strftime('%m/%d %H:%M:%S'))
        # print(f'美金层面权益：{data["totalEq"]}')
        # print(f'仓位美金价值：{data["notionalUsd"]}')
        # for details in data['details']:
        #     print(f'币种类型：{details["ccy"]}')
        #     print(f'币种余额：{details["cashBal"]}')
        #     print(f'可用余额：{details["availBal"]}')
        #     print(f'冻结金额：{details["fixedBal"]}')


def 设置杠杆倍数(UserInfo, instId, lever, mgnMode, posSide):

    api_key = UserInfo['api_key']
    secret_key = UserInfo['secret_key']
    passphrase = UserInfo['passphrase']

    timestamp = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
    method = 'POST'
    request_path = '/api/v5/account/set-leverage'

    if mgnMode == "isolated":
        body = {
            "instId": instId,  # "BTC-USDT",
            "lever": lever,
            'mgnMode': mgnMode,
            "posSide": posSide,
            # "ccy": "USDT",
        }
    else:
        body = {
            "instId": instId,  # "BTC-USDT",
            "lever": lever,
            'mgnMode': mgnMode,
            # "posSide": posSide,
            # "ccy": "USDT",
        }

    message = timestamp + method + request_path + json.dumps(body)

    signature = base64.b64encode(hmac.new(secret_key.encode('utf-8'), message.encode('utf-8'), hashlib.sha256).digest())

    base_url = 'https://www.okx.com'

    headers = {
        "OK-ACCESS-KEY": api_key,
        "OK-ACCESS-SIGN": signature.decode('utf-8'),
        "OK-ACCESS-TIMESTAMP": timestamp,
        "OK-ACCESS-PASSPHRASE": passphrase,
        "Content-Type": "application/json",
    }

    url = base_url + request_path

    response = requests.post(url, headers=headers, data=json.dumps(body))
    # print(response.text)
    if response.status_code == 200:
        msg = json.loads(response.text)['msg']
        if msg == "":
            data = json.loads(response.text)['data'][0]
            # print(data)
            # print('设置杠杆倍数成功')
            # print(f'产品ID：{data["instId"]}')
            # print(f'持仓方向：{data["posSide"]}')
            # print(f'杠杆倍数：{data["lever"]}')
            return 1
        else:
            # printf(f'设置杠杆倍数失败，原因:{response.text}', 'Purple')
            print(f'设置杠杆倍数失败，原因:{response.text}')
            return 0
    else:
        print(f'设置杠杆倍数失败，原因:{response.text}')
        # printf(f'设置杠杆倍数失败，原因:{response.text}', 'Purple')
        return 0

def 加仓(printf, mode, UserInfo, instId, side, posSide, sz='1', lever='5', tdMode='cross'):

    api_key = UserInfo['api_key']
    secret_key = UserInfo['secret_key']
    passphrase = UserInfo['passphrase']

    if mode == '平' or 设置杠杆倍数(printf, UserInfo, instId, lever, tdMode, posSide, tdMode):

        # print('123')
        timestamp = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
        method = 'POST'
        request_path = '/api/v5/trade/order'

        body = {
            "instId": instId,  # "BTC-USDT",
            "tdMode": tdMode,
            "ccy": "USDT",
            "reduceOnly": True,
            # "lever": "0.5",
            "side": side,  # buy  sell
            "posSide": posSide,  # long short
            "ordType": "market",
            "sz": sz,
        }

        message = timestamp + method + request_path + json.dumps(body)

        signature = base64.b64encode(hmac.new(secret_key.encode('utf-8'), message.encode('utf-8'), hashlib.sha256).digest())

        base_url = 'https://www.okx.com'

        headers = {
            "OK-ACCESS-KEY": api_key,
            "OK-ACCESS-SIGN": signature.decode('utf-8'),
            "OK-ACCESS-TIMESTAMP": timestamp,
            "OK-ACCESS-PASSPHRASE": passphrase,
            "Content-Type": "application/json",
        }

        url = base_url + request_path
        # print(url)

        response = requests.post(url, headers=headers, data=json.dumps(body))
        # print(response.text)
        if response.status_code == 200:
            data = json.loads(response.text)
            msg = data['data'][0]['sMsg']

            if msg == 'Order placed':
                printf(f'{mode}{多空(posSide)}成功, 订单id：{data["data"][0]["ordId"]} ' + datetime.fromtimestamp(int(data['inTime']) / 1000000).strftime('%m/%d %H:%M:%S'), 'blue')
            else:
                printf(f'{mode}{多空(posSide)}失败, 原因：{msg} ' + datetime.fromtimestamp(int(data['inTime']) / 1000000).strftime('%m/%d %H:%M:%S'), 'Purple')


        else:
            printf(f'修改仓位错误，原因:{response.text}', 'Purple')
    else:
        printf(f'开单设置杠杆倍数失败', 'Purple')


def 减仓(UserInfo, instId, side, posSide, sz=1):

    api_key = UserInfo['api_key']
    secret_key = UserInfo['secret_key']
    passphrase = UserInfo['passphrase']

    timestamp = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
    method = 'POST'
    request_path = '/api/v5/trade/order'
    body = {
        "instId": instId,  # "BTC-USDT",
        "tdMode": "cross",
        "reduceOnly": True,
        "side": side,  # buy  sell
        "posSide": posSide,  # long short
        "ordType": "market",
        "sz": sz,
    }

    message = timestamp + method + request_path + json.dumps(body)

    signature = base64.b64encode(hmac.new(secret_key.encode('utf-8'), message.encode('utf-8'), hashlib.sha256).digest())

    base_url = 'https://www.okx.com'

    headers = {
        "OK-ACCESS-KEY": api_key,
        "OK-ACCESS-SIGN": signature.decode('utf-8'),
        "OK-ACCESS-TIMESTAMP": timestamp,
        "OK-ACCESS-PASSPHRASE": passphrase,
        "Content-Type": "application/json",
    }

    url = base_url + request_path
    # print(url)

    response = requests.post(url, headers=headers, data=json.dumps(body))
    # print(response.text)
    if response.status_code == 200:
        data = json.loads(response.text)
        msg = data['data'][0]['sMsg']
        if msg == 'Order placed':
        # print(data)
            print('成功：')
            print("请求okx时间：", datetime.fromtimestamp(int(data['inTime']) / 1000000).strftime('%m/%d %H:%M:%S'))
            print("okx返回时间：", datetime.fromtimestamp(int(data['outTime']) / 1000000).strftime('%m/%d %H:%M:%S'))
            print(f'订单id：{data["data"][0]["ordId"]}')
        else:
            print('失败：')
            print("请求okx时间：", datetime.fromtimestamp(int(data['inTime']) / 1000000).strftime('%m/%d %H:%M:%S'))
            print("okx返回时间：", datetime.fromtimestamp(int(data['outTime']) / 1000000).strftime('%m/%d %H:%M:%S'))
            print(msg)


def 市价全平(UserInfo, instId, posSide):

    api_key = UserInfo['api_key']
    secret_key = UserInfo['secret_key']
    passphrase = UserInfo['passphrase']

    timestamp = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
    method = 'POST'
    request_path = '/api/v5/trade/close-position'
    body = {
        "instId": instId,  # "BTC-USDT",
        "mgnMode": "cross",
        "posSide": posSide,
        "ccy": "USDT",
    }

    message = timestamp + method + request_path + json.dumps(body)

    signature = base64.b64encode(hmac.new(secret_key.encode('utf-8'), message.encode('utf-8'), hashlib.sha256).digest())

    base_url = 'https://www.okx.com'

    headers = {
        "OK-ACCESS-KEY": api_key,
        "OK-ACCESS-SIGN": signature.decode('utf-8'),
        "OK-ACCESS-TIMESTAMP": timestamp,
        "OK-ACCESS-PASSPHRASE": passphrase,
        "Content-Type": "application/json",
    }

    url = base_url + request_path
    # print(url)

    response = requests.post(url, headers=headers, data=json.dumps(body))
    # print(response.text)
    if response.status_code == 200:
        msg = json.loads(response.text)['msg']
        if msg == "":
            data = json.loads(response.text)['data'][0]
            # print(data)
            print('市价全平成功')
            print(f'产品ID：{data["instId"]}')
            print(f'持仓方向：{data["posSide"]}')
        else:
            print('市价全平失败')
            print(msg)




    # 设置杠杆倍数(UserInfo, "BTC-USDT-SWAP", "30", "cross", "long")
    # 查看账户余额(UserInfo)
    # 查看持仓信息(UserInfo)
    # 加仓(UserInfo, 'LOOKS-USDT-SWAP', 'buy', 'long', '5', '20', 'cross')
    #
    # 设置杠杆倍数('LUNA-USDT-SWAP', '30', 'cross', 'long')
    #
    # 减仓('LUNA-USDT-SWAP', 'sell', 'long', '1')
    #
    # 市价全平(UserInfo, 'LOOKS-USDT-SWAP', 'long')
