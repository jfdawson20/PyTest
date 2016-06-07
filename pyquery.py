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
import xlsxwriter

class PyQuery(): 
	def __init__(self,name):
                self.db = PyDB(name)
    
        #list all tests in database
        def GetTests(self,id=None,startDateTime=None,endDateTime=None,result=None): 
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
                              
            if (result != None): 
                tests = tests.filter(self.db.Test.result == result)          
                              
               
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

            ret = self.GetBatchHighlights(tests)
            print "\nTEST GROUP HIGHLIGHTS"
            print "Number of Tests:",ret[0]
            
            for results in ret[1]:
                print "Minimum Stat:",results[1],"Value",results[2],"Run:",results[0]

            for results in ret[2]:
                print "Maximum Stat:",results[1],"Value",results[2],"Run:",results[0]   
        
            for results in ret[3]:
                print "Runs With Result:",results[0],"Value",results[1]
            

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
        
        def MinStats(self,tests):
            stats = self.GetStats(tests[0].id)
            minstats = []
            for s in stats:
                x = (tests[0].id,s.name,s.val)
                minstats.append(x)

            for t in tests:
                stats = self.GetStats(t.id)
                i = 0
                for s in stats:
                    x = (t.id,s.name,s.val)
                    if (x[2] < minstats[i][2]):
                        minstats[i] = x

                    i+=1

            return minstats
            
        def MaxStats(self,tests):
            stats = self.GetStats(tests[0].id)
            maxstats = []
            for s in stats:
                x = (tests[0].id,s.name,s.val)
                maxstats.append(x)

            for t in tests:
                stats = self.GetStats(t.id)
                i = 0
                for s in stats:
                    x = (t.id,s.name,s.val)
                    if (x[2] > maxstats[i][2]):
                        maxstats[i] = x

                    i+=1

            return maxstats
            
        def ResultStats(self,tests):

            testInfo = self.GetTestInfo(tests[0].id)
            ret = []
            ret.append([testInfo[0].result,1])
            for t in tests:
                hit = 0
                testInfo = self.GetTestInfo(t.id)
                for r in ret:
                    if testInfo[0].result == r[0]:
                        r[1] += 1
                        hit = 1
                
                if hit == 0:
                    ret.append([testInfo[0].result,1])

            return ret


        def GetBatchHighlights(self,tests):
            minstats = self.MinStats(tests)
            maxstats = self.MaxStats(tests)
            resStats = self.ResultStats(tests)

            numRuns = 0
            for x in resStats:
                numRuns += x[1]
            
            ret = [numRuns,minstats,maxstats,resStats]
            return ret
        
        def ExportCombinedExcel(self,tests,base='./data'):
            #make local csv directory if it doesnt exist 
            if not os.path.exists(base): 
                os.makedirs(base)

            testBase = base+'/'+datetime.datetime.now().strftime("%m:%d:%y-%H:%M:%S")+'_combined'
            if not os.path.exists(testBase): 
                os.makedirs(testBase)

            filename = testBase + '/combined_results.xlsx'

            #create excel workbook
            workbook        = xlsxwriter.Workbook(filename,{'strings_to_numbers': True})
            highlightSheet  = workbook.add_worksheet('highlights')
            summarySheet    = workbook.add_worksheet('summary')
            
            #grab first test info to setup max columns and stuff
            testFields = tests[0].TableHeader()
            testInfo   = tests[0].TableLine()
            params     = self.GetParamsTable(tests[0].id)
            stats      = self.GetStatsTable(tests[0].id)
           
            smaxcols = len(testInfo)-1+len(params)-1+len(stats)-1
            summarySheet.set_column(0,smaxcols,15)

            #create a data worksheet per test
            #each sheet tagged with run id number
            dataSheet=[]
            i = 0
            for t in tests:
                dataSheet.append(workbook.add_worksheet('data_'+str(t.id)))
                dataSheet[i].set_column(0,100,15)
                i+=1 

            srow = 0     
            scol = 0
            
            drow = 0
            dcol = 0

            merge_format = workbook.add_format({'align': 'center'})
            summarySheet.merge_range(srow,scol,srow,scol+smaxcols,'TEST SUMMARY',merge_format)
            srow+=1
            
            #write summary sheete
            for t in tests:
                scol = 0
                testFields = t.TableHeader()
                testInfo   = t.TableLine()
                params     = self.GetParams(t.id)
                stats      = self.GetStats(t.id)
        
                line =[]
                if(srow == 1):
                    for field in testFields:
                        line.append(field)

                    for field in params:
                        line.append(field.name)

                    for field in stats:
                        line.append(field.name)
                
                    for item in line:
                        summarySheet.write(srow,scol,item)
                        scol+=1
                    
                    scol = 0
                    srow+=1
                    line = []
 
                for field in testInfo:
                    line.append(field)

                for field in params:
                    line.append(field.val)

                for field in stats:
                    line.append(field.val)                   

                for item in line:
                    summarySheet.write(srow,scol,item)
                    scol+=1

                srow+=1
                    
            #write data sheets
            i = 0
            for t in tests:
                data = self.GetDataTable(t.id)
                for d in data:
                    dcol = 0
                    for field in d:
                        dataSheet[i].write(drow,dcol,field) 
                        dcol +=1
                
                    drow+=1
                
        
                drow = 0
                dcol = 0
                i+=1 

            workbook.close()



        def ExportExcel(self,test,base='./data'):
            #make local csv directory if it doesnt exist 
            if not os.path.exists(base): 
                os.makedirs(base)

            testBase = base+'/'+test.start_datetime.strftime("%m:%d:%y-%H:%M:%S")+'_'+test.name
            if not os.path.exists(testBase): 
                os.makedirs(testBase)

            filename = testBase + '/results.xlsx'

            workbook     = xlsxwriter.Workbook(filename,{'strings_to_numbers': True})
            summarySheet = workbook.add_worksheet('summary')
            dataSheet    = workbook.add_worksheet('data')

            srow = 0     
            scol = 0
            
            drow = 0
            dcol = 0

            testinfo = self.GetTestTable(test.id)
            params   = self.GetParamsTable(test.id)
            stats    = self.GetStatsTable(test.id)
            data     = self.GetDataTable(test.id)
            
            smaxcols = len(testinfo)+len(params)+len(stats)+6
            smaxrows = max(len(testinfo[0]),len(params[0]),len(stats[0]))

            summarySheet.set_column(0,max(len(testinfo[0]),len(params[0]),len(stats[0])),20)
            dataSheet.set_column(0,len(data[0]),20)

            merge_format = workbook.add_format({'align': 'center'})
            summarySheet.merge_range(srow,scol,srow,scol+smaxrows,'TEST INFORMATION',merge_format)
            srow+=1
            
            for t in testinfo:
                scol = 0
                for field in t:
                    summarySheet.write(srow,scol,field) 
                    scol +=1
                
                srow+=1
        
            srow+=1 
            scol=0

            merge_format = workbook.add_format({'align': 'center'})
            summarySheet.merge_range(srow,scol,srow,scol+smaxrows,'TEST PARAMETERS',merge_format)
            srow+=1
  
            for t in params:
                scol = 0
                for field in t:
                    summarySheet.write(srow,scol,field) 
                    scol +=1
                
                srow+=1
        
            srow+=1
            scol=0

            merge_format = workbook.add_format({'align': 'center'})
            summarySheet.merge_range(srow,scol,srow,scol+smaxrows,'TEST STATISTICS',merge_format)
            srow+=1 
            for t in stats:
                scol = 0
                for field in t:
                    summarySheet.write(srow,scol,field) 
                    scol +=1
                
                srow+=1
        
            srow+=1 
            
            for t in data:
                dcol = 0
                for field in t:
                    dataSheet.write(drow,dcol,field) 
                    dcol +=1
                
                drow+=1
        
            drow+=1 

            workbook.close()

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
    parser.add_argument('-r', '--result', dest='resultType', help='Result Type to Filter By', default=None)
    parser.add_argument('-f', '--file', dest='folder', help='CSV Folder Output', default=None)
    parser.add_argument('-v', '--verbose', action='store_true',help='print all the things')
    
    args = parser.parse_args()

    if (args.test == None):
        print "No Test Name Provided, Exiting"
        sys.exit()

    myQuery = PyQuery(args.test)
    tests = myQuery.GetTests(id=args.id,startDateTime=args.startDateTime,endDateTime=args.endDateTime,result=args.resultType)

    if (args.op == 'list'):   
        myQuery.DisplayTests(tests)

    elif(args.op == 'display'):
        for t in tests: 
            myQuery.DisplayTestResults(t)

    elif(args.op == 'csv'):
        for t in tests: 
            myQuery.ExportCSV(t,args.folder)

    elif(args.op == 'excel'):
        for t in tests:
            myQuery.ExportExcel(t,args.folder)
    
    elif(args.op == 'excelmerge'):
        myQuery.ExportCombinedExcel(tests,args.folder)

    elif(args.op == 'minstats'):
        ret =  myQuery.GetBatchHighlights(tests)
        print ret

