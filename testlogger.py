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
        for field in fields: 
            n,t = field
            cmd = cmd + " " + n + " " + t
            if field != fields[-1]:
                cmd = cmd + ','

        cmd = cmd + ')' 
        print cmd

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
        cmd = '''SELECT name FROM ''' + table + '''  WHERE name=?'''
        self.dbCursor.execute(cmd,(field,))
        ret = self.dbCursor.fetchone()
        
        if (ret == None):
            return -1

        else:
            return 0 

    def AddField(self,table,field=(),default='NULL'):
        cmd = '''ALTER TABLE ''' + str(table) + ''' ADD ''' + str(field[0]) + \
              ''' ''' + str(field[1]) + ''' ''' + str(default)

        self.dbCursor.execute(cmd)
        return 0 
        

if __name__ == "__main__":
    testlog = TestLogger('pytest.db')
    #fields = [('item','text'),('type','text')]
    #testlog.CreateTable('example',fields)  
    #testlog.InsertRow('example',('1','2'))
    ret = testlog.CheckFieldExists('master_test_record','name')
    print ret

    ret = testlog.CheckFieldExists('master_test_record','blah')
    print ret 

    testlog.AddField('testtable',('jello','text'),'NULL') 
