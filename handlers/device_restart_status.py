import sys
sys.path.append('/home/pi/smartpump/services/fcc')
import services

def set_restart():
    services.set_restart_flag()

if __name__ == "__main__":
    set_restart()