job = my_cron.new(command='python3 /home/pi/smartpump/handlers/sm_trigger_high.py', comment = 'sim_hard_reboot')
job.every_reboot()
    
job = my_cron.new(command='python3 /home/pi/smartpump/handlers/sm_trigger_high.py', comment = 'sim_hard_reboot')
job.every_reboot()