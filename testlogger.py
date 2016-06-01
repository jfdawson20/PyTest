#!/usr/bin/python 

import os 
import sqlite3 
import time 
import datetime

class TestLogger():
    def __init__(self,db):
        self.connection = sqlite3.connect(db)
        self.dbCursor = self.connection.cursor()

    def __del__(self):
        self.connection.close()
    
    def CreateTable(self, name ,fields=[()]):
        cmd = '''CREATE TABLE '''
        cmd = cmd + name + " ("
        if(len(fields) > 0):
            for field in fields: 
                n,t = field
                cmd = cmd + " " + n + " " + t
                if field != fields[-1]:
                    cmd = cmd + ','

        cmd = cmd + ')' 
        #print cmd

        self.dbCursor.execute(cmd)
        self.connection.commit()

        return 0 

    def InsertRow(self,table,values=[]):
        cmd = '''INSERT INTO ''' + table + ''' VALUES ('''
        ops = ''''''
        for i in range(len(values)):
            cmd = cmd + '?'
            if (i != len(values)-1):
                cmd = cmd + ','

        cmd = cmd + ')'
        self.dbCursor.execute(cmd,tuple(values))
        self.connection.commit()

        return 0
    
    def CheckTableExists(self,table):
        cmd = '''SELECT name FROM sqlite_master WHERE type='table' AND name=?'''
        self.dbCursor.execute(cmd,(table,))
        ret = self.dbCursor.fetchone()

        if(ret == None):
            return -1
        else:
            return 0

    def CheckTestTypeExists(self,name):
        cmd = '''SELECT name FROM master_test_record WHERE name=?'''
        self.dbCursor.execute(cmd,(name,))
        ret = self.dbCursor.fetchone()
        
        if (ret == None):
            return -1

        else:
            return 0 


    def CheckFieldExists(self,table,field):
        cmd = '''PRAGMA table_info('''+str(table)+''')'''
        self.dbCursor.execute(cmd)
        ret = self.dbCursor.fetchall()
        
        for r in ret:
            if field in r:
                print field
                return 0
 
        return -1 

    def AddField(self,table,field=(),default='NULL'):
        cmd = '''ALTER TABLE ''' + str(table) + ''' ADD ''' + str(field[0]) + \
              ''' ''' + str(field[1]) + ''' ''' + str(default)

        self.dbCursor.execute(cmd)
        return 0 
    
    def GetField(self,table,field,keyname,key):
        cmd = '''SELECT ''' + str(field) + ''' FROM ''' + str(table) + \
              ''' WHERE ''' + str(keyname) + ''' = ?'''
       
        print cmd
        self.dbCursor.execute(cmd,(key,))
        ret = self.dbCursor.fetchone()
        print ret
        ret = str(ret[0])
        return ret

   
    def GetFields(self,table,keyname=None,key=None):
        if(keyname != None):
            cmd = '''SELECT * FROM ''' + str(table) + \
                ''' WHERE ''' + str(keyname) + ''' = ?'''

            self.dbCursor.execute(cmd,(key,))
            data = self.dbCursor.fetchall()

        else:
            cmd = '''SELECT * FROM ''' + str(table)
            self.dbCursor.execute(cmd)
            data = self.dbCursor.fetchall() 

        cmd = '''PRAGMA table_info('''+str(table)+''')'''
        self.dbCursor.execute(cmd)
        headers = self.dbCursor.fetchall()

        records = []
        i = 0
        for rows in data:
            tmp=[]
            i = 0
            for items in rows: 
                tmp.append((headers[i][1],items))
                i = i + 1
            records.append(tmp)

        return records  

if __name__ == "__main__":
    testlog = TestLogger('pytest.db')
    #fields = [('item','text'),('type','text')]
    #testlog.CreateTable('example',fields)  
    #testlog.InsertRow('example',('1','2'))
    ret = testlog.CheckFieldExists('powerapp_statistics','name')
    print ret

    ret = testlog.CheckFieldExists('master_test_record','blah')
    print ret 

    ret = testlog.GetFields('master_test_record','name','powerapp')
    for record in ret:
        print "------------ New Record ------------"
        for pair in record:
            print "Field: " + str(pair[0])
            print "Value: " + str(pair[1])
        print"\n\n"
    #testlog.AddField('testtable',('jello','text'),'NULL') 
