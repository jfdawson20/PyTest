# PyTest
# Summary
pytest is a set of python test logging and querying tools based on a SQL backend. 

Modules: 
pydb.py
pytest.py
pyquery.py 


pydb.py - PyDB Class: 
    Interface/Wrapper around SQL Test Database 
    -Creates and returns database connection 
    -Defines table types used
    -Creates tables if required 

pytest.py - PyTest Class: 
    Main module for creating python tests
    -Creation of test object
    -Creation of test parameters, statistics, and data 
    -Commiting test data to database 

pyquery.py - PyQuery Class:
    Main module/application for querying and displaying test data 
    -Connecting to a database
    -Filtering tests 
    -Viewing test entries 
    -Displaying test logs 
    -Exporting test records in a variety of formats 
    -Pushing local test data to remote databases 


# Getting Started 
# Install
1) Pull copy of git repo:
    'git clone https://github.com/jfdawson20/PyTest'

2) Install modules 
    'python setup.py install' 

# Create Test 

1) In your python based test import pytest 
    from pytest import PyTest 


2) Create an instance of PyTest
    MyTest = PyTest(name='test_name',desc='test description string')

# Add Test Parameters
    MyTest.CreateParameter(name='parameter1',val=val, desc='descripton of parameter')
    MyTest.CreateParameter...
    ...

# Add Test Statistics 
    MyTest.CreateStatistic(name='stat1',val=val, desc='descripton of statistic')
    MyTest.CreateStatistic...
    ...

# Create Data header
    header = ['header 1', 'header 2', 'header 3', header 4']
    MyTest.SetDataHeader(header)

# Run test
## While running test log data, update stats, etc 
    
    while(TestIsRunning)
        data1 = getData1()
        data2 = getData2()
        data3 = getData3()
        data4 = getData4()

        dataline = [data1,data2,data3,data4]
        MyTest.WriteDataLine(dataline)

        MyTest.UpdateStatistic('stat1',newval)
        ...
        ...

# Stop Test, log result 
    MyTest.CloseTest('user_defined_result_string')    

        
# Commit test log to database 
    MyTest.Commit()
    
 
