import sys
sys.path.append('/home/pi/smartpump/services/fcc')
import services
sys.path.append('/home/pi/smartpump/helpers')
import main_logger
my_logger=main_logger.get_logger(__name__)

def totalizer_parser(totalizer_byte):
    total_volume=parse_data('total volume',totalizer_byte,16,1,'f9')
    total_money=parse_data('total money',totalizer_byte,16,1,'fa')
    return (total_volume,total_money)
def ppu_parser(totalizer_byte):
    ppu=parse_data('total volume',totalizer_byte,8,1,'f4')
    return (ppu)

def parse_data(text,data,byte_number,divisor,splitter):
    if not data:
        return
    hex_string=data.hex()
    splitted= hex_string.split(splitter)
    extract=splitted[1][:byte_number]
    print('extract is: {}'.format(extract))    
    actual_data=''
    for x in range(len(extract),0,-2):
        actual_data+=extract[x-1]
    print('unprocessed {} is: {}'.format(text,actual_data))
    real_data=int(actual_data)/divisor
    print('processed {} is: {}'.format(text,real_data))
    return real_data

def transaction_parser(transaction_byte):
    volume=parse_data('volume',transaction_byte,12,1,'f9')
    money=parse_data('money',transaction_byte,12,1,'fa')
    ppu=parse_data('ppu',transaction_byte,8,1,'f7')
    return (volume,money,ppu)


def get_pump_decimal_data(address):
    my_byte=bytearray([])
    my_byte.append(0xff)
    my_byte.append(0xe3)
    my_byte.append(0xfe)
    my_byte.append(0xee)
    my_byte.append(0xe0)
    my_byte.append(0xe0)
    my_byte.append(0xfb)
    lsbs=get_lsbs(my_byte)
    twos=get_twos_compliment(lsbs)
    res=twos&0x0f
    my_byte.append((0xe0+res))
    my_byte.append(0xf0)
    #print('byte generated is: {}'.format(my_byte))
    return my_byte

def get_price_change_data(address,price,level):
    try:
        price_float=float(price)
        print('unformatted splitted: {}'.format(price))
        price_string='%05.1f'% price
        print('formatted splitted: {}'.format(price_string))
        splitted=price_string.split('.')
        first_decimal = int(splitted[1][0])
        my_byte=bytearray([])
        my_byte.append(0xff)
        my_byte.append(0xe5)
        if level ==1:
            my_byte.append(0xf4)
        elif level ==2:
            my_byte.append(0xf5)
        else:
            my_byte.append(0xf4)
        my_byte.append(0xf6)
        my_byte.append(0xe0)
        my_byte.append(0xf7)
        my_byte.append((0xe0+first_decimal))
        for x in range(len(splitted[0]),0,-1):
            my_byte.append((0xe0+int(splitted[0][x-1])))
        my_byte.append(0xfb)
        lsbs=get_lsbs(my_byte)
        twos=get_twos_compliment(lsbs)
        res=twos&0x0f
        my_byte.append((0xe0+res))
        my_byte.append(0xf0)
        return my_byte
        
    except Exception as e:
        print(e)
        return None
    
def get_lsbs(bytearrays):
    lsb=0
    for byte in bytearrays:
       lsb+=(byte&0x0f)
    return lsb

def get_twos_compliment(byte):
    temp=0x01
    ans=0
    for xx in range(8):
        yy=byte&(temp<<xx)
        yy=yy>>xx
        if yy: yy=0
        else: yy=1
        ans+=yy<<xx
    return ans+1
def parse_status(response):
    if not response:
        return None
    response=response.hex()
    try:
        status=int(response[0])
        address=int(response[1])
    except Exception as e:
        status=response[0]
        address=int(response[1])
        print(e)
    #print('status is; {} and address is: {}'.format(status,address))
    #services.set_current_status(status,address)
    #my_logger.debug('status is; {} and address is: {}'.format(status,address))
    return (status,address)

if __name__ =="__main__":
    pass
#result=get_twos_compliment(0x33)
#print('the twos compliment is: {}'.format(bin(result)))
#res=result&0x0f
#print('final result is: {}'.format(hex(res)))
#result=get_lsbs(bytearray([0xff,0xf1,0xf8,0xe1,0xe1,0xe1,0xe1,0xe1,0xf6,0xe1,0xf4,0xfb]))
#print('the lsbs is: {}'.format(hex(result)))
#byte_code=get_price_change_data(1,146.6,1)
#print('bytecode is: {}'.format(byte_code.hex()))


