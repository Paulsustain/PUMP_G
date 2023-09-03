import sys
import os
import io
import sqlite3
sys.path.append('/home/pi/smartpump/helpers')
import helper
dir_path = os.path.dirname(os.path.realpath(__file__))
print(dir_path)
conn = sqlite3.connect(dir_path+'/store.db')
c = conn.cursor()
device_address=helper.get_device_mac_address()

#MIGRATION 1    
c.execute('''CREATE TABLE IF NOT EXISTS transaction_details
             (id integer primary key AUTOINCREMENT,
             device_address VARCHAR(50) DEFAULT NULL,
             nozzle_address INT DEFAULT NULL ,
             start_totalizer float default null,
             end_totalizer float default null,
             start_totalizer_money float default null,
             end_totalizer_money float default null,
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
             nozzle_address int default null,
             totalizer_money float default null,
             totalizer_volume float default null,
             read_at varchar(50) default null,
             uploaded int default 0)''')


#MIGRATION 3    
c.execute('''CREATE TABLE IF NOT EXISTS prices
             (id integer primary key AUTOINCREMENT,
             device_address VARCHAR(50) DEFAULT NULL,
             nozzle_address int default null,
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

query = "SELECT * FROM prices"

result=c.execute(query)
if(len(c.fetchall()) == 0):
    from datetime import datetime
    for number in range(1,17):
        c.execute("INSERT INTO prices (device_address,nozzle_address,price,set_by,set_at) VALUES(?,?,?,?,?)", (device_address,number,162,'Smartflow', datetime.now().strftime('%Y-%m-%d %H:%M:%S')))


#MIGRATION 6
c.execute('''CREATE TABLE IF NOT EXISTS scheduled_prices
             (id integer primary key AUTOINCREMENT,
             device_address VARCHAR(50) DEFAULT NULL,
             nozzle_address int default null,
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
    

#MIGRATION 2
c.execute('''CREATE TABLE IF NOT EXISTS device_config
             (id integer primary key AUTOINCREMENT, slug text, value VARCHAR(50), updated_at text default NULL)''')

#MIGRATION 3
query = "SELECT value FROM device_config where slug = 'CAN_TRANSMIT'"
result=c.execute(query)

if(len(c.fetchall()) == 0): 
    c.execute("INSERT INTO device_config (slug, value) VALUES('CAN_TRANSMIT', 1)")

#MIGRATION 4
query = "SELECT value FROM device_config where slug = 'TRANSMIT_INTERVAL'"
result=c.execute(query)

if(len(c.fetchall()) == 0): 
    c.execute("INSERT INTO device_config (slug, value) VALUES('TRANSMIT_INTERVAL', 180)")

#MIGRATION 5
query = "SELECT value FROM device_config where slug = 'FIRMWARE_VERSION'"
result=c.execute(query)

if(len(c.fetchall()) == 0):   
    c.execute("INSERT INTO device_config (slug, value) VALUES('FIRMWARE_VERSION', '1.0.0' )")

query = "SELECT value FROM device_config where slug = 'ADC_SENSOR_COUNT'"
result=c.execute(query)

if(len(c.fetchall()) == 0):   
    c.execute("INSERT INTO device_config (slug, value) VALUES('ADC_SENSOR_COUNT', '1' )")

#MIGRATION 13, UPDATE DEVICE CONFIG TABLE
import json

query = "SELECT value FROM device_config where slug = 'TANK_DETAILS'"
result=c.execute(query)
if(len(c.fetchall()) == 0):
    tank_details = [
        {"Name": "Test_MTC", "Control_mode": "C", "Tank_controller": "MTC", "Controller_polling_address": 1, "Tank_index": 1},
        {"Name": "Test_TLS", "Control_mode": "C", "Tank_controller": "TLS", "Controller_polling_address": 1, "Tank_index": 1},
        {"Name": "Test_Analog", "Control_mode": "S", "Tank_controller": "HYD", "Controller_polling_address": 1, "Tank_index": 1}
    ]
    tank_details = json.dumps(tank_details)
    c.execute("INSERT INTO device_config (slug, value) VALUES(?, ?)", ('TANK_DETAILS', tank_details))

query = "SELECT value FROM device_config where slug = 'DEVICE_DETAILS'"
result=c.execute(query)
if(len(c.fetchall())==0):
    device_details = {'transmit_interval': 120, 'active': True}
    device_details = json.dumps(device_details)

    c.execute("INSERT INTO device_config (slug, value) VALUES(?, ?)", ('DEVICE_DETAILS', device_details))

query = "SELECT value FROM device_config where slug = 'PUMP_DETAILS'"
result=c.execute(query)
if(len(c.fetchall()) == 0):
    pump_details = [
        {"pump_id": 1, "nozzle_address":1, "protocol": "GVR", "price": 100, "site_name":"Smartflow", "Tank_index": 1,"site_id":1,"device_id":3},
        {"pump_id": 1, "nozzle_address":2, "protocol": "GVR", "price": 100, "site_name":"Smartflow", "Tank_index": 1,"site_id":1,"device_id":3}
    ]
    pump_details = json.dumps(pump_details)
    c.execute("INSERT INTO device_config (slug, value) VALUES(?, ?)", ('PUMP_DETAILS', pump_details))

#MIGRATION 2

c.execute('''CREATE TABLE IF NOT EXISTS restart_flag
             (id integer primary key AUTOINCREMENT, restart integer, updated_at text default NULL)''')

query = "SELECT restart FROM restart_flag"

result=c.execute(query)
if(len(c.fetchall()) == 0):
    from datetime import datetime
    c.execute("INSERT INTO restart_flag (restart,updated_at) VALUES(?, ?)", (0, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    
    
c.execute('''CREATE TABLE IF NOT EXISTS pump_status
             (id integer primary key AUTOINCREMENT, pump_id integer, pump_status integer, updated_at text default NULL)''')

query = "SELECT * FROM pump_status"

result=c.execute(query)
if(len(c.fetchall()) == 0):
    from datetime import datetime
    for number in range(1,17):
        c.execute("INSERT INTO pump_status (pump_id,pump_status,updated_at) VALUES(?, ?,?)", (number,6, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))


#MIGRATION 6
c.execute('''CREATE TABLE IF NOT EXISTS totalizer_check
             (id integer primary key AUTOINCREMENT,
             nozzle_address int default 1,
             last_checked_id int default null,
             last_checked_time VARCHAR(50) DEFAULT NULL,
             checked due default 0)''')

query = "SELECT * FROM totalizer_check"

result=c.execute(query)
if(len(c.fetchall()) == 0):
    from datetime import datetime
    for number in range(1,17):
        c.execute("INSERT INTO totalizer_check (nozzle_address,last_checked_id,last_checked_time) VALUES(?,?,?)", (number,1,datetime.now().strftime('%Y-%m-%d %H:%M:%S')))


try:
    
    c.execute('''ALTER table transaction_details ADD COLUMN site_id INTEGER default null''')
    print('column site_id added successfully')

except Exception as e:
    print(e)
    print('column site_id likely added already')
    
try:
    
    c.execute('''ALTER table transaction_details ADD COLUMN device_id INTEGER default null''')
    print('column device_id added successfully')

except Exception as e:
    print(e)
    print('column device_id likely added already')

conn.commit()
conn.close()
print('done') 