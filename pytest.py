#!/usr/bin/python 

import os  
import time 
import datetime

# sqlachemy imports for database interface
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String

#import to make pretty tables 
from terminaltables import AsciiTable

#csv import
import csv 

class PyTest(): 
	Base   = declarative_base() 
	def __init__(self,name,desc,res='not_available',batch=-1):
                #setup database connection and session 
		self.engine  = create_engine('sqlite:///' + name + '.db', echo=False)
		self.Session = sessionmaker()
		self.Session.configure(bind=self.engine)
		self.session = self.Session()
                self.Base.metadata.bind = self.engine
                self.Base.metadata.create_all()

                #create test entry 
                self.startTime = datetime.datetime.today().strftime("%H:%M:%S")
                self.startDate = datetime.datetime.today().strftime("%m_%d_%y")
                
                self.testEntry = self.Test(name=name,batch_id=batch,desc=desc,result=res,start_time=self.startTime,start_date=self.startDate)

                self.session.add(self.testEntry)
                self.session.flush()
                #self.session.commit()
                        
                #set primary key of testEntry for later use
                self.testEntryId = self.testEntry.id
                self.batchId     = batch
                self.name        = name 

                #setup holders for parameter and stats
                self.dataHeader = []
                self.dataSequence = 0

        def CreateParameter(self,name,val,desc=''):
            tmp = self.Parameter(test_type=self.name,test_id=self.testEntryId, batch_id = self.batchId, 
                                 name=name,val=val,desc=desc)

            self.session.add(tmp)
            self.session.flush()
            #self.session.commit()
            return 0

        def DeleteParameter(self,name):
            self.session.query(self.Parameter).filter_by(name=name).delete()
            self.session.flush()
            return 0
        
        def DeleteStatistic(self,name):
            self.session.query(self.Statistic).filter_by(name=name).delete()
            self.session.flush()
            return 0

        def DeleteDataField(self,name,seq):
            self.session.query(self.Data).filter_by(name=name).filter_by(seq_num=seq).delete()
            self.session.flush()
            return 0
        
        def CreateStatistic(self,name,val,desc=''):
            tmp = self.Statistic(test_type=self.name,test_id=self.testEntryId, batch_id = self.batchId, 
                                 name=name,val=val,desc=desc)

            self.session.add(tmp)
            self.session.flush()
            return 0
         
        def CreateDataField(self,name,seq=0,val='',desc=''):
            tmp = self.Data(test_type=self.name, seq_num=seq, test_id=self.testEntryId, batch_id = self.batchId, 
                                 name=name,val=val,desc=desc)
            
            #print name
            self.session.add(tmp)
            self.session.flush()
            return 0

        def SetDataHeader(self,header=[]):
            self.dataHeader = header
            return 0 

        def WriteDataLine(self,data=[]):
            if (len(data) != len(self.dataHeader)):
                return -1
            
            i = 0 
            for val in data:
                self.CreateDataField(name=self.dataHeader[i],seq=self.dataSequence,val=val)
                i = i + 1 
            self.dataSequence = self.dataSequence + 1

        def GetDataLine(self,seq):
            values = self.session.query(self.Data).filter_by(test_id=self.testEntryId).filter_by(seq_num=seq)
            return values 

        def GetParams(self):
            params = self.session.query(self.Parameter).filter_by(test_id=self.testEntryId)
            return params

        def GetStats(self):
            stats = self.session.query(self.Statistic).filter_by(test_id=self.testEntryId)
            return stats

        def GetTestInfo(self):
            test = self.session.query(self.Test).filter_by(id=self.testEntryId)
            return test

        def GetData(self):
            data = self.session.query(self.Data).filter_by(test_id=self.testEntryId)
            return data
        
        def Commit(self):
            self.session.commit()
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

            testBase = base+'/'+self.startDate+'_'+self.startTime+'_'+self.name
            if not os.path.exists(testBase): 
                os.makedirs(testBase)

            print testBase

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

            
#----------- Private Classes for Database Storage -------------#      
        class Parameter(Base):
		__tablename__ = 'parameter'

		#define table properties 
		id 	  = Column(Integer, primary_key=True)
                test_type = Column(String(250))
                test_id   = Column(Integer)
                batch_id  = Column(Integer)
		name	  = Column(String(250)) 		
		val	  = Column(String(250)) 		
		desc	  = Column(String(250)) 		
                
                def __repr__(self):
                    s =  "<Parameter(id='%d', test_type='%s', test_id='%d', batch_id='%d', name='%s', val='%s', description='%s')>" % (
                         self.id, self.test_type,self.test_id, self.batch_id, self.name, self.val, self.desc)
            
                    return s

                def TableLine(self):
                    line = [self.id,self.test_type,self.test_id,self.batch_id,self.name,self.val,self.desc]
                    return line

                def TableHeader(self):
                    header = ['id','test_type','test_id','batch_id','parameter name','value','description']
                    return header

	class Statistic(Base):
		__tablename__ = 'statistic'

		#define table properties 
		id 	  = Column(Integer, primary_key=True)
                test_type = Column(String(250))
                test_id   = Column(Integer)
                batch_id  = Column(Integer)
		name	  = Column(String(250)) 		
		val	  = Column(String(250)) 		
		desc	  = Column(String(250)) 		
                
                def __repr__(self):
                    s =  "<Statistic(id='%d', test_type='%s', test_id='%d', batch_id='%d', name='%s', val='%s', description='%s')>" % (
                         self.id, self.test_type, self.test_id, self.batch_id, self.name, self.val, self.desc)

                    return s

                def TableLine(self):
                    line = [self.id,self.test_type,self.test_id,self.batch_id,self.name,self.val,self.desc]
                    return line

                def TableHeader(self):
                    header = ['id','test_type','test_id','batch_id','parameter name','value','description']
                    return header


	class Data(Base):
		__tablename__ = 'data'

		#define table properties 
		id 	  = Column(Integer, primary_key=True)
                test_type = Column(String(250))
                seq_num   = Column(Integer)
                test_id   = Column(Integer)
                batch_id  = Column(Integer)
		name	  = Column(String(250)) 		
		val	  = Column(String(250)) 		
		desc	  = Column(String(250)) 		
                
                def __repr__(self):
                    s =  "<Data(id='%d', test_type='%s', seq_num='%d', test_id='%d', batch_id='%d', name='%s', val='%s', description='%s')>" % (
                         self.id, self.test_type, self.seq_num, self.test_id, self.batch_id, self.name, self.val, self.desc)

                    return s

                def TableLine(self):
                    line = [self.id,self.test_type,self.test_id,self.batch_id,self.name,self.val,self.desc]
                    return line

                def TableHeader(self):
                    header = ['id','test_type','test_id','batch_id','parameter name','value','description']
                    return header


	class Test(Base): 
		__tablename__ = 'test'

		#define table properties 
		id 	   = Column(Integer, primary_key=True)
                start_time = Column(String(250))
                end_time   = Column(String(250))
                start_date = Column(String(250))
                end_date   = Column(String(250))
                batch_id   = Column(Integer) 
		name	   = Column(String(250)) 	    
		desc	   = Column(String(250)) 
		result     = Column(String(250))
		
                def __repr__(self):
                    s =  "<Test(id='%d', batch_id='%d', name='%s', result='%s', description='%s')>" % (
                         self.id, self.batch_id, self.name, self.result, self.desc)

                    return s

                def TableLine(self):
                    line = [self.id,self.start_time,self.end_time,self.start_date,self.end_date,self.batch_id,self.name,self.desc,self.result]
                    return line

                def TableHeader(self):
                    header = ['id','start_time','end_time','start_date','end_date','batch_id','Test Name','Test Description','Test Result']
                    return header


	
if __name__ == "__main__":
    mytest = PyTest('powerapp','nfp6000 Power Test')
    mytest.CreateParameter('nfp_serial','11234444444','nfp6000 serial number')
    mytest.CreateParameter('board_serial','AMDA0099-0001-15234423','Board Serial')
    mytest.CreateParameter('nfp_bsp','nfp-bsp-release-2015.11','bsp version')

    mytest.CreateStatistic('min_power',0,'Minimum power consumption during run')
    mytest.CreateStatistic('max_power',0,'Maximum power consumption during run')
    mytest.CreateStatistic('average_power',0,'Average power consumption during run')

    dataHeader = ["timestamp","nfp_temp","nfp_power","card_power","system_power","hello","11111111","22222222","333333333"]
    mytest.SetDataHeader(dataHeader)

    for i in range(10):
        timestamp = i
        nfp_temp  = i*2
        nfp_power = i*1.1
        card_power = i*1.4
        system_power = i*3.3
        hello  = 'hi'
        a1 = 'a1'
        a2 = 'a2'
        a3 = 'a3'

        data = [timestamp,nfp_temp,nfp_power,card_power,system_power,hello,a1,a2,a3]
        mytest.WriteDataLine(data)

    mytest.DisplayTestResults()
    mytest.ExportCSV()
