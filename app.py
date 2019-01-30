from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *
import json

app = Flask(__name__)

# Channel Access Token
line_bot_api = LineBotApi('vlgEBYCHqjedWeOr0LghZpXN7KALtdXebquusc3WHQOPBwEGujQZ0c/fbA51Kb4kyHvJ335W8D35WeORu7i26jnjYK7T4Nuf5jLhZvByrEnIDggnhcbT1Jdaw6b5TWsrfIiGn3XKuvNHn3z1yVE9lQdB04t89/1O/w1cDnyilFU=')
# Channel Secret
handler = WebhookHandler('dfaf82e2cd7fae694b3d6fc9bc691dac')

# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

#-----------------------從此處開始-----------------------------

def get_data():
    with open("data.json",'r') as load_data:
        return json.load(load_data)

def write(new_data):
    with open("data.json","w") as file:
        json.dump(new_data,file)

def login(data,user_id):
    for i in range(len(data["users"])):
        if data["users"][i]["id"] == user_id:
            return i
    return -1

def signup(data,event):
    message = TemplateSendMessage(
        alt_text='您叫做'+event.message.text+'嗎?',
        template=ConfirmTemplate(
            text='初次使用需要登記姓名\n您叫做'+event.message.text+'嗎?',
            actions=[
                PostbackTemplateAction(
                    label='對',
                    data='0`t`'+event.message.text
                ),
                PostbackTemplateAction(
                    label='不對',
                    data='0`f'
                )
            ]
        )
    )
    line_bot_api.reply_message(event.reply_token, message)

def check_data(new_data):
    if get_data()["ver"] == new_data["ver"]-1:
        return True
    else:
        return False

def restart():
    write({
        "ver": 0, 
        "users": []
    })

def open_atm_ui(data,client_index):
    URL = "line://app/1597095214-Y1BrG15q?p="
    for i in range(len(data["users"])):
        if i != client_index:
            if i >= len(data["users"]):
                URL+=data["users"][i]["name"]
            else:
                URL+=data["users"][i]["name"]+"-"

    line_bot_api.push_message(data["users"][client_index]["id"], 
        TemplateSendMessage(
            alt_text='開啟ATM面板',
            template=ConfirmTemplate(
                text="帳戶餘額："+str(data["users"][i]["balance"])+"元",
                actions=[
                    URITemplateAction(
                        label='開啟',
                        uri=URL
                    ),
                    URITemplateAction(
                        label='ATM',
                        uri=URL
                    )
                ]
            )
        )
    )

def check_money(str_money):
    try:
        if int(str_money) <= 0:
            return False
        else:
            return True
    except:
        return False

def broadcast(data,client_index,output):
    for i in range(len(data["users"])):
        if i != client_index:
            line_bot_api.push_message(data["users"][i]["id"],
                    TextSendMessage(text=output))

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    try:
        data = get_data()
        client_index = login(data,event.source.user_id)
        command = event.message.text.split(',')
        if client_index == -1 :
            signup(data,event)
        elif command[0] == "restart":
            restart()
        elif command[0] == "帳戶餘額":
            open_atm_ui(data,client_index)
        elif command[0] == "pay":
            if check_money(command[1]):
                money = int(command[1])
                if money <= data["users"][client_index]["balance"]:
                    #確保資料正確性
                    while True:
                        data = get_data()
                        data["users"][client_index]["balance"] -= money
                        data["ver"] += 1
                        if check_data(data):
                            write(data)
                            break
                    #-------------
                    line_bot_api.push_message(event.source.user_id,
                        TextSendMessage(text="你向銀行繳付了"+command[1]+"元"))
                    open_atm_ui(data,client_index)
                    broadcast(data,client_index,
                        data["users"][client_index]["name"]+"繳付了"+command[1]+"元")
                else:
                    line_bot_api.push_message(event.source.user_id,TextSendMessage(
                            text="付款失敗：錢不夠啦!("+str(data["users"][client_index]["balance"])+")"))
            else:
                line_bot_api.push_message(event.source.user_id,
                    TextSendMessage(text="付款失敗：輸入格式有誤"))
        elif command[0] == "get":
            if check_money(command[1]):
                #確保資料正確性
                while True:
                    data = get_data()
                    data["users"][client_index]["balance"] += int(command[1])
                    data["ver"] += 1
                    if check_data(data):
                        write(data)
                        break
                #-------------
                line_bot_api.push_message(event.source.user_id,
                    TextSendMessage(text="你向銀行請領了"+command[1]+"元"))
                open_atm_ui(data,client_index)
                broadcast(data,client_index,
                    data["users"][client_index]["name"]+"向銀行請領了"+command[1]+"元")
            else:
                line_bot_api.push_message(event.source.user_id,
                    TextSendMessage(text="請款失敗：輸入格式有誤"))
        elif command[0] == "give":
            if check_money(command[2]):
                money = int(command[2])
                if money <= int(data["users"][client_index]["balance"]):
                    finded = False
                    for i in range(len(data["users"])):
                        if data["users"][i]["name"] == command[1]:
                            finded = True
                            #確保資料正確性
                            while True:
                                data = get_data()
                                data["users"][i]["balance"]+=money
                                data["users"][client_index]["balance"]-=money
                                data["ver"] += 1
                                if check_data(data):
                                    write(data)
                                    break
                            #-------------
                            line_bot_api.push_message(event.source.user_id,
                                TextSendMessage(text="你匯給"+data["users"][i]["name"]+command[2]+"元"))
                            open_atm_ui(data,client_index)
                            line_bot_api.push_message(data["users"][i]["id"],TextSendMessage(
                                text=data["users"][client_index]["name"]+"匯給你"+command[2]+"元"))
                            open_atm_ui(data,i)
                    if not finded:
                        line_bot_api.push_message(event.source.user_id,
                                TextSendMessage(text="找不到此匯款對象("+command[1]+")"))
                else:
                    line_bot_api.push_message(event.source.user_id,TextSendMessage(
                        text="匯款失敗：錢不夠啦!("+data["users"][client_index]["balance"]+")"))
            else:
                line_bot_api.push_message(event.source.user_id,
                    TextSendMessage(text="匯款失敗：輸入格式有誤"))
        else:
            open_atm_ui(data,client_index)
    except Exception as e:
        line_bot_api.push_message(event.source.user_id,
            TextSendMessage(text="歐歐!發生了一點錯誤!\n"+
                "錯誤段落:handle_message()\n"+
                "錯誤訊息:"+str(e)))

@handler.add(PostbackEvent)
def handle_postback(event):
    try:
        data = get_data()
        client_index = login(data,event.source.user_id)
        command = event.postback.data.split('`')
        #註冊用
        if command[0] == '0' and client_index == -1:
            if command[1] == 't':
                #確保資料正確性
                while True:
                    data = get_data()
                    data["users"].append({
                        "id":event.source.user_id,
                        "name":command[2],
                        "balance":15000
                    })
                    data["ver"] += 1
                    if check_data(data):
                        write(data)
                        break
                #-------------
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text="註冊成功，努力成為大富翁吧!!"))
                client_index = login(data,event.source.user_id)
                open_atm_ui(data,client_index)
            elif command[1] == 'f':
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text="請再次輸入您的姓名"))
        
    except Exception as e:
        line_bot_api.push_message(event.source.user_id,
            TextSendMessage(text="歐歐!發生了一點錯誤!\n"+
                "錯誤段落:handle_postback()\n"+
                "錯誤訊息:"+str(e)))

@handler.add(FollowEvent)
def handle_follow(event):
    line_bot_api.reply_message(event.reply_token, 
        TextSendMessage(text="初次使用需輸入姓名，請問您的名字是?"))

#-----------------------到此處結束-----------------------------

import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)