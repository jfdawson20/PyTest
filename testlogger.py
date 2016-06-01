#!/usr/bin/python 

import os 
import sqlite3 
import time 
import datetime

class Test(): 
    def __init__(self,name):
        self.parameters     = []
        self.statistics     = []
        self.resultHeader   = []
        self.resultData     = []

        #first param is always test name
        self.parameters.append(('name',str(name)))
        
        #log initial time and date 
        self.parameters.append(('startDate',str(datetime.datetime.now()).split(" ")[0]))
        self.parameters.append(('startTime',str(datetime.datetime.now()).split(" ")[1]))
            

    def CreateParam(self,param,value):
        self.parameters.append((str(param),str(value)))
        return 0 

    def CreateStat(self,stat,value):
        self.statistics.append((str(stat),str(value)))
        return 0

    def SetResultHeader(self,header=[]):
        self.resultHeader = header
        return 0

    def AddResultData(self,data=[]):
        if (len(data) != len(self.resultHeader)):
            return -1
        else:
            for i in range(len(data)):
                data[i] = str(data[i])

            self.resultData.append(data)
            
        return 0 

    def UpdateParam(self,param,value):
        for p in self.parameters:
            if (p[0] == param):
                p[1] = value
            else:
                self.CreateParameter(param,value)
        return 0 

    def UpdateStat(self,stat,value):
        for s in self.statistics:
            if (s[0] == param):
                s[1] = value
            else:
                self.CreateStat(stat,value)
        return 0 

    def DisplayTestSummary(self): 
        print "------------------ TEST SUMMARY ------------------"
        print "Test Parameters\n"
        for p in self.parameters:
            print p[0] + ": " + p[1]

        print "\n"
        print "Test Statistics\n"
        for s in self.statistics: 
            print s[0] + ": " + s[1]

        print "\n"
        print "Test Results\n" 
        tmp = ""
        for h in self.resultHeader:
            tmp = tmp + h + "\t"
        
        tmp = tmp + "\n"
        print tmp 
        for d in self.resultData:
            tmp = ""
            for x in d:
                tmp = tmp + x + "\t"
            tmp = tmp + "\n"
            print tmp
        
        print "------------------ SUMMARY FINISHED ------------------"       

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

    def InsertRow(self,table,values=()):
        cmd = '''INSERT INTO ''' + table + ''' VALUES ('''
        ops = ''''''
        for i in range(len(values)):
            cmd = cmd + '?'
            if (i != len(values)-1):
                cmd = cmd + ','

        cmd = cmd + ')'
        self.dbCursor.execute(cmd,values)
        self.connection.commit()

        return 0

if __name__ == "__main__":
    testlog = TestLogger('test.db')
    fields = [('item','text'),('type','text')]
    testlog.CreateTable('example',fields)  
    testlog.InsertRow('example',('1','2'))

    mytest = Test('nfp_temp')
    mytest.CreateParam('serial','15234556')
    mytest.CreateParam('board','AMDA0096-0001')
    mytest.CreateParam('software','powerapp')

    mytest.CreateStat('minimum power','0')
    mytest.CreateStat('average power','0')
    mytest.CreateStat('maximum power','0')

    header = ['time','card power','nfp power', 'dac power']
    mytest.SetResultHeader(header)

    for i in range(10):
        testtime = time.time()
        card_power = i*2
        nfp_power  = i*1.1
        dac_power  = i*1.4
        data_to_log = [testtime,card_power,nfp_power,dac_power]
        mytest.AddResultData(data_to_log)

    mytest.DisplayTestSummary()
