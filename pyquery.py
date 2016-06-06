#!/usr/bin/python 

import os  
import time 
import datetime
from argparse import ArgumentParser
import sys 

from pydb import PyDB

#import to make pretty tables 
from terminaltables import AsciiTable

#csv import
import csv 

class PyQuery(): 
	def __init__(self,name):
                self.db = PyDB(name)
    
        #list all tests in database
        def GetTests(self,id=None,startDateTime=None,endDateTime=None,Result=None): 
            tests = self.db.session.query(self.db.Test)
            #start_datetime = datetime.datetime.now()
            if (id != None):
                tests = tests.filter(self.db.Test.id == id)

            if (startDateTime != None): 
                x = datetime.datetime.strptime(startDateTime,"%m:%d:%y-%H:%M:%S")
                tests = tests.filter(self.db.Test.start_datetime >= x)
           
            if (endDateTime != None): 
                x = datetime.datetime.strptime(endDateTime,"%m:%d:%y-%H:%M:%S")
                tests = tests.filter(self.db.Test.start_datetime <= x)          
                              
        
            return tests

        def DisplayTests(self,tests): 
            table = []
            i = 0
            for t in tests: 
                testId = t.id
                table = table + (self.GetTestTable(testId,i))
                i = i + 1

            atable = AsciiTable(table)
            print atable.table
    
        def GetDataLine(self,testId,seq):
            values = self.db.session.query(self.db.Data).filter_by(test_id=testId).filter_by(seq_num=seq)
            return values 

        def GetParams(self,testId):
            params = self.db.session.query(self.db.Parameter).filter_by(test_id=testId)
            return params

        def GetStats(self,testId):
            stats = self.db.session.query(self.db.Statistic).filter_by(test_id=testId)
            return stats

        def GetTestInfo(self,testId):
            test = self.db.session.query(self.db.Test).filter_by(id=testId)
            return test

        def GetData(self,testId):
            data = self.db.session.query(self.Data).filter_by(testId)
            return data
        
        def GetParamsTable(self,testId): 
            table = []
            params = self.GetParams(testId)
            table.append(params[0].TableHeader())
            for p in params:
                table.append(p.TableLine())
 
            return table

        def GetStatsTable(self,testId):
            table = []
            stats = self.GetStats(testId)
            table.append(stats[0].TableHeader())

            for s in stats: 
                table.append(s.TableLine())

            return table 

        def GetDataTable(self,testId):
            test = self.GetTestInfo(testId) 
            dc = test[0].data_count 
            table = []
            header = (test[0].data_header.split(" "))
            table.append(header)
            for i in range(dc):
                v = self.GetDataLine(testId,i)
                tableRow = []
                for stuff in v: 
                    tableRow.append(stuff.val)

                table.append(tableRow)
            return table

        def GetTestTable(self,testId,header=0):
            table = []
            stats = self.GetTestInfo(testId)
            if (header == 0):
                table.append(stats[0].TableHeader())
            
            for s in stats: 
                table.append(s.TableLine())

            return table 


        def DisplayTestResults(self,test):
            print "Printing Test Results\n"
            print "-------- Test Information --------"
            table = self.GetTestTable(test.id)
            atable = AsciiTable(table)
            print atable.table 

            print "\n--------- Parameters -----------"
            table = self.GetParamsTable(test.id)
            atable = AsciiTable(table) 
            print atable.table


            print "\n-------- Statistics -----------"
            table = self.GetStatsTable(test.id)
            atable = AsciiTable(table)
            print atable.table


            print "\n ----------- Data --------------"
            table = self.GetDataTable(test.id)
            atable = AsciiTable(table)
            print atable.table
                    

            return 0

        def ExportCSV(self,test,base='./data'):
            #make local csv directory if it doesnt exist 
            if not os.path.exists(base): 
                os.makedirs(base)

            testBase = base+'/'+test.start_datetime.strftime("%m:%d:%y-%H:%M:%S")+'_'+test.name
            if not os.path.exists(testBase): 
                os.makedirs(testBase)

            #print testBase

            datafile    = testBase+'/DATA.csv'
            paramsfile  = testBase+'/PARAMS.csv'
            statsfile  = testBase+'/STATS.csv'

            with open(datafile,'w') as cfile:
                writer = csv.writer(cfile)
                rows = self.GetDataTable(test.id)
                for row in rows: 
                    writer.writerow(row)

            with open(paramsfile,'w') as cfile:
                writer = csv.writer(cfile)
                rows = self.GetParamsTable(test.id)
                for row in rows: 
                    writer.writerow(row)

            with open(statsfile,'w') as cfile:
                writer = csv.writer(cfile)
                rows = self.GetStatsTable(test.id)
                for row in rows: 
                    writer.writerow(row)
            return 0

            
	
if __name__ == "__main__":
    #setup arg parser for cmd line stuff 
    parser = ArgumentParser()
    parser.add_argument('-t', '--test', dest='test', help='Test Name', default=None)
    parser.add_argument('-op', '--operation', dest='op', help='Operation To Perform', default=None)
    parser.add_argument('-i', '--id', dest='id', help='Specific Test ID to Query', default=None)
    parser.add_argument('-s', '--startdatetime', dest='startDateTime', help='Start Date Range to Search', default=None)
    parser.add_argument('-e', '--enddatetime', dest='endDateTime', help='End Date Range to Search', default=None)
    parser.add_argument('-f', '--file', dest='folder', help='CSV Folder Output', default=None)
    parser.add_argument('-v', '--verbose', action='store_true',help='print all the things')
    
    args = parser.parse_args()

    if (args.test == None):
        print "No Test Name Provided, Exiting"
        sys.exit()

    myQuery = PyQuery(args.test)
    tests = myQuery.GetTests(id=args.id,startDateTime=args.startDateTime,endDateTime=args.endDateTime)

    if (args.op == 'list'):   
        myQuery.DisplayTests(tests)

    elif(args.op == 'display'):
        for t in tests: 
            myQuery.DisplayTestResults(t)

    elif(args.op == 'export'):
        for t in tests: 
            myQuery.ExportCSV(t,args.folder)
