import serial
import sys
sys.path.append('/home/pi/smartpump/helpers')
sys.path.append('/home/pi/smartpump/helpers/fcc')
from datetime import datetime as dt
import pump_parser
#import state_parser
import helper
from time import sleep
from serial import Serial
import logging
#logging.basicConfig(filename='',filemode='a',format='%(asctime)s - %(name)s -%(levelname)s -%(message)s')
import main_logger
my_logger=main_logger.get_logger(__name__)
client=Serial(port='/dev/PUMP_SERIAL',baudrate=5787,timeout=1,parity=serial.PARITY_EVEN,stopbits=serial.STOPBITS_ONE,bytesize=serial.EIGHTBITS)
#client=Serial(port='/dev/ttyAMA0',baudrate=5787,timeout=1,parity=serial.PARITY_EVEN,stopbits=serial.STOPBITS_ONE,bytesize=serial.EIGHTBITS)


def read_pump_transaction(address=1):
    pass
def change_pump_price(address=1):
    pass

def get_totalizers(pump_address):
    hex_code=0x50+pump_address
    response=write_to_serial(bytearray([hex_code]))
    total_volume,total_money=pump_parser.totalizer_parser(response)
    #get_status(pump_address)
    read_at=dt.now().strftime('%Y-%m-%d %H:%M:%S')
    #print(read_at)
    return (pump_address,total_money,total_volume,read_at)

def get_ppu(pump_address):
    hex_code=0x50+pump_address
    response=write_to_serial(bytearray([hex_code]))
    ppu=pump_parser.ppu_parser(response)
    #get_status(pump_address)
    read_at=dt.now().strftime('%Y-%m-%d %H:%M:%S')
    #print(read_at)
    return (ppu)


def get_status(pump_address):
    hex_code=0x00+pump_address
    response=write_to_serial(bytearray([hex_code]))
    return(pump_parser.parse_status(response)) 

def authorize(pump_address):
    print('ran')
    hex_code=0x10+pump_address
    write_to_serial(bytearray([hex_code]))
    status = get_status(pump_address)[0]
    return status

def authorize_call(pump_address):
    status=None
    #while status != 9:
    print('ran')
    hex_code=0x10+pump_address
    write_to_serial(bytearray([hex_code]),1)
    #status = get_status(pump_address)[0]
    #return status

def test():
    print('ran')
    #hex_code=0x0f
    response=write_to_serial(bytearray([0x01,0x02]))
    status=response
    #status = get_status(1)[0]
    #status=0
    return status
    
def set_device_price(price,address,level,status):
    #status,address=get_status(address)
    try:
        if status == 6 or status ==  7 :
            res=prep_data(address)
            temp= (res[0]&0xf0)>>4
            print(temp)
            if temp== 13:
                code=pump_parser.get_price_change_data(address,price,level)
                print(code)
                print('code to send is: {}'.format(code.hex()))
                status=write_prices(code,address)
                #status,address=get_status(address)
                if status:
                    print('price change successful')
                    current_time=dt.now().strftime('%Y-%m-%d %H:%M:%S')
                    #services.set_price(device_address,address,price,CURRENT_USER,current_time)
                else:
                    print('unsuccessful price change')
                    return None
    except Exception as e:
        print(e)
        return None
    return (status,price)

def get_decimal_places(address):
    status,address=get_status(address)
    if status == 6 or status ==  7 :
        res=prep_data(address)
        temp= (res[0]&0xf0)>>4
        print(temp)
        if temp== 13:
            code=pump_parser.get_pump_decimal_data(address)
            print('code to send is: {}'.format(code.hex()))
            write_to_serial(code)
            #status=write_prices(code,address)            
    pass
    
def get_transaction_details(pump_address=1):
    hex_code=0x40+pump_address
    print('**** trying to get transaction details****')
    #my_logger.debug('transaction details hex code sent is: {}'.format(hex_code))
    response=write_to_serial(bytearray([hex_code]))
    #my_logger.debug('transaction details response is: {}'.format(response))
    volume,money,ppu=pump_parser.transaction_parser(response)
    #volume=volume/1000
    #ppu=ppu/10
    #money=money/10
    
    #get_status(pump_address)
    read_at=dt.now().strftime('%Y-%m-%d %H:%M:%S')
    #print(read_at)
    my_logger.info('transaction details is: nozzle: {} money: {} volume: {} ppu: {} read_at: {}'.format(pump_address,money,volume,ppu,read_at))
    return (pump_address,money,volume,ppu,read_at)



    
def write_to_serial(code,auth=0):
    #print(code)
    #logging.debug('code sent to serial is: {}'.format(code.hex()))
    SERIAL_RETRY=3
    count = 0
    message = b''
    while count < SERIAL_RETRY and message == b'':
        client.close()
        client.open()
        client.write(code)
        #print('message sent')
        sleep(0.13)
        message=client.read(1)
        #print('message first byte is: {}'.format(message))
        while client.inWaiting():
            message+=client.read()
            #print(message)
            #sleep(0.01)
        print('received byte is: {}'.format(message.hex()))
        if message == b'' and auth == 1:
            break
        count += 1
    #logging.debug('reaceived byte is: {}'.format(message.hex()))
    return message

def prep_data(pump_address):
    print('ran')
    hex_code=0x20+pump_address
    response=write_to_serial(bytearray([hex_code]))
    print(response)
    return response
    

def write_prices(code,address):
    #print(code)
    #logging.debug('code sent to write_prices is: {} and address is:{}'.format(code.hex(),address))
    client.close()
    client.open()
    client.write(code)
    #print('message sent')
    sleep(0.13)
    hex_code=0x00+address
    client.write(bytearray([hex_code]))
    message=client.read()
    #print('message first byte is: {}'.format(message))
    while client.inWaiting():
        message+=client.read()
        #print(message)
        #sleep(0.01)
    print('reaceived byte is: {}'.format(message.hex()))
    #logging.debug('reaceived byte is: {}'.format(message.hex()))
    status,address=pump_parser.parse_status(message) 
    return status

if __name__ =="__main__":
    #get_totalizers(1)
    #get_decimal_places(1)
    #authorize(1)
    #test()
    get_status(1)
    #get_transaction_details(1)
   
    pass
