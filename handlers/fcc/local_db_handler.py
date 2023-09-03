import sys
import os
import io
import sqlite3
dir_path = os.path.dirname(os.path.realpath(__file__))
print(dir_path)
conn = sqlite3.connect(dir_path+'/store.db')
c = conn.cursor()

#MIGRATION 1    
c.execute('''CREATE TABLE IF NOT EXISTS transaction_details
             (id integer primary key AUTOINCREMENT,
             device_address VARCHAR(50) DEFAULT NULL,
             pump_id INT DEFAULT NULL ,
             start_totalizer float default null,
             end_totalizer float default null,
             start_time VARCHAR(50) DEFAULT NULL,
             end_time VARCHAR(50) DEFAULT NULL,
             liters float default null,
             unit_price float default null,
             amount float default null,
             read_at varchar(50) null,
             uploaded int default 0)''')


#MIGRATION 2    
c.execute('''CREATE TABLE IF NOT EXISTS totalizers
             (id integer primary key AUTOINCREMENT,
             device_address VARCHAR(50) DEFAULT NULL,
             pump_id int default null,
             totalizer_money float default null,
             totalizer_volume float default null,
             read_at varchar(50) default null,
             uploaded int default 0)''')


#MIGRATION 3    
c.execute('''CREATE TABLE IF NOT EXISTS prices
             (id integer primary key AUTOINCREMENT,
             device_address VARCHAR(50) DEFAULT NULL,
             pump_id int default null,
             price float default null,
             set_by float default null,
             set_at VARCHAR(50) DEFAULT NULL,
             uploaded int default 0)''')

#MIGRATION 4
try:
    
    c.execute('''ALTER table prices ADD COLUMN time_schedule varchar(50) default null''')
    print('column time_schedule added successfully')

except Exception as e:
    print(e)
    print('column time_schedule likely added already')
#MIGRATION 5   
try:
    
    c.execute('''ALTER table prices ADD COLUMN in_use INTEGER default 1''')
    print('column in_use added successfully')

except Exception as e:
    print(e)
    print('column in_use likely added already')
    
#MIGRATION 6
c.execute('''CREATE TABLE IF NOT EXISTS scheduled_prices
             (id integer primary key AUTOINCREMENT,
             device_address VARCHAR(50) DEFAULT NULL,
             pump_id int default null,
             price float default null,
             set_by float default null,
             set_at VARCHAR(50) DEFAULT NULL,
             uploaded int default 0,
             used int default 0)''')

try:
    
    c.execute('''ALTER table scheduled_prices ADD COLUMN time_schedule varchar(50) default null''')
    print('column time_schedule added successfully')

except Exception as e:
    print(e)
    print('column time_schedule likely added already')

conn.commit()
conn.close()
print('done')