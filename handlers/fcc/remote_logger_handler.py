import sys
sys.path.append('/home/pi/smartpump/services/fcc')
import remote_api_service

def log_data_to_remote_api():
    try:
        #remote_api_service.upload_local_transaction_logs()
        remote_api_service.upload_transaction_log()
        remote_api_service.upload_online_status()
    except:
        print("could not log inventory to remote db")

def main():
    log_data_to_remote_api()

if __name__ == '__main__':
    main()
