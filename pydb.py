#!/usr/bin/python 

import os  
import time 
import datetime

# sqlachemy imports for database interface
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String, DateTime

#import to make pretty tables 
from terminaltables import AsciiTable

#csv import
import csv 

class PyDB(): 
	Base   = declarative_base() 
	def __init__(self,name):
                #setup database connection and session 
		self.engine  = create_engine('sqlite:///' + name + '.db', echo=False)
		self.Session = sessionmaker()
		self.Session.configure(bind=self.engine)
		self.session = self.Session()
                self.Base.metadata.bind = self.engine
                self.Base.metadata.create_all()

            
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
                start_datetime = Column(DateTime)
                end_datetime   = Column(DateTime) 
                batch_id   = Column(Integer) 
		name	   = Column(String(250)) 	    
		desc	   = Column(String(250)) 
		result     = Column(String(250))
                data_count = Column(Integer)
                data_header = Column(String(1024))

                def __repr__(self):
                    s =  "<Test(id='%d', batch_id='%d', name='%s', result='%s', description='%s')>" % (
                         self.id, self.batch_id, self.name, self.result, self.desc)

                    return s

                def TableLine(self):
                    line = [self.id,self.start_datetime,self.end_datetime,self.batch_id,self.name,self.desc,self.result,self.data_count]
                    return line

                def TableHeader(self):
                    header = ['id','start_datetime','end_datetime','batch_id','Test Name','Test Description','Test Result','Data Count']
                    return header


	
if __name__ == "__main__":
    print "hello"