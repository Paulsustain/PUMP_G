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
PRICE_CHANGE_CHECK_INTERVAL=30
PUMP_CHANGE_CHECK_INTERVAL=10
price_change_counter=[]
device_address=helper.get_device_mac_address()
pumps=[]
#statuses=[]
#logger=logging.getLogger(__name__)
##def get_status_by_id(statuses,address):
##    my_status=0
##    for status in statuses:
##        if status[0]==address:
##            my_status=status[1]
##    return my_status

def set_prices_at_code_start():
    global price_change_counter
    pumps= json.loads(services.get_device_config_by_slug('PUMP_DETAILS')[0])
    try:
        for nozzle in pumps:
            address=nozzle['nozzle_address']
            price=services.get_local_price(address)[3]
            #price=10
            status=gvr_frontier.get_status(nozzle['nozzle_address'])[0]
            price_change_counter.append(0)
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
    try:
        global pumps,authorizer_using_serial,serial_busy
        statuses=[]
        for pump in pumps:
            #print(pumps)
            status=gvr_frontier.get_status(pump['nozzle_address'])[0]
            print(status)
            if status == 7:
                call_authorizer_single(pump['nozzle_address'])
            statuses.append([pump['nozzle_address'],status])
        end_of_transaction_getter(statuses)
    except Exception as e:
        print(e)
            
def end_of_transaction_getter(statuses):
    global pumps,tx_end_using_serial
    for status_list in statuses:
        status=status_list[1]
        address=status_list[0]
        if status == 'a' or status == 'b':
            #tx_end_using_serial=True
            #pump_address,total_money,total_volume,read_at=gvr_frontier.get_totalizers(address)
            pump_address,money,liters,ppu,read_at = gvr_frontier.get_transaction_details(address)
            #tx_end_using_serial=False
            total_volume=total_money=0
            set_end_tx=threading.Thread(target=services.set_end_transaction_details,args=(pump_address,total_volume,total_money,liters,money,ppu,read_at))
            set_end_tx.start()

def call_authorizer_single(address):
    print('***handle or nozzle up***')
    #pump_address,total_money,total_volume,read_at=gvr_frontier.get_totalizers(address)
    status = gvr_frontier.authorize(address)
    #print(pump_address,total_money,total_volume,read_at)
    #authorizer_using_serial=False
    #services.set_start_transaction_details(device_address,pump_address,total_volume,total_money,read_at)
    #set_start_tx=threading.Thread(target=services.set_start_transaction_details,args=(device_address,pump_address,total_volume,total_money,read_at))
    #set_start_tx.start()
    
def call_authorizer(statuses):
    global pumps,authorizer_using_serial
    for status_list in statuses:
        status=status_list[1]
        address=status_list[0]
        if status == 7:
            #authorizer_using_serial=True
            print('***handle or nozzle up***')
            status = gvr_frontier.authorize(address)
            pump_address,total_money,total_volume,read_at=gvr_frontier.get_totalizers(address)
            print(pump_address,total_money,total_volume,read_at)
            #authorizer_using_serial=False
            services.set_start_transaction_details(device_address,pump_address,total_volume,total_money,read_at)
            set_start_tx=threading.Thread(target=services.set_start_transaction_details,args=(device_address,pump_address,total_volume,total_money,read_at))
            set_start_tx.start()

def pump_number_updater():
    while True:
        global pumps
        pumps= json.loads(services.get_device_config_by_slug('PUMP_DETAILS')[0]) 
        sleep(10)
    
def handle_pumps_new():
    update_pumps=threading.Thread(target=pump_number_updater)
    update_pumps.start()
    while True:
        status_manager()

def pump_handler_three():
    try:
    #pumps=[{'pump_id': 1, 'site_id': 1, 'protocol': 'GVR', 'site_name': 'Smartflow', 'Tank_index': 1, 'nozzle_address': 1, 'price': 100}, {'pump_id': 1, 'site_id': 1, 'protocol': 'GVR', 'site_name': 'Smartflow', 'Tank_index': 1, 'nozzle_address': 2, 'price': 100}, {'pump_id': 1, 'site_id': 1, 'protocol': 'GVR', 'site_name': 'Smartflow', 'Tank_index': 1, 'nozzle_address': 3, 'price': 100}]
    #restart_status=services.get_restart_flag()
    #set_prices_at_restart(restart_status)
    ##previous_statuses=services.get_previous_status()
    #print(restart_status)
        
    #print(previous_statuses)
    #print(pumps)
        for index,pump in enumerate(pumps):
            #print(pump)
            pump_protocol=pump['protocol']
            if pump_protocol=='GVR':
                address=pump['nozzle_address']   
                status=gvr_frontier.get_status(address)[0]
                if status:
                    state_helper.parse_status_two(status,address)
                    #print('*&*^&&&^&^',price_change_counter)
                    price_change_counter[index]+=1
                    #print('counter for {} is: {}'.format(address,price_change_counter[index]))
                    if price_change_counter[index]> PRICE_CHANGE_CHECK_INTERVAL:
                        print('****price change check*****')
                        services.effect_price_change(address,status)
                        price_change_counter[index] = 0
    except Exception as e:
        print(e)

def pump_handler_two():
    try:
        status_manager()
    except Exception as e:
        print(e)
        
def pump_handler_one():
    try:
    #pumps=[{'pump_id': 1, 'site_id': 1, 'protocol': 'GVR', 'site_name': 'Smartflow', 'Tank_index': 1, 'nozzle_address': 1, 'price': 100}, {'pump_id': 1, 'site_id': 1, 'protocol': 'GVR', 'site_name': 'Smartflow', 'Tank_index': 1, 'nozzle_address': 2, 'price': 100}, {'pump_id': 1, 'site_id': 1, 'protocol': 'GVR', 'site_name': 'Smartflow', 'Tank_index': 1, 'nozzle_address': 3, 'price': 100}]
    #restart_status=services.get_restart_flag()
    #set_prices_at_restart(restart_status)
    ##previous_statuses=services.get_previous_status()
    #print(restart_status)
        
    #print(previous_statuses)
    #print(pumps)
        for index,pump in enumerate(pumps):
            #print(pump)
            pump_protocol=pump['protocol']
            if pump_protocol=='GVR':
                address=pump['nozzle_address']   
                status=gvr_frontier.get_status(address)[0]
                if status:
                    state_helper.parse_status(status,address)
                    #print('*&*^&&&^&^',price_change_counter)
                    price_change_counter[index]+=1
                    #print('counter for {} is: {}'.format(address,price_change_counter[index]))
                    if price_change_counter[index]> PRICE_CHANGE_CHECK_INTERVAL:
                        print('****price change check*****')
                        services.effect_price_change(address,status)
                        price_change_counter[index] = 0
    except Exception as e:
        print(e)
        
def handle_pumps():
    global price_change_counter,pumps
    update_pumps=threading.Thread(target=pump_number_updater)
    update_pumps.start()
    set_prices_at_code_start()
    #pumps= json.loads(services.get_device_config_by_slug('PUMP_DETAILS')[0])
    #pump_change_count=0
    while True:
        pump_handler_one()
        #sleep(0.05)    
if __name__=="__main__":
    handle_pumps()