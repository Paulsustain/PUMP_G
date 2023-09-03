import sys
sys.path.append('/home/pi/smartpump/data/fcc')
sys.path.append('/home/pi/smartpump/services/fcc')
sys.path.append('/home/pi/smartpump/helpers/fcc')
sys.path.append('/home/pi/smartpump/helpers')
import helper
import main_logger
import gvr_frontier
import services
import state_helper
import json
import threading
from time import sleep
from datetime import datetime
PRICE_CHANGE_CHECK_INTERVAL=50
STATUS_UPDATE_INTERVAL=30
price_change_counter=0
status_update_counter=0
device_address=helper.get_device_mac_address()
site_id=None
pumps=[]
statuses=[None]*16
totalizer_checked_due_status=[None]*16
#logger=logging.getLogger(__name__)
##def get_status_by_id(statuses,address):
##    my_status=0
##    for status in statuses:
##        if status[0]==address:
##            my_status=status[1]
##    return my_status

def check_totalizer_due_status():
    global totalizer_checked_due_status,pumps
    while True:
        try:
            for nozzle in pumps:
                address=nozzle['nozzle_address']
                #number_of_transactions=services.count_transaction_since_last_totalizer(address)
                last_time_checked=services.get_time_since_last_totalizer(address)
                checked_due=check_time_expiry(last_time_checked)
                totalizer_checked_due_status[address]=checked_due
        except Exception as e:
            print(e)
        sleep(20)
                

def check_time_expiry(last_time):
    current_time=datetime.now()
    last_time=datetime.strptime(last_time,'%Y-%m-%d %H:%M:%S')
    current_time=datetime(current_time.year,current_time.month,current_time.day,0,0,0)
    last_time=datetime(last_time.year,last_time.month,last_time.day,0,0,0)
    day_diff=(current_time-last_time).days
    print('the days difference is: {}'.format(day_diff))
    if day_diff >= 1:
        return 1
    else:
        return 0
    
def set_prices_at_code_start():
    global price_change_counter
    pumps= json.loads(services.get_device_config_by_slug('PUMP_DETAILS')[0])
    try:
        for nozzle in pumps:
            address=nozzle['nozzle_address']
            price=services.get_local_price(address)[3]
            #price=10
            status=gvr_frontier.get_status(nozzle['nozzle_address'])[0]
            #price_change_counter.append(0)
            gvr_frontier.set_device_price(price,address,1,status)
            #gvr_frontier.set_device_price(price,address,2,status)
        print(price_change_counter)
    except Exception as e:
        print(e)
            
def set_prices_at_restart(flag):
    global price_change_counter
    if flag:
        for nozzle in pumps:
            address=nozzle['nozzle_address']
            price=services.get_local_price(address)
            #price=10
            status=gvr_frontier.get_status(pump['nozzle_address'])[0]
            gvr_frontier.set_device_price(price,address,1,status)
            #gvr_frontier.set_device_price(price,address,2,status)
        services.clear_restart_flag()
        

def status_manager():
     while True:
        for pump in pumps:
            address=pump['nozzle_address']
            if statuses[address]:
                services.set_current_status(statuses[address],address)
        sleep(5)
            
def price_change_manager():
    global statuses
    while True:
        for pump in pumps:
            address=pump['nozzle_address']
            services.effect_price_change(address,statuses[address])
        sleep(30)

def pump_number_updater():
    while True:
        global pumps
        pumps= json.loads(services.get_device_config_by_slug('PUMP_DETAILS')[0]) 
        sleep(30)
        
def pump_handler():
    global statuses,price_change_counter,status_update_counter
    try:
    #pumps=[{'pump_id': 1, 'site_id': 1, 'protocol': 'GVR', 'site_name': 'Smartflow', 'Tank_index': 1, 'nozzle_address': 1, 'price': 100}, {'pump_id': 1, 'site_id': 1, 'protocol': 'GVR', 'site_name': 'Smartflow', 'Tank_index': 1, 'nozzle_address': 2, 'price': 100}, {'pump_id': 1, 'site_id': 1, 'protocol': 'GVR', 'site_name': 'Smartflow', 'Tank_index': 1, 'nozzle_address': 3, 'price': 100}]
    #restart_status=services.get_restart_flag()
    #set_prices_at_restart(restart_status)
    ##previous_statuses=services.get_previous_status()
    #print(restart_status)
        
    #print(previous_statuses)
    #print(pumps)
        price_change_counter+=1
        status_update_counter+=1
        for index,pump in enumerate(pumps):
            #print(pump)
            device_data={'site_id': pump['site_id'],'device_id':pump['device_id']}
            pump_protocol=pump['protocol']
            #print(pump_protocol)
            if pump_protocol=='GVR':
                #print('eretgd')
                address=pump['nozzle_address']
                site_id=pump['site_id']
                status=gvr_frontier.get_status(address)[0]
                if status:
                    state_helper.parse_status(status,address,totalizer_checked_due_status[address],device_data)
                    statuses[address]=status
                    if price_change_counter >= PRICE_CHANGE_CHECK_INTERVAL:
                        services.effect_price_change(address,status)
                        #price_change_counter = 0
                    if status_update_counter >= STATUS_UPDATE_INTERVAL:
                        updater=threading.Thread(target=services.set_current_status,args=(status,address))
                        updater.start()
                        #status_update_counter = 0
        if price_change_counter >= PRICE_CHANGE_CHECK_INTERVAL:
            price_change_counter = 0
        if status_update_counter >= STATUS_UPDATE_INTERVAL:
           status_update_counter = 0     
    except Exception as e:
        print(e)
        
def handle_pumps():
    global price_change_counter,pumps
    update_pumps=threading.Thread(target=pump_number_updater)
    update_pumps.start()
    totalizer_checker=threading.Thread(target=check_totalizer_due_status)
    totalizer_checker.start()
##    update_status=threading.Thread(target=status_manager)
##    update_status.start()
##    price_updater=threading.Thread(target=price_change_manager)
##    price_updater.start()
    set_prices_at_code_start()
    #pumps= json.loads(services.get_device_config_by_slug('PUMP_DETAILS')[0])
    #pump_change_count=0
    try:
        while True:
            pump_handler()
            #sleep(0.05)
    except (KeyboardInterrupt):
        update_pumps.join()
        #update_status.join()
        #price_updater.join()
if __name__=="__main__":
    handle_pumps()
