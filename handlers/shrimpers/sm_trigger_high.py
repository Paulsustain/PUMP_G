import sys
sys.path.append('/home/pi/smartpump/services/atg')
sys.path.append('/home/pi/smartpump/helpers')
import RPi.GPIO as GPIO
import time
import main_logger
my_logger=main_logger.get_logger(__name__)


GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
 
GPIO.setup(37,GPIO.OUT)

def sm_high():
    try:
        GPIO.output(37,GPIO.LOW)
        print('Pin low')
        time.sleep(5)
        GPIO.output(37,GPIO.HIGH)
        print('Pin high')
        time.sleep(5)
        GPIO.output(37,GPIO.LOW)
        print('Pin low')
    except Exception as e:
        print(e)
        my_logger.exception(e)
        
    
    
if __name__ =='__main__':
    sm_high()

    


