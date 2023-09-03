import sys
sys.path.append('/home/pi/smartpump/helpers')
sys.path.append('/home/pi/smartpump/handlers/fcc')
sys.path.append('/home/pi/smartpump/services/fcc')
import db_handler
import main_logger
import re
import helper
import json
from datetime import datetime
import requests
import services
from mysql.connector import MySQLConnection, Error

my_logger=main_logger.get_logger(__name__)
REMOTE_API_URL = 'https://api.smarteye.com.au/api/v1/'

def reformat_transaction_details(logs):
    reformed=[]
    for log in logs:
        payload = {
        'Nozzle_address': log[2],
        'Device': log[15],
        'Site': log[14],
        'Transaction_start_time': log[7],
        'Transaction_stop_time': log[8],
        'Transaction_raw_volume': log[9],
        'Raw_transaction_price_per_unit': log[10],
        'Pump_mac_address': log[1],
        'Transaction_start_pump_totalizer_volume': log[3],
        'Transaction_stop_pump_totalizer_volume': log[4],
        'Transaction_start_pump_totalizer_amount': log[5],
        'Transaction_stop_pump_totalizer_amount': log[6],
        'Transaction_raw_amount': log[11]
        }
        reformed.append(payload)
    return reformed
    
def upload_transaction_log():
     #get current local config for transmit interval
    transmit= json.loads(services.get_device_config_by_slug('DEVICE_DETAILS')[0])['active']
    if transmit:
        txn=services.get_unuploaded_transactions()
        if not txn: return None
        print(txn)
        #ids=[tuple(list(data[0])) for data in txn]
        ids = []
        for value in txn:
            id = []
            id.append(value[0])
            ids.append(tuple(id))
        print(txn)
        data=reformat_transaction_details(txn)
        print(data)
        print(ids)
        try:
            if len(data) > 0:
                 json_data = json.dumps(data)
                 post_data = []
                 post_data.append(json_data)
                 print(json_data)
                 headers = {'Content-type': 'application/json'}
                 print(REMOTE_API_URL +'data_logger/')
                 r = requests.post(REMOTE_API_URL +'smartpump/transaction_logger/', data = json_data, headers = headers)
                 if(r.status_code == 201):
                     my_logger.debug('data saved remotely')
                     print('data saved remotely')
                     services.update_uploaded_transactions(ids)
                 else:
                     response=r.content.decode()
                     print(response)
                     my_logger.error('unable to upload data')
                     my_logger.debug(response)
            else:
             print('no item saved locally')
             my_logger.debug('no item saved locally')
        except Error as e:
            print('Error:', e)
            my_logger.exception(e)
        except Exception as e:
            print ('Exception:', e)
            my_logger.exception(e)
                

def upload_local_transaction_logs():
    txn=services.get_unuploaded_transactions()
    if not txn: return None
    print(txn)
    #ids=[tuple(list(data[0])) for data in txn]
    ids = []
    for value in txn:
        id = []
        id.append(value[0])
        ids.append(tuple(id))
    print(txn)
    print(ids)
    trimmed=[tx[1:-1] for tx in txn]
    result=db_handler.insert_transaction_details(trimmed)
    if result:
        services.update_uploaded_transactions(ids)
        return True
    else:
        return False
    

def upload_local_totalizer_logs():
    ttlz=services.get_unuploaded_totalizers()
    if not ttlz: return None
    ids = []
    for value in ttlz:
        id = []
        id.append(value[0])
        ids.append(tuple(id))
    print(ttlz)
    print(ids)
    trimmed=[tz[1:-1] for tz in ttlz]
    result=db_handler.insert_totalizer(trimmed)
    print(result)
    if result:
        services.update_uploaded_totalizers(ids)
        return True
    else:
        return False

def upload_online_status():
    result=get_pump_statuses()
    dumps=json.dumps(result)
    print(dumps)
    db_handler.upload_online_status(dumps)
    #print(result)

def check_online_status(last_time_updated,current_time):
    print(last_time_updated,current_time)
    fmt = '%Y-%m-%d %H:%M:%S'
    start = datetime.strptime(last_time_updated, fmt)
    end = datetime.strptime(current_time, fmt)
    minutes=(end - start).total_seconds() / 60.0
    
    print('minute difference is: {}'.format(minutes))
    if minutes < 5:
        print('online')
        return 1
    else:
        print('offline')
        return 0
    
def get_pump_statuses():
    current_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    time_list=services.get_last_status_update_time()
    online_status_list=[]
    for times in time_list:
        online_status=check_online_status(times[1],current_time)
        online_status_list.append([times[0],online_status])
    return online_status_list

def get_device_config():
    MAC = helper.get_device_mac_address()
    r = requests.post(REMOTE_API_URL+'devices/remote_config/', data={"mac_address": MAC})
    if(r.status_code == 200):
        return r.json()['data']
        
    else:
        return {}

def test_func():
    print('called')
    
def get_smartpump_device_config():
    MAC = helper.get_device_mac_address()
    r = requests.post(REMOTE_API_URL+'smartpump/remote_config/', data={"mac_address": MAC})
    #print(REMOTE_API_URL+'smartpump/remote_config/')
    #r = requests.get(REMOTE_API_URL+'smartpump/remote_config/', data={"mac_address": 'b8:27:eb:65:36:c9'})
    print(r.status_code)
    if(r.status_code == 200):
        return r.json()['data']
        
    else:
        return {}

if __name__=="__main__":
    #get_smartpump_device_config()
    upload_transaction_log()
    #upload_local_transaction_logs()
    #upload_transaction_log()
    #upload_online_status()
#upload_local_totalizer_logs()
