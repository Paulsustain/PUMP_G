from crontab import CronTab
import sys
import json
import os
import subprocess
sys.path.append('/home/pi/smarteye/services/atg')
import sqlite_service
CWD = os.path.dirname(os.path.realpath(__file__))

def install_new_jobs():
    my_cron = CronTab(user='pi')

    #my_cron.remove_all()
    my_cron.write()
    
    job = my_cron.new(command='python3  /home/pi/smartpump/handlers/sm_trigger.py', comment = 'sim_reboot_db')
    job.minute.every(4)
    
    job = my_cron.new(command='python3 /home/pi/smartpump/handlers/sm_trigger_high.py', comment = 'sim_hard_reboot')
    job.every_reboot()
    
    #job = my_cron.new(command='python3 /home/pi/smartpump/handlers/sm_trigger_high.py', comment = 'sim_hard_reboot')
    #job.every_reboot()
    #job = my_cron.new(command='python3 /home/pi/smartpump/handlers/db_management.py', comment = 'local_DB_management_run')
    #job.every_reboot()


    
    job = my_cron.new(command='python3  /home/pi/smartpump/handlers/fcc/price_change_handler.py', comment = 'price_change_handler')
    job.minute.every(2)

    job = my_cron.new(command='python3  /home/pi/smartpump/handlers/fcc/remote_logger_handler.py', comment = 'remote_transaction_handler')
    job.minute.every(2)
    
##    job = my_cron.new(command='python3  /home/pi/smartpump/handlers/fcc/remote_config_updater_handler.py', comment = 'remote_config_updater_handler')
##    job.minute.every(1)

    job = my_cron.new(command='python3 /home/pi/smartpump/handlers/fcc/restart_flag_handler.py', comment = 'restart_flag_setter')
    job.every_reboot()

    #get new transmit interval and reset jobs
    interval= json.loads(sqlite_service.get_device_config_by_slug('DEVICE_DETAILS')[0])['transmit_interval']
    
    local_transmit_interval = interval//60
    if local_transmit_interval < 1:
        local_transmit_interval = 1
    
    my_cron.write()

    for job in my_cron:
        print(job)
        
def setup_udev_rule(filename):
    faker=filename
    dir='/home/pi/smartpump/crons/fcc/'
    file_dir = '/etc/udev/rules.d/'
    if not os.path.exists(file_dir+filename):
        try:    
            print('got to sudo cp')
            subprocess.run(["sudo","cp",dir+filename,file_dir])
            subprocess.run(["sudo","udevadm","trigger"])
            
            #shutil(dir+filename,file_dir)
        except:
            print('unable to create atg udev rule')
    else:
        print("fcc udev has already been registered")
        
def setup_daemon(filename):
    dir = '/etc/systemd/system/'
    if not os.path.exists(dir+filename):
        filepath = CWD+ '/' + filename
        if os.path.exists(filepath):
            os.system("sudo cp {} {}".format(filepath, dir))
            os.system("sudo systemctl daemon-reload")
            os.system("sudo systemctl start {}".format(filename))
            os.system("sudo systemctl enable {}".format(filename))
        else:
            print("Filename doesn't exist in this directory")
    else:
        print("Service has already been registered")
        
def main():
    install_new_jobs()
    setup_udev_rule('fcc_custom_udev.rules')
    setup_daemon('fcc_service.service')
if __name__ == '__main__':
    main()
    install_new_jobs()
