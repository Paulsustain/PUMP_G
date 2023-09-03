from os import stat
import sys
sys.path.append('/home/pi/smartpump/data/fcc')
sys.path.append('/home/pi/smartpump/services/fcc')
sys.path.append('/home/pi/smartpump/helpers')
sys.path.append('/home/pi/smartpump/handlers/fcc')
import main_logger
from time import sleep
import helper
import services
import gvr_frontier
import gvr_pump_handler
import threading
import json
from datetime import datetime
my_logger=main_logger.get_logger(__name__)
pumps=[]

def start_transaction_details(address,device_address,device_data):
    site_id=device_data['site_id']
    device_id=device_data['device_id']
    #print('*************** check totalizer is: {} @ start of transaction*******************'.format(check_totalizer))
    pump_address,total_money,total_volume,read_at=gvr_frontier.get_totalizers(address)
    print(pump_address,total_money,total_volume,read_at)
    set_start_tx=threading.Thread(target=services.set_start_transaction_details,args=(device_address,pump_address,total_volume,total_money,read_at,site_id,device_id))
    set_start_tx.start()
    
def get_ppu_status(address):
    ppu= gvr_frontier.get_ppu(address)
    ppu=ppu/10
    print('ppu is',ppu)
    return ppu

def price_check():
    
    pumps= json.loads(services.get_device_config_by_slug('PUMP_DETAILS')[0])
    try:
        for nozzle in pumps:
            address=nozzle['nozzle_address']
            price=nozzle['price']
    except Exception as e:
        print(e)
    print('price check is ', price)
    return price

def end_transaction_details(address):
    #print('*************** check totalizer is: {} @ end of tarnsaction*******************'.format(check_totalizer))
    pump_address,total_money,total_volume,read_at=gvr_frontier.get_totalizers(address)
    start_totalizer=services.get_start_totalizer(address)
    print('start totalizer is: {} while current totalizer is: {}'.format(start_totalizer,total_volume))
    my_logger.info('start totalizer is: {} while current totalizer is: {} at {}'.format(start_totalizer,total_volume,read_at))
    if start_totalizer == total_volume:
        print('no valid transaction')
        my_logger.error('no valid transaction at: {}'.format(read_at))
        money=liters=ppu=0
    else:
        pump_address,money,liters,ppu,read_at = gvr_frontier.get_transaction_details(address)
    set_end_tx=threading.Thread(target=services.set_end_transaction_details,args=(pump_address,total_volume,total_money,liters,money,ppu,read_at))
    set_end_tx.start()
    set_transaction_ongoing=threading.Thread(target=services.update_running_transaction,args=(address,0,datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    set_transaction_ongoing.start()
    #gvr_pump_handler.change_ongoing_tx(address,0)
    #ongoing_transaction_status[address]=0

def parse_status(status,address,device_data):
    #global ongoing_tx
    
    ongoing_transaction_status=services.get_transaction_running_status(address)
    print('**** status is: {}'.format(status))
    print(ongoing_transaction_status)
    print('transaction_status is : {} for nozzle: {}'.format(ongoing_transaction_status,address))
    site_id=device_data['site_id']
    device_id=device_data['device_id']
    #ongoing_transaction=services.get_transaction_running_status(address)
    device_address=helper.get_device_mac_address()
    if status == 6 and ongoing_transaction_status:
        end_transaction_details(address)
        my_logger.warning('***Pump went off during transaction on nozzle {}, transaction ended***'.format(address))

    if  status == 7:
        if ongoing_transaction_status:
            end_transaction_details(address)
            #my_logger.info('*** Nozzle {} lifted up***'.format(address))
            my_logger.info('*** Nozzle {} lifted up* pump status is {}**'.format(address,status))
            print('***handle or nozzle up***')
            start_transaction_details(address,device_address,device_data)
            #services.set_start_transaction_details(device_address,pump_address,total_volume,total_money,read_at)
            #gvr_frontier.authorize_call(address)
        if (price_db == price_pump):
            my_logger.info('*** Nozzle {} lifted up* pump status is {}**'.format(address,status))
            print('***handle or nozzle up* status is {}**'.format(status))
            start_transaction_details(address,device_address,device_data)
            #services.set_start_transaction_details(device_address,pump_address,total_volume,total_money,read_at)
            gvr_frontier.authorize_call(address)
            my_logger.info('*** Nozzle {} Authorized to sell at price {}***'.format(address,price_db))
            
        if (price_db != price_pump):
            #my_logger.info('*** Nozzle {} lifted up***'.format(address))
            my_logger.info('*** Nozzle {} lifted up* pump status is {}**'.format(address,status))
            print('***handle or nozzle up***')
            set_price(address)
            start_transaction_details(address,device_address,device_data)
            #services.set_start_transaction_details(device_address,pump_address,total_volume,total_money,read_at)
            gvr_frontier.authorize_call(address)
            my_logger.warning('*** price from pump is {} while the price from remote config is {}***'.format(price_db,price_pump))
            my_logger.info('*** Nozzle {} Authorized to sell at price{}***'.format(address,price_db))
            
            
    if status == 8:
        my_logger.info('*** Nozzle {} Authorized/Not Delivering(Idle)***'.format(address))
    '''if status ==9:
        my_logger.debug('***Transaction Ongoing on Nozzle  {}***'.format(address))'''
        
            
    
    '''condition = True  #services.set_end_transaction_details(pump_address,total_volume,total_money,liters,money,ppu,read_at)
    while condition:
        if status==9:
            my_logger.debug('***Transaction Ongoing on Nozzle  {}***'.format(address))
            condition = False '''
    
    
    if status==9:
        if not ongoing_transaction_status:
            set_transaction_ongoing=threading.Thread(target=services.update_running_transaction,args=(address,1,datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            set_transaction_ongoing.start()
##            gvr_pump_handler.change_ongoing_tx(address,1)
##            print('transaction_status is : {} for nozzle {} after increment'.format(gvr_pump_handler.ongoing_transaction_status[address],address))
##
        #target=services.update_running_transaction(address,1,datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            
    if  status == 'a' or status == 'b':
        #device_address=helper.get_device_mac_address()
        print(' end of transaction seen')
        my_logger.info('***Transaction ended on Nozzle  {}***'.format(address))
        end_transaction_details(address)
 
 
def set_price(address):
    #for nozzle in pumps:
    #address=nozzle['nozzle_address']
    #price=services.get_local_price(address)
    price=price_check()
    #price=10
    status=gvr_frontier.get_status(address)[0]
    gvr_frontier.set_device_price(price,address,1,status)
    #gvr_frontier.set_device_price(price,address,2,status)
    #services.clear_restart_flag()


price_pump=get_ppu_status(1)
price_db=price_check()
