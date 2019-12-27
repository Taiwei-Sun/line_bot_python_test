from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

import os

app = Flask(__name__)

line_bot_api = LineBotApi('yjc2B9p8sbGN7jutAUPASpmJUE+AYwjq96P6ErBD7kGZ5P1BWC4aFeznWGQyqUBnzxdUUWonoUvu+oS9fo/Ox2J4I/bXgfv0KqLx4wk/0i8n+pShPRXkT809X3wsP31FEiJAi9dYW/V/GMUL5wS8LAdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('48937fdda35c6bf04da439ff7fb9f5fc')

prayDirectory="prayTmp"


def createDirectory(dir):
    if not os.path.exists(dir):
        try:
            os.mkdir(dir)
        except OSError:
            print ("Creation of the directory %s failed" % dir)
        else:
            print ("Successfully created the directory %s " % dir)




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


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    clientMessage=event.message.text
    clientMessageArray=clientMessage.split()
    if clientMessageArray[0]=="Fudge":
        clientMessage=clientMessage.replace("Fudge ","")
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=clientMessage))
    
    if "禱告名單" in clientMessage:
        createDirectory(prayDirectory)
        
        


if __name__ == "__main__":
    app.run()