#test2
#123
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


prayDirectory="prayTmp/"
prayTable="prayTmp.txt"
prayTablePath=prayDirectory+prayTable

def test_tables():
    """ create tables in the PostgreSQL database"""
    commands = (
        """
        INSERT INTO prayTable(group_id,group_name)
        VALUES('ggid','ggname');
        """,
        """ 
        SELECT
            table_id,
            group_id,
            group_name
        FROM
            prayTable;
        """,
        """
        CREATE TABLE prayTable(
            table_id serial PRIMARY KEY,
            group_id VARCHAR (35),
            group_name VARCHAR (50)
        );
        """,
        """
        CREATE TABLE userTable(
            user_id serial PRIMARY KEY,
            user_name VARCHAR (25)
        );
        """,
        """
        CREATE TABLE sessionTable(
            session_id serial PRIMARY KEY,
            table_id Integer,
            user_id Integer,
            userType SMALLINT,
            addTime TIMESTAMP without time zone,
            bySomeone VARCHAR (25)
        );
        """)
    conn = None
    try:
        
        # connect to the PostgreSQL server
        #conn = psycopg2.connect(host="localhost",database="fudge", user="postgres", password="postgres")
        DATABASE_URL = os.environ['DATABASE_URL']
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        
        cur = conn.cursor()
        # create table one by one
        #for command in commands:
        #    cur.execute(command)
        
        cur.execute(commands[2])
        cur.execute(commands[3])
        cur.execute(commands[4])
        cur.execute(commands[0])
        cur.execute(commands[1])
        print("The number of parts: ", cur.rowcount)
        
        row = cur.fetchone()
        while row is not None:
            print(row)
            row = cur.fetchone()
        
        # close communication with the PostgreSQL database server
        cur.close()
        # commit the changes
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


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


	
test_tables()
print("down")




