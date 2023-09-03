import time
import sys
import json
sys.path.append('/home/pi/smartpump/crons')
sys.path.append('/home/pi/smartpump/services/fcc')
import jobs
import services
import remote_api_service
import datetime

def reformat_smart_pump_config(full_config):
    smartpump_config=[]
    for nozzle_config in full_config:
        temp={}
        temp['nozzle_address']=nozzle_config['Nozzle_address']
        temp['site_name']=nozzle_config['Pump']['Site']['Name']
        temp['site_id']=nozzle_config['Pump']['Site']['Site_id']
        temp['protocol']=nozzle_config['Pump']['Pump_protocol']
        temp['device_id']=nozzle_config['Pump']['Device']['Device_id']
        temp['price']=nozzle_config['First_initial_price']
        temp['decimal_volume']=nozzle_config['Decimal_setting_volume']
        temp['decimal_price']=nozzle_config['Decimal_setting_price_unit']
        temp['decimal_amount']=nozzle_config['Decimal_setting_amount']
        
        #temp['Decimal_setting_volume']=nozzle_config['Pumpbrand']['nozzles']['Decimal_setting_volume']
        
        print("The reformatted config is ",temp)
        smartpump_config.append(temp)
    return smartpump_config
        
def update_device_with_remote_config():
    #1. Get remote config
    try:
        config_dict = remote_api_service.get_device_config()
        print(config_dict)
        #remote_api_service.test_func()
        smart_pump_config =remote_api_service.get_smartpump_device_config()
        print("This is smartpump",smart_pump_config)
        print("ends here")
    except Exception as e:
        print(e)
        print('error connecting to api')
        return
    #2. Get current local config
    local_tank_config = json.loads(services.get_device_config_by_slug('TANK_DETAILS')[0])
    local_device_config = json.loads(services.get_device_config_by_slug('DEVICE_DETAILS')[0])
    local_pump_config = json.loads(services.get_device_config_by_slug('PUMP_DETAILS')[0])
    #3. Update the local config if it differs from the remote config
    if smart_pump_config:
        #tank_config = config_dict['tank_details']
        #device_config = config_dict['device_details']
        pump_config= reformat_smart_pump_config(smart_pump_config)
        print("The pump configuration to the db is ",pump_config)
        #print(tank_config)
      
        '''    
        if device_config != local_device_config:
            print('New device configurations')
            print('local: {}\n'.format(local_device_config))
            print('remote: {}\n'.format(device_config))
            services.new_update_device_config('DEVICE_DETAILS', json.dumps(device_config))
        '''
        
        if pump_config != local_pump_config:
            print('New pump configurations')
            print('local: {}\n'.format(local_pump_config))
            print('remote: {}\n'.format(pump_config))
            services.new_update_device_config('PUMP_DETAILS', json.dumps(pump_config))
            print("i am here")
            
        if pump_config==local_pump_config:
            print("Pump configurationis already updated")
        
            
           # if device_config['transmit_interval'] > 0 and device_config['transmit_interval'] != local_device_config['transmit_interval']:
           #     jobs.install_new_jobs()
        
    #4. 
def main():
    update_device_with_remote_config()

if __name__ == '__main__':
    main()
