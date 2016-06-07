#!/usr/bin/python 

import os  
import time 
import datetime
import random 

from pydb import PyDB

#import to make pretty tables 
from terminaltables import AsciiTable

#csv import
import csv 
import xlsxwriter

class PyTest(): 
	def __init__(self,name,desc,res='not_available',batch=-1):

                self.db = PyDB(name)
                #create test entry 
                self.startDateTime = datetime.datetime.now()#.strftime("%H:%M:%S")
                
                
                self.testEntry = self.db.Test(name=name,batch_id=batch,desc=desc,result=res,start_datetime=self.startDateTime,data_count=0)

                self.db.session.add(self.testEntry)
                self.db.session.flush()
                        
                #set primary key of testEntry for later use
                self.testEntryId = self.testEntry.id
                self.batchId     = batch
                self.name        = name 

                #setup holders for parameter and stats
                self.dataHeader = []
                self.dataSequence = 0

        def CreateParameter(self,name,val,desc=''):
            tmp = self.db.Parameter(test_type=self.name,test_id=self.testEntryId, batch_id = self.batchId, 
                                 name=name,val=val,desc=desc)

            self.db.session.add(tmp)
            self.db.session.flush()
            #self.session.commit()
            return 0

        def DeleteParameter(self,name):
            self.db.session.query(self.db.Parameter).filter_by(name=name).delete()
            self.db.session.flush()
            return 0
        
        def DeleteStatistic(self,name):
            self.db.session.query(self.db.Statistic).filter_by(name=name).delete()
            self.db.session.flush()
            return 0

        def DeleteDataField(self,name,seq):
            self.db.session.query(self.db.Data).filter_by(name=name).filter_by(seq_num=seq).delete()
            self.db.session.flush()
            return 0
        
        def CreateStatistic(self,name,val,desc=''):
            tmp = self.db.Statistic(test_type=self.name,test_id=self.testEntryId, batch_id = self.batchId, 
                                 name=name,val=val,desc=desc)

            self.db.session.add(tmp)
            self.db.session.flush()
            return 0

        def UpdateStatistic(self,name,val):
            tmp = self.db.session.query(self.db.Statistic).filter_by(test_id=self.testEntryId).filter_by(name=name).update({"val":val})
            return 0
         
        def CreateDataField(self,name,seq=0,val='',desc=''):
            tmp = self.db.Data(test_type=self.name, seq_num=seq, test_id=self.testEntryId, batch_id = self.batchId, 
                                 name=name,val=val,desc=desc)
            
            #print name
            self.db.session.add(tmp)
            self.db.session.flush()
            return 0

        def SetDataHeader(self,header=[]):
            self.dataHeader = header
            self.testEntry.data_header = " ".join(header)
            return 0 

        def WriteDataLine(self,data=[]):
            if (len(data) != len(self.dataHeader)):
                return -1
            
            i = 0 
            for val in data:
                self.CreateDataField(name=self.dataHeader[i],seq=self.dataSequence,val=val)
                i = i + 1 
            self.dataSequence = self.dataSequence + 1
            self.testEntry.data_count = self.dataSequence 

        def GetDataLine(self,seq):
            values = self.db.session.query(self.db.Data).filter_by(test_id=self.testEntryId).filter_by(seq_num=seq)
            return values 

        def GetParams(self):
            params = self.db.session.query(self.db.Parameter).filter_by(test_id=self.testEntryId)
            return params

        def GetStats(self):
            stats = self.db.session.query(self.db.Statistic).filter_by(test_id=self.testEntryId)
            return stats

        def GetTestInfo(self):
            test = self.db.session.query(self.db.Test).filter_by(id=self.testEntryId)
            return test

        def GetData(self):
            data = self.db.session.query(self.Data).filter_by(test_id=self.testEntryId)
            return data
       
        def CloseTest(self,result):
            self.endDateTime = datetime.datetime.now()#.strftime("%H:%M:%S")
            self.testEntry.end_datetime = self.endDateTime
            self.testEntry.result = result
            return 0            
 
        def Commit(self):
            self.db.session.commit()
            return 0

        def GetParamsTable(self): 
            table = []
            params = self.GetParams()
            table.append(params[0].TableHeader())
            for p in params:
                table.append(p.TableLine())
 
            return table

        def GetStatsTable(self):
            table = []
            stats = self.GetStats()
            table.append(stats[0].TableHeader())
            for s in stats: 
                table.append(s.TableLine())

            return table 

        def GetDataTable(self):
            table = []
            table.append(self.dataHeader)
            for i in range(self.dataSequence):
                v = self.GetDataLine(i)
                tableRow = []
                for stuff in v: 
                    tableRow.append(stuff.val)

                table.append(tableRow)
            return table

        def GetTestTable(self):
            table = []
            stats = self.GetTestInfo()
            table.append(stats[0].TableHeader())
            for s in stats: 
                table.append(s.TableLine())

            return table 


        

        def DisplayTestResults(self):
            print "Printing Test Results\n"
            print "-------- Test Information --------"
            table = self.GetTestTable()
            atable = AsciiTable(table)
            print atable.table 

            print "\n--------- Parameters -----------"
            table = self.GetParamsTable()
            atable = AsciiTable(table) 
            print atable.table


            print "\n-------- Statistics -----------"
            table = self.GetStatsTable()
            atable = AsciiTable(table)
            print atable.table


            print "\n ----------- Data --------------"
            table = self.GetDataTable()
            atable = AsciiTable(table)
            print atable.table
                    

            return 0

        def ExportCSV(self,base='./data'):
            #make local csv directory if it doesnt exist 
            if not os.path.exists(base): 
                os.makedirs(base)

            testBase = base+'/'+self.startDateTime.strftime("%m:%d:%y-%H:%M:%S")+'_'+self.name
            #print testBase
            if not os.path.exists(testBase): 
                os.makedirs(testBase)

            #print testBase

            datafile    = testBase+'/DATA.csv'
            paramsfile  = testBase+'/PARAMS.csv'
            statsfile  = testBase+'/STATS.csv'

            with open(datafile,'w') as cfile:
                writer = csv.writer(cfile)
                rows = self.GetDataTable()
                for row in rows: 
                    writer.writerow(row)

            with open(paramsfile,'w') as cfile:
                writer = csv.writer(cfile)
                rows = self.GetParamsTable()
                for row in rows: 
                    writer.writerow(row)

            with open(statsfile,'w') as cfile:
                writer = csv.writer(cfile)
                rows = self.GetStatsTable()
                for row in rows: 
                    writer.writerow(row)
            return 0

        def ExportExcel(self,base='./data'):
            #make local csv directory if it doesnt exist 
            if not os.path.exists(base): 
                os.makedirs(base)

            testBase = base+'/'+self.startDateTime.strftime("%m:%d:%y-%H:%M:%S")+'_'+self.name
            #print testBase
            if not os.path.exists(testBase): 
                os.makedirs(testBase)

            #print testBase

            excelfile    = testBase+'/DATA.csv'

            test = self.GetTestTable()
            data = self.GetDataTable()
            params = self.GetParamsTable()    
            stats = self.GetStatsTable()
                
            
            return 0

            
	
if __name__ == "__main__":
    mytest = PyTest('powerapp','nfp6000 Power Test')
    mytest.CreateParameter('nfp_serial','11234444444','nfp6000 serial number')
    mytest.CreateParameter('board_serial','AMDA0099-0001-15234423','Board Serial')
    mytest.CreateParameter('nfp_bsp','nfp-bsp-release-2015.11','bsp version')

    mytest.CreateStatistic('min_power',-1,'Minimum power consumption during run')
    mytest.CreateStatistic('max_power',-1,'Maximum power consumption during run')
    mytest.CreateStatistic('average_power',-1,'Average power consumption during run')

    dataHeader = ["timestamp","nfp_temp","nfp_power","card_power","system_power","hello","11111111","22222222","333333333"]
    mytest.SetDataHeader(dataHeader)

    r = int(random.random()*100)
    for i in range(r):
        rand = random.random()

        timestamp = rand
        nfp_temp  = rand*2
        nfp_power = rand*1.1
        card_power = rand*1.4
        system_power = rand*3.3
        hello  = 'hi'
        a1 = 'a1'
        a2 = 'a2'
        a3 = 'a3'
        
        data = [timestamp,nfp_temp,nfp_power,card_power,system_power,hello,a1,a2,a3]
        mytest.WriteDataLine(data)

        if(i == 0):
            min_power = nfp_power
            max_power = nfp_power
            average_sum = nfp_power

        else:
            if nfp_power > max_power:
                max_power = nfp_power

            if nfp_power < min_power:
                min_power = nfp_power

            average_sum += nfp_power

    mytest.UpdateStatistic('min_power',min_power)
    mytest.UpdateStatistic('max_power',max_power)
    
    average_power = (average_sum)/i
    mytest.UpdateStatistic('average_power',average_power)
             
    if (rand <= .5):
        mytest.CloseTest('Pass')

    else:
        mytest.CloseTest('fail')

    mytest.DisplayTestResults()
    #mytest.ExportCSV()
    mytest.Commit()
