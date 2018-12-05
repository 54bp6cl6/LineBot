from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *
import requests
import random
import time

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

#user類別
class user:
    def __init__(self,ID,Q):
        self.ID = ID
        self.Q = Q

#讀取成員名單
def GetUserList():
    url = "https://script.google.com/macros/s/AKfycbwVs2Si91yKz6m3utpaPtsttbh_lUQ8LOQM3Zud2hPFxXCgW3u1/exec"
    payload = {
        'sheetUrl':"https://docs.google.com/spreadsheets/d/1mlxmS0MYfBHSqiRLjaKyqNBvYZZHIGLwsbxr6FENdn4/edit#gid=0",
        'sheetTag':"成員列表",
        'row': 1,
        'col': 1,
        'endRow' : 51,
        'endCol' : 2
    }
    resp = requests.get(url, params=payload)
    temp = resp.text.split(',')
    userlist = []
    i = 0
    while i < len(temp):
        if temp[i] != "":
            userlist.append(user(temp[i],temp[i+1]))
            i+=2
        else:
            break
    return userlist

#登入
def Login(user_id,userlist):
    for user in userlist:
        if user.ID == user_id:
            return userlist.index(user)
    return -1

#註冊
def Signup(user_id):
    url = "https://script.google.com/macros/s/AKfycbxn7Slc2_sKHTc6uEy3zmm3Bh_4duiGCXLavUM3RB0a3yzjAxc/exec"
    payload = {
        'sheetUrl':"https://docs.google.com/spreadsheets/d/1mlxmS0MYfBHSqiRLjaKyqNBvYZZHIGLwsbxr6FENdn4/edit#gid=0",
        'sheetTag':"成員列表",
        'data':user_id+',-1'
    }
    requests.get(url, params=payload)
    
def Write(x,data):
    url = "https://script.google.com/macros/s/AKfycbyBbQ1lsq4GSoKE0yiU5d6x0z2EseeBNZVTewWlSZhQ6EVrizo/exec"
    payload = {
        'sheetUrl':"https://docs.google.com/spreadsheets/d/1mlxmS0MYfBHSqiRLjaKyqNBvYZZHIGLwsbxr6FENdn4/edit#gid=0",
        'sheetTag':"成員列表",
        'data':data,
        'x':str(x+1),
        'y':'2'
    }
    requests.get(url, params=payload)
    
#對答案
def Ans(Q, ans):
    if Q == 0:
        if ans.find('芝麻街') >= 0:
            return "答對了"
        else:
            return "錯，答案是「芝麻街」，因為芝麻街美語(沒雨)"
    elif Q == 1:
        if ans.find('冰淇淋') >= 0:
            return "答對了"
        else:
            return "錯，答案是「冰淇淋(麒麟)」"
    elif Q == 2:
        if ans.find('平行線') >= 0:
            return "答對了"
        else:
            return "錯，答案是「平行線」，因為沒有相交(香蕉)"
    elif Q == 3:
        if ans.find('虱目魚') >= 0 or ans.find('濕木魚') >= 0:
            return "答對了"
        else:
            return "錯，答案是「虱目魚」(濕木魚)"
    elif Q == 4:
        if ans.find('布丁狗') >= 0 or ans.find('不叮狗') >= 0:
            return "答對了"
        else:
            return "錯，答案是「布丁狗」(不叮狗)"

# 處理訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    try:
        userlist = GetUserList()
        clientindex = Login(event.source.user_id,userlist)
        if clientindex == -1:
            Signup(event.source.user_id)
            userlist = GetUserList()
            clientindex = Login(event.source.user_id,userlist)
        Q = int(userlist[clientindex].Q)
        #開始使用功能
        if Q < 0:
            ran = random.randint(0,9)
            if ran == 0:
                line_bot_api.reply_message(event.reply_token,TextSendMessage(text="哪一條街永遠不下雨?"))
            elif ran == 1:
                line_bot_api.reply_message(event.reply_token,TextSendMessage(text="麒麟飛到北極會變成什麼?"))
            elif ran == 2:
                line_bot_api.reply_message(event.reply_token,TextSendMessage(text="猴子最討厭哪一種線?"))
            elif ran == 3:
                line_bot_api.reply_message(event.reply_token,TextSendMessage(text="木魚掉進海裡會變成什麼?"))
            elif ran == 4:
                line_bot_api.reply_message(event.reply_token,TextSendMessage(text="有一隻蚊子牠只叮[鼠牛虎兔龍蛇馬羊猴雞豬]，請問這隻蚊子叫什麼名字?"))
            elif ran == 5:
                line_bot_api.reply_message(
                    event.reply_token,TemplateSendMessage(
                        alt_text='猜題面板(手機限定)',
                        template=ButtonsTemplate(
                            thumbnail_image_url='logo.png',
                            title='題目',
                            text='狼、老虎和獅子誰玩遊戲一定會被淘汰?',
                            actions=[
                                PostbackTemplateAction(
                                    label='狼',
                                    data='1`t'
                                ),
                                PostbackTemplateAction(
                                    label='老虎',
                                    data='1`f'
                                ),
                                PostbackTemplateAction(
                                    label='獅子',
                                    data='1`f'
                                )
                            ]
                        )
                    )
                )
            elif ran == 6:
                line_bot_api.reply_message(event.reply_token,
                    TemplateSendMessage(
                        alt_text='猜題面板(手機限定)',
                        template=ButtonsTemplate(
                            thumbnail_image_url='logo.png',
                            title='題目',
                            text='孔子有三位徒弟子貢、子路、和子游,請問哪一位不是人?',
                            actions=[
                                PostbackTemplateAction(
                                    label='子貢',
                                    data='1`f'
                                ),
                                PostbackTemplateAction(
                                    label='子路',
                                    data='1`t'
                                ),
                                PostbackTemplateAction(
                                    label='子游',
                                    data='1`f'
                                )
                            ]
                        )
                    )
                )
            elif ran == 7:
                line_bot_api.reply_message(event.reply_token,
                    TemplateSendMessage(
                        alt_text='猜題面板(手機限定)',
                        template=ButtonsTemplate(
                            thumbnail_image_url='logo.png',
                            title='題目',
                            text='獅子、狼、熊，哪一隻的牙齒最好?',
                            actions=[
                                PostbackTemplateAction(
                                    label='獅子',
                                    data='1`f'
                                ),
                                PostbackTemplateAction(
                                    label='狼',
                                    data='1`t'
                                ),
                                PostbackTemplateAction(
                                    label='熊',
                                    data='1`f'
                                )
                            ]
                        )
                    )
                )
            elif ran == 8:
                line_bot_api.reply_message(event.reply_token,
                    TemplateSendMessage(
                        alt_text='猜題面板(手機限定)',
                        template=ButtonsTemplate(
                            thumbnail_image_url='logo.png',
                            title='題目',
                            text='喵喵、吱吱 、旺旺誰會最先被叫起來背書?',
                            actions=[
                                PostbackTemplateAction(
                                    label='喵喵',
                                    data='1`f'
                                ),
                                PostbackTemplateAction(
                                    label='吱吱',
                                    data='1`f'
                                ),
                                PostbackTemplateAction(
                                    label='旺旺',
                                    data='1`t'
                                )
                            ]
                        )
                    )
                )
            elif ran == 9:
                line_bot_api.reply_message(event.reply_token,
                    TemplateSendMessage(
                        alt_text='猜題面板(手機限定)',
                        template=ButtonsTemplate(
                            thumbnail_image_url='logo.png',
                            title='題目',
                            text='蝴蝶, 蜘蛛, 蜈蚣, 哪一個沒有領到酬勞?',
                            actions=[
                                PostbackTemplateAction(
                                    label='蝴蝶',
                                    data='1`f'
                                ),
                                PostbackTemplateAction(
                                    label='蜘蛛',
                                    data='1`f'
                                ),
                                PostbackTemplateAction(
                                    label='蜈蚣',
                                    data='1`t'
                                )
                            ]
                        )
                    )
                )
            Write(clientindex,ran)
        elif Q < 5:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=Ans(Q ,event.message.text)))
            Write(clientindex,-1)
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="要回答請點擊題目下方的按鈕喔"))
    except Exception as e:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=str(e)))

@handler.add(PostbackEvent)
def handle_postback(event):
    userlist = GetUserList()
    clientindex = Login(event.source.user_id,userlist)
    data = event.postback.data.split('`')
    #註冊用
    if data[0] == '0' and clientindex < 0:
        if data[1] == 't':
            Signup(event.source.user_id,data[2])
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="註冊成功，歡迎來到LineBot世界"))
        elif data[1] == 'f':
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="請再次輸入您的姓名"))
    elif data[0] == '1':
        userlist = GetUserList()
        clientindex = Login(event.source.user_id,userlist)
        Q = int(userlist[clientindex].Q)
        if data[1] == 't' and Q > 4:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="答對了"))
        else:
            if Q == 5:
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text="錯，答案是「狼」，因為「桃太郎」(淘汰狼)"))
            elif Q == 6:
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text="錯，答案是「子路」，因為「指鹿(子路)為馬」"))
            elif Q == 7:
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text="錯，答案是「狼」，因為「狼牙棒」"))
            elif Q == 8:
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text="錯，答案是「旺旺」，因為「旺旺仙貝(先背)」"))
            elif Q == 9:
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text="錯，答案是「蜈蚣」，因為「無功(蜈蚣)不受祿」"))
        if Q > 4:
            Write(clientindex,-1)
import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
