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
import psycopg2
import datetime

app = Flask(__name__)

line_bot_api = LineBotApi('yjc2B9p8sbGN7jutAUPASpmJUE+AYwjq96P6ErBD7kGZ5P1BWC4aFeznWGQyqUBnzxdUUWonoUvu+oS9fo/Ox2J4I/bXgfv0KqLx4wk/0i8n+pShPRXkT809X3wsP31FEiJAi9dYW/V/GMUL5wS8LAdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('48937fdda35c6bf04da439ff7fb9f5fc')

prayTableColumns=["table_id","group_id","group_name"]
userTableColumns=["user_id","user_name"]
sessionTableColumns=["session_id","table_id","user_id","userType","addTime","bySomeone"]
prayTable=["prayTable",prayTableColumns]
userTable=["userTable",userTableColumns]
sessionTable=["sessionTable",sessionTableColumns]
userMessage=["userMessage",["message_id","user_id","user_name","message"]]

helpList="""
可用功能
-----------------------------
建立禱告名單:<名單名稱>
更名禱告名單:<名單名稱>
1+<名子>
2+<名子>
-<名子>
-----------------------------

範例:建立禱告名單
-----------------------------
建立禱告名單:2-2區禱告名單二月30號
-----------------------------

範例:增加已確定禱告名單
-----------------------------
1+弟兄三號
-----------------------------

範例:增加還未確定禱告名單
-----------------------------
2+福音朋友二號
-----------------------------

範例:刪除還未確定禱告名單
-----------------------------
-福音朋友二號
-----------------------------


"""


def modify_tables(tableName,columns,row,accessType):
    rows=None
    if columns!=None: columnsLen=len(columns)
    if row!=None: rowLen=len(row)
    if tableName==prayTable[0]: table=prayTable
    elif tableName==userTable[0]: table=userTable
    elif tableName==sessionTable[0]: table=sessionTable
    
    commands = ("SELECT","FROM","WHERE","INSERT INTO","VALUES","UPDATE","SET","DELETE FROM")
    conn = None
    try:
        command=""
        # connect to the PostgreSQL server
        DATABASE_URL = os.environ['DATABASE_URL']
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        cur = conn.cursor()
        # create table one by one
        #for command in commands:
        #    cur.execute(command)
        
        if accessType=='r':
            command=commands[0]+"\n "
            for i in range(columnsLen):
                if i != columnsLen-1: command=command+columns[i]+","
                else: command=command+columns[i]+"\n"
            command=command+commands[1]+" "+tableName+";\n"
            #if row!= None:#only for pray table
            #    command=command[:-2]+"\n"
            #    command=command+commands[2]+" "+
            
            #print("command=\n"+command+"\n")
            cur.execute(command)
            
            #print("The number of parts: ", cur.rowcount)
            
            row = cur.fetchone()
            
            if row!=None:
                rows=[]
                while row is not None:
                    #print(row)
                    rows.append(row)
                    row = cur.fetchone()
            
            
        elif accessType=='i':
            command=commands[3]+" "+tableName+"("
            for i in range(columnsLen):
                if i != columnsLen-1: command=command+columns[i]+","
                else: command=command+columns[i]
            command=command+")\n"+commands[4]+"("
            for i in range(rowLen):
                if i != rowLen-1: command=command+str(row[i])+","
                else: command=command+str(row[i])+");"
            #print("command=\n"+command)
            cur.execute(command)
        elif accessType=='u':
            command=commands[5]+" "+tableName+"\n"
            command=command+" "+commands[6]
            for i in range(1,columnsLen):
                if row[i]==None: continue
                command=command+" "+columns[i]+"="+str(row[i])+","
            command=command[:-1]+'\n'
            command=command+commands[2]+" "+columns[0]+"="+str(row[0])+";"
            #print("command=\n"+command)
            cur.execute(command)
        elif accessType=='d':
            command=commands[7]+" "+tableName+"\n"
            command=command+commands[2]+" "+columns[0]+"="+str(row[0])+";"
            #print("command=\n"+command)
            cur.execute(command)
        
        
        # close communication with the PostgreSQL database server
        cur.close()
        # commit the changes
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
    return rows

def get_id(table,column,str):
    table_id=None
    tableName=table[0]
    rows=modify_tables(tableName,[table[1][0],column],None,'r')
    if rows==None: return None;
    for row in rows:
        if row[1]==str: table_id=row[0]
    return table_id

def get_userName(user_id):
    rows=modify_tables(userTable[0],userTable[1],None,'r')
    for row in rows:
        if row[0]==user_id: return row[1]
    
    return None

def add_prayUser(tableName,userName,userType,provider):
    tableID=str(get_id(prayTable,prayTable[1][2],tableName))
    ts = (datetime.datetime.now()+datetime.timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S')
    ts=ts.split('.')[0]
    if get_id(userTable,userTable[1][1],userName)==None: modify_tables(userTable[0],[userTable[1][1]],["'"+userName+"'"],'i')
    userID=get_id(userTable,userTable[1][1],userName)
    modify_tables(sessionTable[0],[sessionTable[1][1],sessionTable[1][2],sessionTable[1][3],sessionTable[1][4],sessionTable[1][5]],[tableID,userID,str(userType),"'"+ts+"'","'"+provider+"'"],'i')

def delete_prayUser(tableName,userName):
    table_id=get_id(prayTable,prayTable[1][2],tableName)
    user_id=get_id(userTable,userTable[1][1],userName)
    rows=modify_tables(sessionTable[0],sessionTable[1],None,'r')
    for row in rows:
        if row[1]==table_id and row[2]==user_id:
            modify_tables(sessionTable[0],sessionTable[1],[row[0]],'d')
            return True
    return False

#dt_object = datetime.fromtimestamp(timestamp)

def check_DB(tableName,columns,str):
    datas=modify_tables(tableName,columns,None,'r')
    if datas==None: return False
    for data in datas:
        if data[0]==str:
            return True
    return False

def get_source(event):
    if event.source.type == 'user':
        return {'bot_id':os.environ.get('bot_id', None), 'group_id':None, 'user_id':event.source.user_id}
    elif event.source.type == 'group':
        return {'bot_id':os.environ.get('bot_id', None), 'group_id':event.source.group_id, 'user_id':event.source.user_id}
    elif event.source.type == 'room':
        return {'bot_id':os.environ.get('bot_id', None), 'group_id':event.source.room_id, 'user_id':event.source.user_id}
    else:
        raise Exception('event.source.type:%s' % event.source.type)



def check_table(groupID):
    return check_DB("prayTable",[prayTableColumns[1]],groupID)

def get_lastTableName(groupID):
    datas=modify_tables(prayTable[0],[prayTable[1][0],prayTable[1][1],prayTable[1][2]],None,'r')
    lastName=None
    if datas==None:return None
    preID=0
    for i in range(len(datas)):
        if datas[i][1]==groupID and datas[i][0]>preID: 
            lastName=datas[i][2]
            preID=datas[i][0]
    return lastName

def rename_tableName(group_id,newTableName):
    table_id=get_id(prayTable,prayTable[1][1],group_id)
    modify_tables(prayTable[0],[prayTable[1][0],prayTable[1][2]],[table_id,"'"+newTableName+"'"],'u')                                                                                        
    


def createPrayTable(group_id,groupName):
    modify_tables("prayTable",[prayTableColumns[1],prayTableColumns[2]],["'"+group_id+"'","'"+groupName+"'"],'i')

def filter_rows(table_id,rows):
    if rows==None: return [];
    rowsF=[]
    for i in range(len(rows)):
        #print(rows[i][0])
        #print("rows[i][0]==table_id")
        #print(rows[i][0]==table_id)
        if rows[i][0]==table_id: 
            rowsF.append(rows[i])
            #print(rowsF)
    return rowsF


def showPrayTable(group_id):
    table_id=get_id(prayTable,prayTable[1][1],group_id)
    tableName=get_lastTableName(group_id)
    clientMessage=tableName+"\n"
    if table_id!=None:
        rows=modify_tables(sessionTable[0],[sessionTable[1][1],sessionTable[1][2],sessionTable[1][3]],None,'r')
        #print(rows)
        rows=filter_rows(table_id,rows)
        #print(table_id)
        #print(rows)
        number=0
        for row in rows:
            if row[2]==1:
                number=number+1
                userTmp=get_userName(row[1])
                if userTmp!=None: clientMessage=clientMessage+str(number)+". "+userTmp+"\n"
                else: clientMessage=clientMessage+" no user_id="+str(row[1])
        
        clientMessage=clientMessage+"\n"
        clientMessage=clientMessage+"鼓勵中:\n"
        number=0
        for row in rows:
            if row[2]==2:
                number=number+1
                userTmp=get_userName(row[1])
                if userTmp!=None: clientMessage=clientMessage+str(number)+". "+userTmp+"\n"
                else: clientMessage=clientMessage+" no user_id="+str(row[1])

        clientMessage=clientMessage+"\n"
        return clientMessage
    return "not find table, no group_id="+group_id
    

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
    tableName=get_lastTableName(sourceID['group_id'])
    
    if sourceID['group_id']!=None:#for group
        if (clientMessage[:2]=="1+" or clientMessage[:2]=="2+" or clientMessage[:1]=="-") and check_table(sourceID['group_id']):
            newName=clientMessage[2:]
            if clientMessage[:2]=="1+":
                add_prayUser(tableName,newName,1,profile.display_name)
                sendMessage="Hi "+profile.display_name+" 已經加入確認名單 "+newName
            if clientMessage[:2]=="2+":
                add_prayUser(tableName,newName,2,profile.display_name)
                sendMessage="Hi "+profile.display_name+" 已經加入待確認名單 "+newName
            if clientMessage[:1]=="-":
                newName=clientMessage[1:]
                print("clientMessage[:1]==\"-\"")
                if delete_prayUser(tableName,newName): sendMessage="Hi "+profile.display_name+" 已經刪除名單 "+newName
                else: sendMessage="Hi "+profile.display_name+" "+newName+" 名子不存在"
            
            
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text=sendMessage))
        
        if "禱告名單" in clientMessage and sourceID['group_id']!=None:
            
            if "help" in clientMessage or "Help" in clientMessage or "HELP" in clientMessage :
                sendMessage=helpList
            elif "建立禱告名單" in clientMessage:
                newTableName=clientMessage[7:]#mark clientMessage.split(":")[1]
                #if get_id(prayTable,prayTable[1][1],sourceID['group_id'])==None:
                if tableName==None:
                    createPrayTable(sourceID['group_id'],newTableName)
                    sendMessage="Hi "+profile.display_name+", 已經建立禱告名單:"+newTableName
                else:
                    sendMessage="Hi "+profile.display_name+", 已經存在 禱告名單:"+tableName+"\n可以使用\n更名禱告名單:"+newTableName
            elif "更名禱告名單" in clientMessage:
                newTableName=clientMessage[7:]
                rename_tableName(sourceID['group_id'],newTableName)
                sendMessage="Hi "+profile.display_name+", 已經更新禱告名單:"+tableName
            else :
                if not check_table(sourceID['group_id']):
                    sendMessage="請建立禱告名單 範例: '建立禱告名單:2-2區禱告名單二月30號'"
                else:
                    sendMessage=showPrayTable(sourceID['group_id'])
                sendMessage="Hi "+profile.display_name+"\n"+sendMessage
                
                
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text=sendMessage))
            
            
        
    else:# for personal
        messageLen=len(clientMessage)
        sendMessage="Hi "+profile.display_name+", "+clientMessage #" It cannot be used for personal use"
        for i in range(int(messageLen/100)):
            tmpMessage=clientMessage[:100]
            clientMessage=clientMessage[100:]
            modify_tables(userMessage[0],[userMessage[1][1],userMessage[1][2],userMessage[1][3]],["'"+sourceID['user_id']+"'","'"+profile.display_name+"'","'"+tmpMessage+"'"],'i')
        
        modify_tables(userMessage[0],[userMessage[1][1],userMessage[1][2],userMessage[1][3]],["'"+sourceID['user_id']+"'","'"+profile.display_name+"'","'"+clientMessage+"'"],'i')
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=sendMessage))
    
    
    if clientMessageArray[0]=="Fudge" : #"pray table not for personal use"
        
        if "reply" in clientMessage:
            sendMessage=clientMessage.replace("Fudge ","")
            sourceID=get_source(event)
            profile = line_bot_api.get_profile(sourceID['user_id'])
            sendMessage="Hi "+profile.display_name+", "+sendMessage
        
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=sendMessage))
           
        


if __name__ == "__main__":
    app.run()