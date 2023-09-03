import os
import subprocess

from crontab import CronTab

CWD = os.path.dirname(os.path.realpath(__file__))


def main():
    run_general_jobs()
    run_jobs()
    setup_daemon('i2c_rtc.service')
    
def run_general_jobs():
    my_cron = CronTab(user='pi')

    my_cron.remove_all()
    my_cron.write()
    
    
    
    #rewrite static jobs
    job = my_cron.new(command='python3 /home/pi/smarteye/helpers/sim_reboot.py', comment = 'sim_reboot')
    job.every_reboot()
    #sim module will reboot
    
    job = my_cron.new(command='python3 /home/pi/firmware_download_manager.py', comment = 'download_manager')
    job.every_reboot()
    #
    job = my_cron.new(command='python3 /home/pi/smarteye/helpers/sim_reboot.py', comment = 'sim_reboot')
    job.minute.every(30)
    #sim module will reboot

    job = my_cron.new(command='python3 /home/pi/smarteye/helpers/pi_restart.py' , comment = 'pi_restart')
    #job.hours.every(12)
    job.every(6).hours()
    
    job = my_cron.new(command='python3  /home/pi/smarteye/handlers/heartbeat_handler.py', comment = 'heartbeat_handler')
    job.minute.every(1)
    
    job = my_cron.new(command='python3 /home/pi/firmware_download_manager.py' , comment = 'download_manager')
    job.minute.every(24)
    
    job = my_cron.new(command='python3 /home/pi/smarteye/handlers/anydesk_config.py', comment = 'anydesk_config')
    job.every_reboot()
    
    job = my_cron.new(command='python3  /home/pi/smarteye/handlers/rtc_update_handler.py', comment = 'rtc_update_handler')
    job.minute.every(5)
    
    #job = my_cron.new(command='python3  /home/pi/smarteye/helpers/rtc_startup_setter.py', comment = 'rtc_startup_setter')
    #job.minute.every(1)
    

    my_cron.write()
    for job in my_cron:
        print(job)        
        
def run_jobs():
    #get current dir
    print(CWD)
    #return a list of dirs in the dir
    dirs = [dir for dir in os.listdir(CWD) if os.path.isdir(dir)]
    # for each dir, run the jobs.py file
    for dir in dirs:
        job_path = CWD + "/" + dir + "/jobs.py"
        if os.path.exists(job_path):
            process = subprocess.run(['/usr/bin/python3', job_path], stdout=subprocess.PIPE, universal_newlines=True)
            print("inside "+job_path)
            print(process.stdout)
            
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

        
if __name__ == "__main__":
    main()
    run_general_jobs()