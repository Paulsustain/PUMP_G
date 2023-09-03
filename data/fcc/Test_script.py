import serial
import threading
from serial import Serial
from time import sleep
import pump_parser
import helpers
import services
from datetime import datetime as dt
import db_handler
client=Serial(port='/dev/MTC_SERIAL',baudrate=5787,timeout=1,parity=serial.PARITY_EVEN,stopbits=serial.STOPBITS_ONE,bytesize=serial.EIGHTBITS)
start_totalizer=None
end_totalizer=None
start_time=None
end_time=None
#get_totalizers(1)
ADDRESS=1
device_address=helpers.get_device_mac_address()
CURRENT_USER='Rilwan'
STATUS=None
SELLING=False
CURRENT_PRICE=0


##while True:
##    client.write(bytearray([0x11]))
##    print('message sent')
##    sleep(1)
##    message=client.read(1)
##    #print('message first byte is: {}'.format(message))
##    while client.inWaiting():
##        message+=client.read()
##        #print(message)
##        sleep(0.01)
##    print('reaceived byte is: {}'.format(message.hex()))

def get_totalizers(pump_address):
    hex_code=0x50+pump_address
    response=write_to_serial(bytearray([hex_code]))
    total_volume,total_money=pump_parser.totalizer_parser(response)
    get_status(pump_address)
    read_at=dt.now().strftime('%Y-%m-%d %H:%M:%S')
    print(read_at)
    return (pump_address,total_money,total_volume,read_at)
    #db_handler.insert_totalizer(1,pump_address,total_money,total_volume,read_at)
    
def store_totalizer(device_address,pump_address,total_money,total_volume,read_at):
    services.insert_totalizer(device_address,pump_address,total_money,total_volume,read_at)
    
def store_transaction_details(device_address,pump_id,start_totalizer,end_totalizer,start_time,end_time,liters,unit_price,amount,read_at):
    print('*********start totalizers is: {}********'.format(start_totalizer))
    services.insert_transaction_details(device_address,pump_id,start_totalizer,end_totalizer,start_time,end_time,liters,unit_price,amount,read_at)
   
def get_transaction_details(pump_address):
    hex_code=0x40+pump_address
    response=write_to_serial(bytearray([hex_code]))
    volume,money,ppu=pump_parser.transaction_parser(response)
    get_status(pump_address)
    read_at=dt.now().strftime('%Y-%m-%d %H:%M:%S')
    print(read_at)
    return (pump_address,money,volume,ppu,read_at)
    #db_handler.insert_totalizer(1,pump_address,total_money,total_volume,read_at)
def prep_data(pump_address):
    print('ran')
    hex_code=0x20+pump_address
    response=write_to_serial(bytearray([hex_code]))
    print(response)
    return response
    
def get_status(pump_address):
    hex_code=0x00+pump_address
    response=write_to_serial(bytearray([hex_code]))
    return(pump_parser.parse_status(response)) 


def authorize(pump_address):
    print('ran')
    hex_code=0x10+pump_address
    write_to_serial(bytearray([hex_code]))
    get_status(pump_address)
    
def write_to_serial(code):
    #print(code)
    client.close()
    client.open()
    client.write(code)
    print('message sent')
    sleep(1)
    message=client.read(1)
    #print('message first byte is: {}'.format(message))
    while client.inWaiting():
        message+=client.read()
        #print(message)
        sleep(0.01)
    print('reaceived byte is: {}'.format(message.hex()))
    return message

def write_prices(code,address):
    #print(code)
    client.close()
    client.open()
    client.write(code)
    print('message sent')
    sleep(1)
    hex_code=0x00+address
    client.write(bytearray([hex_code]))
    message=client.read()
    #print('message first byte is: {}'.format(message))
    while client.inWaiting():
        message+=client.read()
        #print(message)
        sleep(0.01)
    print('reaceived byte is: {}'.format(message.hex()))
    status,address=pump_parser.parse_status(message) 
    return status

def check_for_call(address):
    global SELLING,start_time,start_totalizer
    status,address=get_status(address)
    if status==7:
        SELLING=True
        start_totalizer=get_totalizers(address)[2]
        print('start totalizers is: {}'.format(start_totalizer))
        price=services.get_local_price(address)
        if price:
            price=price[3]
            set_device_price(price,address,1)
            set_device_price(price,address,2)
        authorize(address)
        status,address=get_status(address)
        if status == 9:
            current_time=dt.now().strftime('%Y-%m-%d %H:%M:%S')
            start_time=current_time
            
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

def get_remote_price(device_address):
    print('**got into remote prie ***')
    remote_price_details=db_handler.get_remote_price(device_address)
    print('remote price_details is: {}'.format(remote_price_details))
    ids=save_remote_price(remote_price_details)
    if ids:
        db_handler.confirm_remote_prices(ids)


def compare_prices():
    global CURRENT_PRICE
    try:
        price_details=services.get_local_price(ADDRESS)
        new_price=price_details[3]
        if new_price != CURRENT_PRICE:
            set_device_price(new_price,ADDRESS,1)
            set_device_price(new_price,ADDRESS,2)
            CURRENT_PRICE=new_price
    except Exception as e:
        print(e)
        
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

def pricing_routine():
    get_remote_price(device_address)
    check_scheduled_price()
    compare_prices()
    pass
    
def run_test():
    global SELLING,ADDRESS,pricing
    while True:
        try:
            print('***got here ***')
            print(pricing)
            print(pricing.is_alive())
            if not pricing.is_alive():
                print('thread not alive')
                try:
                    pricing.join()
                except Exception as e:
                    print(e)
                pricing=threading.Thread(target= pricing_routine)
                pricing.start()
            else:
                print('thread still alive, skip')
            check_for_call(ADDRESS)
            status,address=get_status(ADDRESS)
            print('SELLING IS : {}'.format(SELLING))
            if status != 9 and SELLING==True:
                current_time=dt.now().strftime('%Y-%m-%d %H:%M:%S')
                end_time=current_time
                pump_address,total_money,total_volume,read_at=get_totalizers(ADDRESS)
                store_total=threading.Thread(target= store_totalizer,args=(device_address,pump_address,total_money,total_volume,read_at,))
                store_total.start()
                #store_totalizer(device_address,pump_address,total_money,total_volume,read_at)
                end_totalizer=total_volume
                print('************ GOT HERE ***********')
                pump_address,money,volume,ppu,read_at = get_transaction_details(ADDRESS)
                store_transaction=threading.Thread(target=store_transaction_details,args=(device_address,ADDRESS,start_totalizer,end_totalizer,start_time,end_time,volume,ppu,money,read_at,))
                store_transaction.start()
                #store_transaction_details(device_address,ADDRESS,start_totalizer,end_totalizer,start_time,end_time,volume,ppu,money,read_at)
                #get_totalizers(ADDRESS)
                SELLING=False
        except Exception as e:
            print(e)
        sleep(2)
        print('**done**')
    ##get_transaction_details()



       


price_details=services.get_local_price(ADDRESS)
CURRENT_PRICE=price_details[3]
set_device_price(CURRENT_PRICE,ADDRESS,1)
set_device_price(CURRENT_PRICE,ADDRESS,2)
pricing=threading.Thread(target= pricing_routine)
run_test()
#set_price(0.5,ADDRESS,1)
#set_price(20,ADDRESS,2)
