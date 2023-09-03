import serial
import os
import time

def main():
    gprs_conn = ["sudo poff gprs_connect", "sudo pon gprs_connect"]
    os.system(gprs_conn[0])
    time.sleep(2)
    os.system(gprs_conn[1])
    time.sleep(2)

if __name__ == '__main__':
    main()