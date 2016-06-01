#!/usr/bin/python 

import os 
import sqlite3 
import time 
import datetime
from testlogger import TestLogger

class PyTest(): 
    def __init__(self,name,db='pytest.db'):
		#initialize test variables 
        self.parameters     = []
        self.statistics     = []
        self.resultHeader   = []
        self.resultData     = []

	#Initialize database connection
        self.logger = TestLogger(db)

        #first param is always test name
        self.parameters.append(('name',str(name)))
        
        #log initial time and date 
        self.parameters.append(('startDate',str(datetime.datetime.now()).split(" ")[0]))
        self.parameters.append(('startTime',str(datetime.datetime.now()).split(" ")[1]))
            
	#test result parameter
        self.parameters.append(('result','incomplete'))
	
        #check if mtr exists in database, create it if its not found 
        if (self.logger.CheckTableExists('master_test_record') == -1):
            fields = [('mkey','text'),('testcount','text')]
            for p in self.parameters:
                name,val = p 
                fields.append((name,'text'))
            
            #create master test record table
            self.logger.CreateTable('master_test_record',fields)
    
                
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
                return -1
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

    def PushTestResults(self):
        fields = []
        vals   = []
        
        #make sure all parameters exist in mtr
        for params in self.parameters:
            fields.append(params[0])    
            vals.append(params[1])
            if (self.logger.CheckFieldExists('master_test_record',params[0]) == -1):
                self.logger.AddField('master_test_record',(params[0],'text'))

        self.logger.InsertRow('master_test_record',vals)
    
        
if __name__ == "__main__":

    mytest = PyTest('powerapp')
    mytest.CreateParam('nfp_serial','15234556')
    mytest.CreateParam('board_type','lithium')
    mytest.CreateParam('board_serial','AMDA0096-0001-150604223')
    mytest.CreateParam('bsp_version','2015.11')

    mytest.CreateStat('minimum power','0')
    mytest.CreateStat('average power','0')
    mytest.CreateStat('maximum power','0')

    header = ['time','card power','nfp power', 'dac power']
    mytest.SetResultHeader(header)

    for i in range(10):
        testtime = time.time()
        card_power = i*2
        dac_power  = i*1.4
        nfp_power  = i*1.2
       	data_to_log = [testtime,card_power,nfp_power,dac_power]
       	mytest.AddResultData(data_to_log)

    mytest.DisplayTestSummary()
