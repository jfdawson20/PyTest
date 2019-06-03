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

class PyTest(): 
        '''
        Init Function: Create conenction to PyDB Database, Create a new test entry, Capture start dateTime,
        record test id for future use. 
        Arguments: 
            name     - String: test/database name 
            desc     - String: description of test
            res      - String: Test Result - Defaults to 'not_available'
            batch    - Integer: Batch ID of test - Defaults to -1 
            dbtype   - String: Database Type (sqlite or mysql) - Defaults to local sqlite database
            user     - String: Database Username if Required - Defaults to None
            password - String: Database Password if Requried - Defaults to None
            host     - String: Database Host Name if Required - Defaults to None
        '''
	def __init__(self,tname,dname,desc,res='not_available',batch=-1,dbtype='sqlite',user=None,password=None,host=None):

                #Create connection to database
                self.db = PyDB(name=dname,dbtype=dbtype,user=user,password=password,host=host)

                #create test entry 
                self.startDateTime = datetime.datetime.now()
                self.testEntry = self.db.Test(name=tname,batch_id=batch,desc=desc,result=res,start_datetime=self.startDateTime,data_count=0)

                #add new entry to current session (but dont commit!)
                self.db.session.add(self.testEntry)
                self.db.session.flush()
                        
                #set primary key of testEntry for later use
                self.testEntryId = self.testEntry.id
                self.batchId     = batch
                self.name        = name 

                #setup holders for parameter and stats
                self.dataHeader = []
                self.dataSequence = 0
        
        '''
        CloseTest Function: Capture stop time for test entry and record user provided result 
        Arguments:
            result  : String: User Defined Result 
        '''
        def CloseTest(self,result):
            self.endDateTime = datetime.datetime.now()#.strftime("%H:%M:%S")
            self.testEntry.end_datetime = self.endDateTime
            self.testEntry.result = result
            return 0            
 
        '''
        Commit Function: Pushes current test entry session into the database
        '''
        def Commit(self):
            self.db.session.commit()
            return 0


        ### Create Data Object Functions ###
        '''
        CreateParameter Function: Create a new parameter object and add it to current test
        Arguments:
            name    - String: Name of New Parameter
            val     - String: Value of new Parameter
            desc    - String: Description of New Parameter - Defaults to ''
        '''
        def CreateParameter(self,name,val,desc=''):
            tmp = self.db.Parameter(test_type=self.name,test_id=self.testEntryId, batch_id = self.batchId, 
                                 name=name,val=val,desc=desc)

            self.db.session.add(tmp)
            self.db.session.flush()
            #self.session.commit()
            return 0
        
        '''
        CreateStatistic Function: Create a new statistics object and add it to current test
        Arguments:
            name    - String: Name of New Parameter
            val     - String: Value of new Parameter
            desc    - String: Description of New Parameter - Defaults to ''
        '''       
        def CreateStatistic(self,name,val,desc=''):
            tmp = self.db.Statistic(test_type=self.name,test_id=self.testEntryId, batch_id = self.batchId, 
                                 name=name,val=val,desc=desc)

            self.db.session.add(tmp)
            self.db.session.flush()
            return 0
        
        '''
        CreateDataField Function: Create a new data object and add it to current test
        Arguments:
            name    - String: Name of New Parameter
            seq     - Integer: Sequence number, used to organize datasets sequentally - Defaults to 0
            val     - String: Value of new Parameter - Defaults to ''
            desc    - String: Description of New Parameter - Defaults to ''
        '''       
        def CreateDataField(self,name,seq=0,val='',desc=''):
            tmp = self.db.Data(test_type=self.name, seq_num=seq, test_id=self.testEntryId, batch_id = self.batchId, 
                                 name=name,val=val,desc=desc)
            
            #print name
            self.db.session.add(tmp)
            self.db.session.flush()
            return 0

        '''
        WriteDataLine Function: Create a set of Data objects with the same sequence ID 
        Creates len(data) number of data objects with the same seq number. seq number automatically incremented 
        Arguments:
            data    - List: List of data values. each index in the list must match the dataheader set previously to calling this function. 
        '''       
        def WriteDataLine(self,data=[]):
            if (len(data) != len(self.dataHeader)):
                return -1
            
            i = 0 
            for val in data:
                self.CreateDataField(name=self.dataHeader[i],seq=self.dataSequence,val=val)
                i = i + 1 
            self.dataSequence = self.dataSequence + 1
            self.testEntry.data_count = self.dataSequence 


        ### Delete Data Object Functions ###
        '''
        DeleteParameter Function: Delete parameter 'name' from current session 
        Arguments:
            name    - String: Name of Parameter to Delete
        '''
        def DeleteParameter(self,name):
            self.db.session.query(self.db.Parameter).filter_by(name=name).delete()
            self.db.session.flush()
            return 0
        
        '''
        DeleteStatistic Function: Delete statistic 'name' from current session 
        Arguments:
            name    - String: Name of Parameter to Delete
        '''       
        def DeleteStatistic(self,name):
            self.db.session.query(self.db.Statistic).filter_by(name=name).delete()
            self.db.session.flush()
            return 0

        '''
        DeleteDataField Function: Delete data 'name' from current session 
        Arguments:
            name    - String: Name of Parameter to Delete
        '''
        def DeleteDataField(self,name,seq):
            self.db.session.query(self.db.Data).filter_by(name=name).filter_by(seq_num=seq).delete()
            self.db.session.flush()
            return 0
        

        ### Update Data Object Functions ###
        '''
        UpdateParameter Function: update already defined parameter 'name' from current session 
        Arguments:
            name    - String: Name of Parameter to Delete
        '''
        def UpdateStatistic(self,name,val):
            #tmp = self.db.session.query(self.db.Statistic).filter_by(test_id=self.testEntryId).filter_by(name=name).update({"val":val})
            for stats in self.testEntry.statistics:
                if stats.name == name: 
                    stats.val = val
                    return 0
            
            self.CreateStatistic(name,val,'')

            return 0
        
        '''
        SetDataHeader Function: sets data header used when creating data lines 
        Arguments:
            header  : list: List of strings, each entry is a seperate data field
        '''        
        def SetDataHeader(self,header=[]):
            self.dataHeader = header
            self.testEntry.data_header = " ".join(header)
            return 0 


        ### Get Data Object Functions ###
        '''
        GetDataLine Function: Get all Data Objects from session with the same sequence number 
        Arguments:
            seq     : Integer: Sequence number to collect
        '''
        def GetDataLine(self,seq):
            values = self.db.session.query(self.db.Data).filter_by(test_id=self.testEntryId).filter_by(seq_num=seq)
            return values 

        '''
        GetParams Function: Get all Parameters in Session
        '''
        def GetParams(self):
            params = self.testEntry.parameters #self.db.session.query(self.db.Parameter).filter_by(test_id=self.testEntryId)
            return params
        
        '''
        GetStats Function: Get all Stats in Session
        '''
        def GetStats(self):
            stats = self.testEntry.statistics #self.db.session.query(self.db.Statistic).filter_by(test_id=self.testEntryId)
            return stats
        
        '''
        GetTestInfo Function: Get Test Entry for Session
        '''
        def GetTestInfo(self):
            test = [self.testEntry] #self.db.session.query(self.db.Test).filter_by(id=self.testEntryId)
            return test
        
        '''
        GetData Function: Get all Data Entries in Session
        '''
        def GetData(self):
            data = self.testEntry.data #self.db.session.query(self.Data).filter_by(test_id=self.testEntryId)
            return data
       
        '''
        GetParamsTable Function: Returns a 2D list of all parameters in test entry
        first entry is a list of paramter headers 
        '''
        def GetParamsTable(self): 
            table = []
            params = self.GetParams()
            if params == []:
                return []

            table.append(params[0].TableHeader())
            for p in params:
                table.append(p.TableLine())
 
            return table
        
        '''
        GetStatsTable Function: Returns a 2D list of all statistics in test entry
        first entry is a list of statistic headers
        '''
        def GetStatsTable(self):
            table = []
            stats = self.GetStats()
        
            if stats == []:
                return []
            table.append(stats[0].TableHeader())
            for s in stats: 
                table.append(s.TableLine())

            return table 

        '''
        GetDataTable Function: Returns a 2D list of all data entrys in test, organized by sequence number 
        first entry is a list of data headers defined by the user before calling this function ! 
        '''
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

        '''
        GetTestTable Function: Returns a 2D list of test information
        first entry is a list of test info headers 
        '''
        def GetTestTable(self):
            table = []
            stats = self.GetTestInfo()
            table.append(stats[0].TableHeader())
            for s in stats: 
                table.append(s.TableLine())

            return table 

        '''
        DisplayTestResults Function: Prints all information regarding current test 
        to the console in asciitables
        '''
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

#example case            
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
    for i in range(1000):
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
