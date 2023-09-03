
import pika
import sys
sys.path.append('/home/pi/smarteye/helpers')
import helper
import json
import datetime
import time

def send_heartbeat_message_to_remote_server():
    try:
        #credentials = pika.PlainCredentials('prod_user', 'prod_password')
        mq_url = "amqps://prod_user:prod_password@b-f44d9c58-da38-4253-86f8-60f12212dad8.mq.eu-west-1.amazonaws.com:5671"
        #parameters = pika.ConnectionParameters('34.240.137.86', 5672, '/', credentials)
        connection = pika.BlockingConnection(pika.URLParameters(mq_url))

        channel = connection.channel()

        channel.exchange_declare(exchange='heartbeat_logs', exchange_type='topic')
        ip_address = helper.get_device_ip_address()
        MAC = helper.get_device_mac_address()
        routing_key = 'heartbeat.'+MAC
        last_time_online = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        message = json.dumps({'last_time_online': last_time_online, 'local_ip': ip_address, 'device_mac_address': MAC })
        channel.basic_publish(exchange='heartbeat_logs',
                            routing_key=routing_key,
                            body=message)
        #i am not using delivery_mode because we dont need to persist heartbeat
        print(" [x] Sent %r:%r" % (routing_key, message))
        connection.close()
        print("heartbeat message sent to db")
    except:
        print("heartbeat message not sent")


def main():
    while True:
        send_heartbeat_message_to_remote_server()
        time.sleep(3)

if __name__ == '__main__':
    main()
