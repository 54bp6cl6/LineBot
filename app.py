from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *
import requests

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

#user類別
class user:
    def __init__(self,ID,Name,Balance,Step,Situation):
        self.Name = Name
        self.ID = ID
        self.Balance = int(Balance)
        self.Step = int(Step)
        self.Situation = Situation

#讀取成員名單
def GetUserList():
    url = "https://script.google.com/macros/s/AKfycbwVs2Si91yKz6m3utpaPtsttbh_lUQ8LOQM3Zud2hPFxXCgW3u1/exec"
    payload = {
        'sheetUrl':"https://docs.google.com/spreadsheets/d/1PQsud7dyau5wrR5Eu26aW2O17zxysmVY8Ib69XUDnnQ/edit#gid=0",
        'sheetTag':"users",
        'row': 1,
        'col': 1,
        'endRow' : 51,
        'endCol' : 20
    }
    resp = requests.get(url, params=payload)
    temp = resp.text.split(',')
    userlist = []
    i = 0
    while i < len(temp):
        if temp[i] != "":
            userlist.append(user(temp[i],temp[i+1],temp[i+2],temp[i+3],temp[i+4]))
            i+=5
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
def Signup(user_id,name):
    url = "https://script.google.com/macros/s/AKfycbxn7Slc2_sKHTc6uEy3zmm3Bh_4duiGCXLavUM3RB0a3yzjAxc/exec"
    payload = {
        'sheetUrl':"https://docs.google.com/spreadsheets/d/1PQsud7dyau5wrR5Eu26aW2O17zxysmVY8Ib69XUDnnQ/edit#gid=0",
        'sheetTag':"users",
        'data':user_id+','+name+',15000,1'
    }
    requests.get(url, params=payload)

def Write(clientindex,data,index):
    url = "https://script.google.com/macros/s/AKfycbyBbQ1lsq4GSoKE0yiU5d6x0z2EseeBNZVTewWlSZhQ6EVrizo/exec"
    payload = {
        'sheetUrl':"https://docs.google.com/spreadsheets/d/1PQsud7dyau5wrR5Eu26aW2O17zxysmVY8Ib69XUDnnQ/edit#gid=0",
        'sheetTag':"users",
        'data':data,
        'x':str(clientindex+1),
        'y':index
    }
    requests.get(url, params=payload)

def GetActions(event,userlist,clientindex):
    out = []
    for user in userlist:
        if user.ID != userlist[clientindex].ID:
            out.append(
                PostbackTemplateAction(
                    label=user.Name,
                    data='1`'+str(userlist[clientindex].Step + 1)+"`"+user.Name
                )
            )
    out.append(
        PostbackTemplateAction(
            label="取消",
            data='-1`'
        )
    )
    return out

def Play(event,userlist,clientindex):
    temp = userlist[clientindex].Situation.split('`')
    if event.message.text.find("取消") != -1 and temp[0] != '0':
        Write(clientindex,str(userlist[clientindex].Step+1),'4')
        Write(clientindex,'0','5')
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="你取消了交易"))
    elif temp[0] == '0':
        if event.message.text.find("restart") != -1:
            i = 0
            for user in userlist:
                Write(i,"15000",'3')
                Write(i,"1",'4')
                Write(i,"0",'5')
                line_bot_api.push_message(user.ID, TextSendMessage(text=userlist[clientindex].Name+"重啟了遊戲，你的存款變成了15000元"))
                i+=1
        elif event.message.text == "匯款":
            line_bot_api.reply_message(event.reply_token, 
                TemplateSendMessage(
                    alt_text='匯款視窗',
                    template=ButtonsTemplate(
                        thumbnail_image_url='https://raw.githubusercontent.com/54bp6cl6/LineBot/Monopoly/image1.jpg',
                        title='匯款',
                        text='你要匯款給誰？',
                        actions=GetActions(event,userlist,clientindex)
                    )
                )
            )
            Write(clientindex,str(userlist[clientindex].Step+1),'4')
        elif event.message.text == "領錢":
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="你要向銀行請領多少錢？"))
            Write(clientindex,'2','5')
        elif event.message.text == "付錢":
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="你要繳交多少錢？"))
            Write(clientindex,'3','5')
        elif event.message.text == "帳戶餘額":
            out = "----------------------"
            for user in userlist:
                out += user.Name + ":" + str(user.Balance) + "元\n"
            out += "----------------------"
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=out))
    #匯款
    elif temp[0] == '1':
        try:
            if event.message.text != '0':
                int(event.message.text)
                Write(clientindex,str(userlist[clientindex].Step + 1),'4')
                Write(clientindex,str(userlist[clientindex].Balance - int(event.message.text)),'3')
                Write(clientindex,'0','5')
                i=0
                for user in userlist:
                    if user.Name == temp[1]:
                        Write(i,str(userlist[i].Balance + int(event.message.text)),'3')
                        line_bot_api.push_message(user.ID, TextSendMessage(text=userlist[clientindex].Name+"匯給你"+event.message.text+"元"))
                        break
                    i+=1
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text="你匯給了"+temp[1]+event.message.text+"元"))
            else:
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text="不能匯0元啦!!!"))
        except:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='輸入錯誤，請輸入數字，\n並注意不要包含任何空格\n若要取消，請輸入\"取消\"'))
    #領錢
    elif temp[0] == '2':
        try:
            if event.message.text != '0':
                int(event.message.text)
                Write(clientindex,str(userlist[clientindex].Balance + int(event.message.text)),'3')
                Write(clientindex,'0','5')
                for user in userlist:
                    if user.Name != userlist[clientindex].Name:
                        line_bot_api.push_message(user.ID, TextSendMessage(text=userlist[clientindex].Name+"向銀行請領了"+event.message.text+"元"))
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text="你向銀行請領了"+event.message.text+"元"))
            else:
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text="沒有人在請領0元的啦!!!"))
        except:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='輸入錯誤，請輸入數字，\n並注意不要包含任何空格\n若要取消，請輸入\"取消\"'))
    #付錢
    elif temp[0] == '3':
        try:
            if event.message.text != '0':
                int(event.message.text)
                Write(clientindex,str(userlist[clientindex].Balance - int(event.message.text)),'3')
                Write(clientindex,'0','5')
                for user in userlist:
                    if user.Name != userlist[clientindex].Name:
                        line_bot_api.push_message(user.ID, TextSendMessage(text=userlist[clientindex].Name+"繳交了"+event.message.text+"元給銀行"))
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text="你繳交了"+event.message.text+"元給銀行"))
            else:
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text="沒有人罰錢罰0元的啦!!!"))
        except:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='輸入錯誤，請輸入數字，\n並注意不要包含任何空格\n若要取消，請輸入\"取消\"'))

# 處理訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    try:
        userlist = GetUserList()
        clientindex = Login(event.source.user_id,userlist)
        if clientindex > -1:
            #開始使用功能
            Play(event,userlist,clientindex)
        else:
            message = TemplateSendMessage(
                alt_text='註冊面板',
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
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="註冊成功，努力成為大富翁吧!!"))
        elif data[1] == 'f':
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="請再次輸入您的姓名"))
    ##取消
    elif data[0] == '-1' and userlist[clientindex].Situation!="0":
        if userlist[clientindex].Situation!=0:
            Write(clientindex,str(userlist[clientindex].Step+1),'4')
            Write(clientindex,'0','5')
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="你取消了交易"))
    ##匯款
    elif data[0] == '1':
        if int(data[1]) == userlist[clientindex].Step:
            Write(clientindex,"1`"+data[2],'5')
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="要匯給"+data[2]+"多少錢"))
            Write(clientindex,str(userlist[clientindex].Step+1),4)


    
@handler.add(FollowEvent)
def handle_follow(event):
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text="初次使用需輸入姓名，請問您的名字是?"))
    
import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)