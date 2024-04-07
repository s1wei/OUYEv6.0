import os
import threading
import tkinter as tk
import configparser
import webbrowser

import time
import json
import requests
from bs4 import BeautifulSoup

import REST

from datetime import datetime


def joinpath(*path):
    return os.path.realpath(os.path.join(*path))


def save_config(unique_name, my_capital, trader_capital, api_key, secret_key, passphrase, sleep_interval, Openbrowser):
    config = configparser.ConfigParser()
    config['Settings'] = {
        'UniqueName': unique_name,
        'MyCapital': my_capital,
        'TraderCapital': trader_capital,
        'ApiKey': api_key,
        'SecretKey': secret_key,
        'Passphrase': passphrase,
        'SleepInterval': sleep_interval,
        'Openbrowser': Openbrowser,
    }

    with open('config.ini', 'w') as configfile:
        config.write(configfile)

def load_config():
    config = configparser.ConfigParser()
    config.read('config.ini')

    if 'Settings' in config:
        settings = config['Settings']
        return (
            settings.get('UniqueName', ''),
            settings.get('MyCapital', ''),
            settings.get('TraderCapital', ''),
            settings.get('ApiKey', ''),
            settings.get('SecretKey', ''),
            settings.get('Passphrase', ''),
            settings.get('SleepInterval', ''),
            settings.get('Openbrowser', ''),
        )
    else:
        return '', '', '', '', '', '', ''


def custom_round(value):
    return max(round(value), 1)


def GetTraderdetail(printf, UserInfo, uniqueName, PositionSize):

    global This_Pos, Last_Pos, first_time

    # 备份 This_Pos 为上一次获取的仓位
    Last_Pos = This_Pos.copy()

    url = 'https://www.okx.com/api/v5/copytrading/public-current-subpositions'

    # header = {"content-type": "application/json;charset=UTF-8"}

    params = {
        'instType': 'SWAP',
        'uniqueCode': f'{uniqueName}'
    }

    response = requests.get(url=url, params=params)

    if response.status_code == 200:

        data = json.loads(response.text)['data']


        # 清空 This_Pos
        This_Pos = {}

        for item in data:
            subPos = float(item['subPos'])  # 持仓量
            instId = item['instId']  # 交易货币
            instType = item['instType']
            openAvgPx = item['openAvgPx']  # 开仓均价
            lever = item['lever']  # 杠杆倍数
            mgnMode = item['mgnMode']
            posSide = item['posSide']  # 仓位类型
            subPosId = item['subPosId']  # 交易id
            # uTime = item['uTime']  # 时间

            # 将仓位信息添加到 This_Pos 字典
            This_Pos[subPosId] = {
                'subPos': subPos,
                'instId': instId,
                'openAvgPx': openAvgPx,
                'lever': lever,
                'mgnMode': mgnMode,
                'posSide': posSide,
                'subPosId': subPosId,
            }

            if float(openAvgPx) > 0.00000001:

                # 如果交易ID在上一次的字典中没有，说明是新开仓
                if subPosId not in Last_Pos and not first_time:

                    MyBuyNum = custom_round(PositionSize * subPos)

                    if posSide == 'net':

                        if float(subPos) > 0:
                            printf(f'交易员以单价{openAvgPx}U {lever}倍【买入开多】{instId} ,{subPos}张 ，我开{MyBuyNum}张', 'green')
                            REST.加仓(printf, '开', UserInfo, instId, 'buy', 'long', MyBuyNum, lever, mgnMode)
                        else:
                            printf(f'交易员以单价{openAvgPx}U {lever}倍【卖出开空】{instId} ,{subPos}张 ，我开{MyBuyNum}张', 'red')
                            REST.加仓(printf, '开', UserInfo, instId, 'sell', 'short', MyBuyNum, lever, mgnMode)
                    else:

                        if posSide == 'long':
                            printf(f'交易员以单价{openAvgPx}U {lever}倍【买入开多】{instId} ,{subPos}张 ，我开{MyBuyNum}张', 'green')
                            REST.加仓(printf, '开', UserInfo, instId, 'buy', posSide, MyBuyNum, lever, mgnMode)
                        elif posSide == 'short':
                            printf(f'交易员以单价{openAvgPx}U {lever}倍【卖出开空】{instId} ,{subPos}张 ，我开{MyBuyNum}张', 'red')
                            REST.加仓(printf, '开', UserInfo, instId, 'sell', posSide, MyBuyNum, lever, mgnMode)
            else:

                printf(f"币价小于0.00000001，不开单", 'black')

            # 遍历上一次的字典，判断平仓
        for subPosId in (Last_Pos if not first_time else []):
            # print(subPosId)
            # 如果交易ID在这一次的字典中没有，说明是平仓
            if subPosId not in This_Pos:
                closed_position = Last_Pos[subPosId]
                instId = closed_position["instId"]
                subPos = closed_position["subPos"]
                openAvgPx = closed_position["openAvgPx"]
                posSide = closed_position["posSide"]
                lever = closed_position["lever"]
                mgnMode = closed_position['mgnMode']

                MyBuyNum = custom_round(PositionSize * subPos)

                if posSide == 'net':

                    if float(subPos) > 0:
                        printf(f'交易员以单价{openAvgPx}U {lever}倍【卖出平多】{instId} ,{subPos}张 ，我平{MyBuyNum}张', 'red')
                        REST.加仓(printf, '平', UserInfo, instId, 'sell', 'long', MyBuyNum, lever, mgnMode)
                    else:
                        printf(f'交易员以单价{openAvgPx}U {lever}倍【买入平空】{instId} ,{subPos}张 ，我平{MyBuyNum}张', 'green')
                        REST.加仓(printf, '平', UserInfo, instId, 'buy', 'short', MyBuyNum, lever, mgnMode)
                else:
                    if posSide == 'long':
                        printf(f'交易员以单价{openAvgPx}U {lever}倍【卖出平多】{instId} ,{subPos}张 ，我平{MyBuyNum}张', 'red')
                        REST.加仓(printf, '平', UserInfo, instId, 'sell', posSide, MyBuyNum, lever, mgnMode)
                    elif posSide == 'short':
                        printf(f'交易员以单价{openAvgPx}U {lever}倍【买入平空】{instId} ,{subPos}张 ，我平{MyBuyNum}张', 'green')
                        REST.加仓(printf, '平', UserInfo, instId, 'buy', posSide, MyBuyNum, lever, mgnMode)
    else:

        try:
            printf(f'检测故障(欧易原因)：{json.loads(response.text)["msg"]}', 'Purple')
        except:
            printf(f'检测故障(欧易原因)：{response.text}', 'Purple')

    first_time = False


def start_trading(printf):

    global Last_Pos, This_Pos, first_time, stop_thread_event
    # 提取输入框的内容
    unique_name = unique_name_entry.get()
    my_capital = my_capital_entry.get()
    trader_capital = trader_capital_entry.get()
    api_key = api_key_entry.get()
    secret_key = secret_key_entry.get()
    passphrase = passphrase_entry.get()
    sleep_interval = sleep_entry.get()

    # # api_key = "the_api_key_to_check"
    # # 构建请求URL
    # url = f"https://www.s1wei.com"
    # # 发送GET请求
    # response = requests.get(url)
    # # 处理响应
    # if response.status_code == 200:
    #     if response.text == '0':
    #         printf('未查询到您的api-Key存在授权记录', 'Purple')
    #         stop_thread()
    #     else:
    #         printf('认证成功，欢迎使用', 'blue')
    # else:
    #     printf(f"链接验证服务器失败，请链接网络再试", 'Purple')
    #     stop_thread()

    url = f'https://www.okx.com/cn/copy-trading/trader/{unique_name}/swap/current'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    title_tag = soup.find('title')
    title_text = title_tag.text if title_tag else None
    name = title_text.split()[0] if title_text else None

    if name == 'OKX全球领先的比特币交易平台':
        printf('未查询到交易员，请稍后再试', 'Purple')
    else:
        if stop_thread_event:
            printf(f'启动成功, 监控交易员: {name}', 'blue')

            save_config(unique_name, my_capital, trader_capital, api_key, secret_key, passphrase, sleep_interval, '1')

            printf(f'开始监控跟单：设置交易员本金：{trader_capital}U, 我的本金：{my_capital}U', 'blue')

            PositionSize = float(my_capital)/float(trader_capital)

            UserInfo = {
                'api_key': api_key,
                'secret_key': secret_key,
                'passphrase': passphrase
            }

            # 上一次获取的仓位字典
            Last_Pos = {}

            # 当前获取的仓位字典
            This_Pos = {}

            # 首次获取的标志
            first_time = True

            start_button["text"] = "监控中..."
            while stop_thread_event:
                try:
                    GetTraderdetail(printf, UserInfo, unique_name, PositionSize)
                    time.sleep(float(sleep_interval))
                except Exception as e:
                    if 'Connection' in str(e):
                        printf(f'连接欧易失败{datetime.now().time()} - 少量出现无视即可', 'Purple')
                    else:
                        printf(f'出错了，快联系开发人员:{e}', 'Purple')
                    # first_time = True
                # print('监控中')


def on_closing():
    global stop_thread_event
    # 在关闭窗口时执行的操作
    try:
        if Openbrowser != '1':
            webbrowser.open('https://www.s1wei.com')
    except:
        pass
    root.destroy()  # 销毁 Tkinter 窗口
    stop_thread_event = False
    exit()


if __name__ == '__main__':

    stop_thread_event = False

    # 上一次获取的仓位字典
    Last_Pos = {}

    # 当前获取的仓位字典
    This_Pos = {}

    # 首次获取的标志
    first_time = True

    # 创建主窗口
    root = tk.Tk()
    root.title("欧耶v6.0")
    root.iconbitmap(joinpath(os.path.dirname(__file__), 'icon.ico'))
    # 设置窗口大小为800x400
    root.geometry("830x300")

    # 在窗口关闭时调用 on_closing 函数
    root.protocol("WM_DELETE_WINDOW", on_closing)

    # 创建标签和输入框
    unique_name_label = tk.Label(root, text="交易员unique:")
    unique_name_entry = tk.Entry(root)

    my_capital_label = tk.Label(root, text="我的本金:")
    my_capital_entry = tk.Entry(root)

    trader_capital_label = tk.Label(root, text="交易员本金:")
    trader_capital_entry = tk.Entry(root)

    api_key_label = tk.Label(root, text="API Key:")
    api_key_entry = tk.Entry(root)

    secret_key_label = tk.Label(root, text="Secret Key:")
    secret_key_entry = tk.Entry(root)

    passphrase_label = tk.Label(root, text="Passphrase:")
    passphrase_entry = tk.Entry(root)

    sleep_label = tk.Label(root, text="监控间隔(秒):")
    sleep_entry = tk.Entry(root)


    def start_stop_thread():
        global stop_thread_event
        # print(stop_thread_event)
        if not stop_thread_event:
            start_thread()
        else:
            stop_thread()


    def start_thread():
        global stop_thread_event
        stop_thread_event = True
        threading.Thread(target=start_trading, args=(log_message, )).start()
        start_button["text"] = "停止"

    def stop_thread():
        global stop_thread_event
        stop_thread_event = False
        start_button["text"] = "启动"
        log_message('停止成功', 'blue')

    # 创建启动按钮
    start_button = tk.Button(root, text="启动", command=start_stop_thread, state=tk.NORMAL)

    # 创建日志输出文本框
    log_output = tk.Text(root, width=80, height=16)
    log_output.grid(row=0, column=3, rowspan=6, padx=20)

    # 日志输出函数
    def log_message(message, color):
        log_output.tag_configure(color, foreground=color)
        log_output.insert(tk.END, message + "\n", color)
        log_output.see(tk.END)


    # 使用grid布局管理器布局标签、输入框和按钮
    unique_name_label.grid(row=0, column=0, sticky='w')
    unique_name_entry.grid(row=0, column=1)

    my_capital_label.grid(row=1, column=0, sticky='w')
    my_capital_entry.grid(row=1, column=1)

    trader_capital_label.grid(row=2, column=0, sticky='w')
    trader_capital_entry.grid(row=2, column=1)

    api_key_label.grid(row=3, column=0, sticky='w')
    api_key_entry.grid(row=3, column=1)

    secret_key_label.grid(row=4, column=0, sticky='w')
    secret_key_entry.grid(row=4, column=1)

    passphrase_label.grid(row=5, column=0, sticky='w')
    passphrase_entry.grid(row=5, column=1)

    sleep_label.grid(row=6, column=0, sticky='w')
    sleep_entry.grid(row=6, column=1)

    start_button.grid(row=7, column=1, columnspan=2, pady=10)

    try:
        # 读取上次的配置
        last_unique_name, last_my_capital, last_trader_capital, last_api_key, last_secret_key, last_passphrase, last_sleep_interval, Openbrowser = load_config()

        # 在输入框中填充上次的配置
        unique_name_entry.insert(0, last_unique_name)
        my_capital_entry.insert(0, last_my_capital)
        trader_capital_entry.insert(0, last_trader_capital)
        api_key_entry.insert(0, last_api_key)
        secret_key_entry.insert(0, last_secret_key)
        passphrase_entry.insert(0, last_passphrase)
        sleep_entry.insert(0, last_sleep_interval)
    except:
        pass


    log_message('【通知】请合法规范使用本软件，否则由使用者自行承担责任', 'green')
    log_message('【通知】作者：s1wei，一经发现盗版 or 泛滥 停止维护', 'green')
    log_message('【通知】欢迎使用 灯上云端 www.denceun.cn', 'green')

    # 启动主循环
    root.mainloop()