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
from datetime import datetime
my_logger=main_logger.get_logger(__name__)

def parse_status(status,address,check_totalizer,device_data):
    print('**** status is: {}'.format(status))
    site_id=device_data['site_id']
    device_id=device_data['device_id']
    if  status == 7:
        my_logger.debug('***handle or nozzle up***')
        print('***handle or nozzle up***')
        device_address=helper.get_device_mac_address()
        if check_totalizer:
            print('*************** check totalizer is: {} @ start of transaction*******************'.format(check_totalizer))
            pump_address,total_money,total_volume,read_at=gvr_frontier.get_totalizers(address)
            print(pump_address,total_money,total_volume,read_at)
            set_start_tx=threading.Thread(target=services.set_start_transaction_details,args=(device_address,pump_address,total_volume,total_money,read_at,site_id,device_id))
            set_start_tx.start()
        else:
            read_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            set_start_tx=threading.Thread(target=services.set_transaction_start,args=(device_address,address,read_at,site_id,device_id))
            set_start_tx.start()
        #services.set_start_transaction_details(device_address,pump_address,total_volume,total_money,read_at)
        gvr_frontier.authorize_call(address)
##        if status == 9:
##            #print('transaction authorization succesful')
##            #my_logger.debug('transaction authorization succesful')
##        else:
##            #print('unsuccesful transaction authorization ')
##            my_logger.debug('unsuccessful transaction authorization ')
##            services.clear_transaction_unauthorized(address)
            
    if  status == 'a' or status == 'b':
        #device_address=helper.get_device_mac_address()
        print(' end of transaction seen')
        device_address=gvr_pump_handler.device_address
        my_logger.debug('***transaction ended***')
        if check_totalizer:
            if services.is_open_totalizer_taken(address):
                print('*************** check totalizer is: {} @ end of tarnsaction*******************'.format(check_totalizer))
                pump_address,total_money,total_volume,read_at=gvr_frontier.get_totalizers(address)
                pump_address,money,liters,ppu,read_at = gvr_frontier.get_transaction_details(address)
                set_end_tx=threading.Thread(target=services.set_end_transaction_details,args=(pump_address,total_volume,total_money,liters,money,ppu,read_at))
                set_end_tx.start()
                update_totalizer=threading.Thread(target=services.update_totalizer_checker,args=(pump_address,))
                update_totalizer.start()
            
        else:
            total_money=total_volume=0
            pump_address,money,liters,ppu,read_at = gvr_frontier.get_transaction_details(address)
            set_end_tx=threading.Thread(target=services.set_transaction_end,args=(pump_address,liters,money,ppu,read_at))
            set_end_tx.start()
        #services.set_end_transaction_details(pump_address,total_volume,total_money,liters,money,ppu,read_at)
        
