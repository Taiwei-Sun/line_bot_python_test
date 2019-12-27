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
prayTable="prayTmp.txt"
prayTablePath=prayDirectory+'/'+prayTable

def get_source(event):
    if event.source.type == 'user':
        return {'bot_id':os.environ.get('bot_id', None), 'group_id':None, 'user_id':event.source.user_id}
    elif event.source.type == 'group':
        return {'bot_id':os.environ.get('bot_id', None), 'group_id':event.source.group_id, 'user_id':event.source.user_id}
    elif event.source.type == 'room':
        return {'bot_id':os.environ.get('bot_id', None), 'group_id':event.source.room_id, 'user_id':event.source.user_id}
    else:
        raise Exception('event.source.type:%s' % event.source.type)
        
def modify_file(filename,str,type):
    contents=""
    if os.path.exists(filename):
        myfileR = open(filename, 'r')
        contents =myfileR.read()
        myfileR.close()
    
    myfile = open(filename, 'w+')
    
    if type == "add":
        contents=contents+str+'\n'
    
    if type == "delete":
        contents=contents.replace(str+'\n',"")
    
    # Write a line to the file
    myfile.write(contents)
    # Close the file
    myfile.close()

def check_file(filename,str):
    contents=""
    if os.path.exists(filename):
        myfileR = open(filename, 'r')
        contents =myfileR.read()
        myfileR.close()
    if str+'\n' in contents:
        return True
    else :
        return False

def check_table(tablesID):
    return check_file(prayTablePath,tablesID)


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
        
        
        
        if "禱告名單" in clientMessage:
            createDirectory(prayDirectory)
            sourceID=get_source(event)
            if check_table(sourceID['group_id']):
                clientMessage="table exists"
            else:
                clientMessage="Need create new pray table"
            profile = line_bot_api.get_profile(sourceID['user_id'])
            clientMessage="Hi "+profile.display_name+" "+clientMessage
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text=clientMessage))
            
        if "reply" in clientMessage:
            clientMessage=clientMessage.replace("Fudge ","")
            sourceID=get_source(event)
            profile = line_bot_api.get_profile(sourceID['user_id'])
            clientMessage="Hi "+profile.display_name+" "+clientMessage
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text=clientMessage))
    
    
        
        


if __name__ == "__main__":
    app.run()