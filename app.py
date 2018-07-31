from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *

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

# 處理訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    message = TemplateSendMessage(
        alt_text='天氣模板',
        template=CarouselTemplate(
            columns=[
                CarouselColumn(
                    thumbnail_image_url='https://ananedu.com/a/5/9/images/imge015.jpg',
                    title='板橋區',
                    text='12:00 晴天\n溫度:30°\n降雨機率:2%',
                    actions=[
                        PostbackTemplateAction(
                            label='詳細資料',
                            data='12'
                        )
                    ]
                ),
                CarouselColumn(
                    thumbnail_image_url='https://ananedu.com/a/5/9/images/imge015.jpg',
                    title='板橋區',
                    text='13:00 晴天\n溫度:32°\n降雨機率:0%',
                    actions=[
                        PostbackTemplateAction(
                            label='詳細資料',
                            data='13'
                        )
                    ]
                ),
                CarouselColumn(
                    thumbnail_image_url='https://ananedu.com/a/5/9/images/imge011.jpg',
                    title='板橋區',
                    text='14:00 雨天\n溫度:25°\n降雨機率:86%',
                    actions=[
                        PostbackTemplateAction(
                            label='詳細資料',
                            data='14'
                        )
                    ]
                )
            ]
        )
    )
    line_bot_api.reply_message(event.reply_token, message)
    
@handler.add(PostbackEvent)
def handle_postback(event):
    if event.postback.data == '12':
        line_bot_api.reply_message(event.reply_token, 
            TextSendMessage(text='板橋\n12:00 晴天\n溫度:30°\n降雨機率:2%\n空氣品質:差\n紫外線:高'))
    if event.postback.data == '13':
        line_bot_api.reply_message(event.reply_token, 
            TextSendMessage(text='板橋\n13:00 晴天\n溫度:32°\n降雨機率:0%\n空氣品質:差\n紫外線:過高'))
    if event.postback.data == '14':
        line_bot_api.reply_message(event.reply_token, 
            TextSendMessage(text='板橋\n14:00 雨天\n溫度:25°\n降雨機率:86%\n空氣品質:普通\n紫外線:普通'))

import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
