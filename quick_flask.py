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

prayDirectory="prayTmp/"
prayTable="prayTmp.txt"
prayTablePath=prayDirectory+prayTable



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
    
    if type!="read":
        myfile = open(filename, 'w+')
        if type == "add":
            contents=contents+str+'\n'
        if type == "delete":
            contents=contents.replace(str+'\n',"")
        # Write a line to the file
        myfile.write(contents)
        # Close the file
        myfile.close()
    return contents

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

def check_table(groupID):
    return check_file(prayTablePath,groupID)

def get_tableName(groupID):
    lines=modify_file(prayTablePath,None,"read")
    for line in lines.splitlines():
        if groupID in line:
            return line.split()[1]
    return None
    

def createDirectory(dir):
    if not os.path.exists(dir):
        try:
            os.mkdir(dir)
        except OSError:
            print ("Creation of the directory %s failed" % dir)
        else:
            print ("Successfully created the directory %s " % dir)

def createPrayTable(group_id,tableName):
    if not check_table(group_id):
        modify_file(prayTablePath,group_id+" "+tableName,"add")
        modify_file(prayDirectory+tableName+"1","已確認名單:","add") #1 confirmed people
        modify_file(prayDirectory+tableName+"2","待確認名單:","add") #2 to be confirmed people

def showPrayTable(groupID):
    tableName=get_tableName(groupID)
    clientMessage=tableName+"\n"
    if tableName!=None:
        lines=modify_file(prayDirectory+tableName+"1",None,"read")
        number=0
        for line in lines.splitlines():
            if number>0:
                clientMessage=clientMessage+number+". "+line+"\n"
            else :
                clientMessage=clientMessage+line+"\n"
        clientMessage=clientMessage+"\n"
        lines=modify_file(prayDirectory+tableName+"2",None,"read")
        number=0
        for line in lines.splitlines():
            if number>0:
                clientMessage=clientMessage+number+". "+line+"\n"
            else :
                clientMessage=clientMessage+line+"\n"
        return clientMessage
    return "Need create new pray table"
    


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
    sourceID=get_source(event)
    profile = line_bot_api.get_profile(sourceID['user_id']) #get user profile
    
    if (clientMessage[:2]=="1+" or clientMessage[:2]=="2+") and sourceID['group_id']!=None and check_table(sourceID['group_id']):
        newName=clientMessage[1:]
        if clientMessage[:2]=="1+":
            modify_file(prayDirectory+tableName+"1",newName,"add")
        if clientMessage[:2]=="2+":
            modify_file(prayDirectory+tableName+"2",newName,"add")
    
    if "禱告名單" in clientMessage and sourceID['group_id']!=None:
        createDirectory(prayDirectory)
        
        if "建立禱告名單:" in clientMessage:
            tableName=clientMessage.split(":")[1]
            createPrayTable(sourceID['group_id'],tableName)
            clientMessage="Hi "+profile.display_name+", 已經建立禱告名單:"+tableName
        else :
            if not check_table(sourceID['group_id']):
                clientMessage="Need create new pray table"
            else:
                clientMessage=showPrayTable(sourceID['group_id'])
            clientMessage="Hi "+profile.display_name+"\n"+clientMessage
            
    
    line_bot_api.reply_message(event.reply_token,TextSendMessage(text=clientMessage))
    
    if clientMessageArray[0]=="Fudge" : #"pray table not for personal use"
        
        if "reply" in clientMessage:
            clientMessage=clientMessage.replace("Fudge ","")
            sourceID=get_source(event)
            profile = line_bot_api.get_profile(sourceID['user_id'])
            clientMessage="Hi "+profile.display_name+", "+clientMessage
        
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=clientMessage))
    
    
        
        


if __name__ == "__main__":
    app.run()