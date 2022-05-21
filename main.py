# 这是一个示例 Python 脚本。

# 按 Shift+F10 执行或将其替换为您的代码。
# 按 双击 Shift 在所有地方搜索类、文件、工具窗口、操作和设置。


import telebot
from telebot import apihelper
import json
import os
import schedule

import websockets
import requests
import asyncio

os.environ["http_proxy"] = "http://127.0.0.1:7890"
os.environ["https_proxy"] = "http://127.0.0.1:7890"
os.environ["socks5"] = "http://127.0.0.1:7890"

print('运行成功！')
r = requests.get('https://api2.binance.com/api/v3/ticker/price')
print(r.json())
proxies = {'http': "socks5://127.0.0.1:7890",
           'https': "socks5://127.0.0.1:7890"}
bot = telebot.TeleBot("5378351752:AAFek7mwdQOL1yx_HNn741hJamgFRMJS0aY")
chat_id = '685775649'
bot.send_message(chat_id, "运行成功！")
current_price = ""
every_min_send = 5
current_min_send = 0


def send_message(message):
    current_min_send = current_min_send + 1
    bot.send_message(chat_id, message)
    print(current_min_send)


def clean_send_sum():
    current_min_send = 0
    print(current_min_send)


schedule.every(10).minutes.do(clean_send_sum)


async def main_logic():
    # async with websockets.connect('wss://stream.binance.com:9443/ws/lunabusd@kline_1m', ping_timeout=10) as websocket:
    async with websockets.connect('wss://stream.binance.com:9443/ws', ping_timeout=10) as websocket:
        await websocket.send(json.dumps({
            "method": "SUBSCRIBE",
            "params":
                [
                    "lunabusd@aggTrade",
                    "lunabusd@kline_1m"
                ],
            "id": 2
        }))
        while True:
            response_str = await websocket.recv()
            data = json.loads(response_str)
            # print("接受服务端返回信息: ", data)
            try:
                if 'p' in data:
                    current_price = data['p']
                    print("当前价格: ", data["p"])
                elif 'k' in data:
                    k = data["k"]
                    cjl = data["k"]['v']
                    cjl_f = float(cjl)
                    cjl_f = cjl_f / 100000000
                    cjl_f = float(format(cjl_f, '.2f'))
                    last = float(k['c'])
                    first = float(k['o'])
                    # high = float(format(high, '.3f'))
                    # low = float(format(low, '.3f'))
                    last = float(last)
                    first = float(first)
                    print('当前成交量:', cjl_f)
                    is_f = '+'
                    if last > first:
                        zfl = last - first
                        zf = zfl / first
                        is_f = '+'
                    else:
                        zfl = first - last
                        zf = zfl / last
                        is_f = '-'
                    zf = format(zf, '.5f')
                    zf = float(zf) * 100
                    print(f'振幅:{is_f}', zf, '%')
                    if cjl_f > 15:
                        send_message(f'当前成交量超过{cjl_f}亿,当前价格:{current_price}')
                    if float(zf) > 0.5:
                        send_message(f'当前震荡超过{is_f}{zf}%,当前价格:{current_price}')
            except:
                print("异常解析")
                
asyncio.get_event_loop().run_until_complete(main_logic())

