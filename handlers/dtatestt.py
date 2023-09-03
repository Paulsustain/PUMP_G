import datetime
import os
#import pyodbc
# Make it work for Python 2+3 and with Unicode
import io
import sqlite3
import sys
sys.path.append('/home/pi/smartpump/helpers')
sys.path.append('/home/pi/smartpump/handlers/fcc')
sys.path.append('/home/pi/smartpump/data/fcc')
import price_change_handler
import helper
import gvr_frontier
import main_logger
import json
from datetime import datetime, time
my_logger=main_logger.get_logger(__name__)

db_path = '/home/pi/smartpump/db/fcc/store.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

#co = pyodbc.connect('Driver={SQL Server};''Server=;''Database=store;''Trusted_Connection=yes')
'''def connect_db():
    con=None
    cur=None
    try: 
        con = sqlite3.connect(db_path)
        if con:
            #print(con,'database connection successful')
            #my_logger.debug(con)
            #my_logger.debug('database connection successful')
            cur=con.cursor()
    except Exception as e:
        print(e)    
    return (con,cur)'''
def purge():
    #global a
    my_result=[]
    y = c.execute(''' SELECT id FROM transaction_details''')
    
    for row in y:
        my_result.append(row)
            
        
        lenght=len(my_result)
    a=(list(my_result[lenght-1]))
    #t=(list(my_result[0]))
    #for s in t:
    #    f=t
    #print(f)
   
    for r in a:
        d=r
        
    #print(d)
    
    #print(type(a))
    return (d,lenght) 
    
def delete():
    d,lenght=purge()
    print(d)
    print(lenght)
     
    if(lenght>= 1000):
        #d=c.execute('''SELECT  id FROM transaction_details WHERE id BETWEEN 1 AND 1002''')
        #print('much data')
        c.execute('''DELETE  FROM transaction_details WHERE id =14076''')
        #print(len(my_result))
        #print(y)
        
       
            
        #c.execute(querym)
        conn.commit()
        conn.close()
        #print(len(my_result))
    
    else:
        print('low data')
        
        
        #return my_result
        
        #return (len(c.fetchall()))
    '''from datetime import datetime
    for number in range(1,17):'''
    
    
if __name__=="__main__":
    purge()
    delete()


