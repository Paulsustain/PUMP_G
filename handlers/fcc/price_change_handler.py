import sys
sys.path.append('/home/pi/smartpump/services/fcc')
sys.path.append('/home/pi/smartpump/helpers')
sys.path.append('/home/pi/Desktop/GVR_PI')
import services
import helper
import db_handler
from datetime import datetime as dt
import json
import main_logger

my_logger=main_logger.get_logger(__name__)
device_address=helper.get_device_mac_address()
print(device_address)
def pricing_routine():
    get_remote_price(device_address)
    check_scheduled_price()
    #compare_prices()
    pass

def get_price(address):
    price=services.get_local_price(address)
    return price

def set_device_price(price,address,level):
    status,address=get_status(address)
    if status == 6 or status ==  7 :
        res=prep_data(address)
        temp= (res[0]&0xf0)>>4
        print(temp)
        if temp== 13:
            code=pump_parser.get_price_change_data(address,price,level)
            print('code to send is: {}'.format(code.hex()))
            status=write_prices(code,address)
            #status,address=get_status(address)
            if status:
                print('price change successful')
                current_time=dt.now().strftime('%Y-%m-%d %H:%M:%S')
                #services.set_price(device_address,address,price,CURRENT_USER,current_time)
            else: print('unsuccessful price change')
    return (status,price)

def check_scheduled_price():
    details=services.get_due_unused_scheduled_price()
    id_list=[]
    for detail in details:
        if detail:
            current_time=dt.now().strftime('%Y-%m-%d %H:%M:%S')
            _id,device_address,address,price,user,set_at,uploaded,time_scheduled,used=detail
            id=[]
            id.append(_id)
            id_list.append(tuple(id))
            services.set_price(device_address,address,price,user,current_time)
    if id_list:
        services.confirm_scheduled_price(id_list)
        
##def compare_prices():
##    global CURRENT_PRICE
##    try:
##        price_details=services.get_local_price(ADDRESS)
##        new_price=price_details[3]
##        if new_price != CURRENT_PRICE:
##            set_device_price(new_price,ADDRESS,1)
##            set_device_price(new_price,ADDRESS,2)
##            CURRENT_PRICE=new_price
##    except Exception as e:
##        print(e)

def save_remote_price(remote_price_details):
    if not remote_price_details:
        return None
    ids=[]
    current_time=dt.now().strftime('%Y-%m-%d %H:%M:%S')
    for remote_price_detail in remote_price_details:
        _id,device_address,address,price,user,set_at,time_scheduled,sent=remote_price_detail
        print('time scheduled is: {}'.format(time_scheduled))
        if not time_scheduled:
            res=services.set_price(device_address,address,price,user,current_time)
        else:
            res=services.set_scheduled_price(device_address,address,price,user,current_time,time_scheduled)
        if res:
            ids.append(_id)
    return ids

def get_remote_price(device_address):
    print('**got into remote price ***')
    #my_logger.debug('**got into remote_price**')
    remote_price_details=db_handler.get_remote_price(device_address)
    print('remote price_details is: {}'.format(remote_price_details))
    #my_logger.debug('remote price_details is: {}'.format(remote_price_details))
    ids=save_remote_price(remote_price_details)
    if ids:
        db_handler.confirm_remote_prices(ids)
        
if __name__ =="__main__":
    pricing_routine()