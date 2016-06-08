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

'''
Class: PyDB 
PyDB provides access to a underlying database via a set of sqlalchemy api's.
'''
class PyDB(): 
	Base   = declarative_base() 
	def __init__(self,name,dbtype='sqlite',user=None,password=None,host=None):
                #setup database connection and session 
                if (dbtype ==  'sqlite'):
		    self.engine = create_engine('sqlite:///' + name + '.db', echo=False)
                elif (dbtype == 'mysql'):
                    self.engine = create_engine('mysql://'+user+':'+password+'@'+host)
                    databases = self.engine.execute("SHOW DATABASES;")
                    databases = [d[0] for d in databases]
                    
                    if (name not in databases):
                        self.engine.execute("CREATE DATABASE "+name) #create db
                    
                    self.engine.execute("USE "+name) # select new db

		self.Session = sessionmaker()
		self.Session.configure(bind=self.engine)
		self.session = self.Session()
                self.Base.metadata.bind = self.engine
                self.Base.metadata.create_all()
        
        '''
        Function to copy current database contents to a new database instance. 
        newDb is of type PyDB and must already be setup to contain the correct tables used by 
        MyDB 
        '''
        def CopyToNewDB(self,newDb):
            tables = self.Base.metadata.tables;
            for t in tables: 
                data = self.engine.execute(tables[t].select()).fetchall()
                if data: 
                    newDb.engine.execute(tables[t].insert(),data)

            return 0
#----------- Private Classes for Database Storage -------------#  

        '''
        The Parameter class provides the python object representation of the Paramter table 
        found within the sql database.
        '''
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
               
                def __len__(self):
                    return 7
                
                '''
                Python repr function, returns formatted string when str(type Test) is called
                '''
                def __repr__(self):
                    s =  "<Parameter(id='%d', test_type='%s', test_id='%d', batch_id='%d', name='%s', val='%s', description='%s')>" % (
                         self.id, self.test_type,self.test_id, self.batch_id, self.name, self.val, self.desc)
            
                    return s
                '''
                TableLine function, returns array of all relavant object parameters.
                '''
                def TableLine(self):
                    line = [self.id,self.test_type,self.test_id,self.batch_id,self.name,self.val,self.desc]
                    return line

                '''
                TableHeader function, returns array of all relavant object parameter names in string format.
                '''
                def TableHeader(self):
                    header = ['id','test_type','test_id','batch_id','parameter name','value','description']
                    return header
        '''
        The Stats class provides the python object representation of the Data table 
        found within the sql database.
        '''
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

                '''
                Python length function, allows support for len(type Statistic) operations
                '''
                def __len__(self):
                    return 7

                '''
                Python repr function, returns formatted string when str(type Test) is called
                '''
                def __repr__(self):
                    s =  "<Statistic(id='%d', test_type='%s', test_id='%d', batch_id='%d', name='%s', val='%s', description='%s')>" % (
                         self.id, self.test_type, self.test_id, self.batch_id, self.name, self.val, self.desc)

                    return s
                
                '''
                TableLine function, returns array of all relavant object parameters.
                '''
                def TableLine(self):
                    line = [self.id,self.test_type,self.test_id,self.batch_id,self.name,self.val,self.desc]
                    return line
                
                '''
                TableHeader function, returns array of all relavant object parameter names in string format.
                '''
                def TableHeader(self):
                    header = ['id','test_type','test_id','batch_id','parameter name','value','description']
                    return header

        '''
        The Data class provides the python object representation of the Data table 
        found within the sql database.
        '''
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
                
                '''
                Python length function, allows support for len(type Statistic) operations
                '''       
                def __len__(self):
                    return 8
                
                '''
                Python repr function, returns formatted string when str(type Test) is called
                '''       
                def __repr__(self):
                    s =  "<Data(id='%d', test_type='%s', seq_num='%d', test_id='%d', batch_id='%d', name='%s', val='%s', description='%s')>" % (
                         self.id, self.test_type, self.seq_num, self.test_id, self.batch_id, self.name, self.val, self.desc)

                    return s
                
                '''
                TableLine function, returns array of all relavant object parameters.
                '''
                def TableLine(self):
                    line = [self.id,self.test_type,self.test_id,self.batch_id,self.name,self.val,self.desc]
                    return line

                '''
                TableHeader function, returns array of all relavant object parameter names in string format.
                '''                              
                def TableHeader(self):
                    header = ['id','test_type','test_id','batch_id','parameter name','value','description']
                    return header

        '''
        The Test class provides the python object representation of the Test table 
        found within the sql database.
        '''
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

                '''
                Python length function, allows support for len(type Statistic) operations
                '''
                def __len__(self):
                    return 9

                '''
                Python repr function, returns formatted string when str(type Test) is called
                '''
                def __repr__(self):
                    s =  "<Test(id='%d', batch_id='%d', name='%s', result='%s', description='%s')>" % (
                         self.id, self.batch_id, self.name, self.result, self.desc)

                    return s
                
                '''
                TableLine function, returns array of all relavant object parameters.
                '''
                def TableLine(self):
                    line = [self.id,self.start_datetime.strftime("%m:%d:%y-%H:%M:%S"),self.end_datetime.strftime("%m:%d:%y-%H:%M:%S"),self.batch_id,self.name,self.desc,self.result,self.data_count]
                    return line

                '''
                TableHeader function, returns array of all relavant object parameter names in string format.
                '''
                def TableHeader(self):
                    header = ['id','start_datetime','end_datetime','batch_id','Test Name','Test Description','Test Result','Data Count']
                    return header


	

