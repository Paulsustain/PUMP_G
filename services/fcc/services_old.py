import datetime
import os
# Make it work for Python 2+3 and with Unicode
import io
import sqlite3
import sys
sys.path.append('/home/pi/smartpump/helpers')
sys.path.append('/home/pi/smartpump/handlers/fcc')
sys.path.append('/home/pi/smartpump/data/fcc')
import price_change_handler
import helper
import gvr_frontier
import main_logger
import json
from datetime import datetime
my_logger=main_logger.get_logger(__name__)

db_path = '/home/pi/smartpump/db/fcc/store.db'

def connect_db():
    con=None
    cur=None
    try: 
        con = sqlite3.connect(db_path)
        if con:
            print(con,'database connection successful')
            my_logger.debug(con)
            my_logger.debug('database connection successful')
            cur=con.cursor()
    except Exception as e:
        print(e)    
    return (con,cur)

def insert_transaction_details(device_address,nozzle_address,start_totalizer,end_totalizer,start_totalizer_money,end_totalizer_money,start_time,end_time,liters,unit_price,amount,read_at):
    print('*********start totalizers is: {}******** before insert'.format(start_totalizer))
    try:
        con,cur=connect_db()
        sql_query="""
                    insert into transaction_details(device_address,nozzle_address,start_totalizer,end_totalizer,start_totalizer_money,end_totalizer_money,start_time,end_time,liters,unit_price,amount,read_at) values (?,?,?,?,?,?,?,?,?,?,?,?)
                    """
        cur.execute(sql_query,(device_address,nozzle_address,start_totalizer,end_totalizer,start_totalizer_money,end_totalizer_money,start_time,end_time,liters,unit_price,amount,read_at))
        
        con.commit()
        con.close()
        print('data inserted successfully')
    except Exception as e:
        print(e)

def get_local_price(nozzle_address):
    print('*********nozzle_address is: {}********'.format(nozzle_address))
    try:
        price_details=None
        con,cur=connect_db()
        sql_query="""
                    select * from prices where nozzle_address = {} and in_use=1 order by set_at desc limit 1;
                    """.format(nozzle_address)
        cur.execute(sql_query)
        result=cur.fetchall()
        if result:
            price_details=result[0]
        con.close()
        print('local price_details returned is: {}'.format(price_details))
        return price_details
    except Exception as e:
        print(e)
        return None

def clear_restart_flag():
    #print('*********nozzle_address is: {}********'.format(nozzle_address))
    from datetime import datetime
    time=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    try:
        con,cur=connect_db()
        sql_query="""
                    update * restart_flag set status = 0 and updated_at = {};
                    """.format(time)
        cur.execute(sql_query)
        con.commit()
        con.close()
        my_logger.debug('restart flag cleared')
        return True
    except Exception as e:
        print(e)
        my_logger.exception(e)
        return False

def set_restart_flag():
    #print('*********nozzle_address is: {}********'.format(nozzle_address))
    from datetime import datetime
    time=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    try:
        con,cur=connect_db()
        sql_query="""
                    update * restart_flag set status = 1 and updated_at = {};
                    """.format(time)
        cur.execute(sql_query)
        con.commit()
        con.close()
        my_logger.debug('restart flag set')
        return True
    except Exception as e:
        print(e)
        my_logger.exception(e)
        return False

def get_restart_flag():
    #print('*********nozzle_address is: {}********'.format(nozzle_address))
    try:
        con,cur=connect_db()
        sql_query="""
                    select restart from restart_flag;
                    """
        cur.execute(sql_query)
        result=cur.fetchall()
        if result:
            restart_flag=result[0][0]
        con.close()
        print('restart_flag is: returned is: {}'.format(restart_flag))
        return restart_flag
    except Exception as e:
        print(e)
        return False

def update_status(address,status):
    pass
    

def get_previous_status():
    try:
        con,cur=connect_db()
        sql_query="""
                    select nozzle_address,pump_status from pump_status;
                    """
        cur.execute(sql_query)
        result=cur.fetchall()
        if result:
            status=result
        con.close()
        print('statuses returned are : {}'.format(result))
        return status
    except Exception as e:
        print(e)
        return False

def get_last_status_update_time():
    pumps= json.loads(get_device_config_by_slug('PUMP_DETAILS')[0])
    time_list=[]
    for pump in pumps:
        last_time=get_last_updated_time(pump['nozzle_address'])
        time_list.append([pump['nozzle_address'],last_time])
    
    return time_list
        
def set_current_status(status,address):
    try:
        if status:
            con,cur=connect_db()
            print('status is: {} and address is: {}'.format(status,address))
            current_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            sql_query="""
                        update pump_status set pump_status = {}, updated_at = '{}' where pump_id = {};
                        """.format(status,current_time,address)
            cur.execute(sql_query)
            con.commit()
            con.close()
        #print('statuses returned are : {}'.format(status))
        return True
    except Exception as e:
        print(e)
        return False

def set_transaction_start(device_address,pump_address,start_time,site_id,device_id):
    try:
        con,cur=connect_db()
        sql_query="""
                    insert into transaction_details (device_address,nozzle_address,start_time,site_id,device_id) values (?,?,?,?,?);
                    """
        cur.execute(sql_query,(device_address,pump_address,start_time,site_id,device_id))
        con.commit()
        con.close()
        return True
    except Exception as e:
        print(e)
        return False
 

##def set_start_transaction_details(device_address,pump_address,total_volume,read_at,site_id,device_id)*:
##    try:
##        con,cur=connect_db()
##        sql_query="""
##                    insert into transaction_details (device_address,nozzle_address,start_totalizer,start_time,site_id,device_id) values (?,?,?,?,?,?);
##                    """
##        cur.execute(sql_query,(device_address,pump_address,total_volume,read_at,site_id,device_id))
##        con.commit()
##        con.close()
##        return True
##    except Exception as e:
##        print(e)
##        return False
##    
def clear_transaction_unauthorized(pump_address):
    try:
        con,cur=connect_db()
        sql_query="""
                    select MAX(id) from transaction_details where nozzle_address = ?;
        
        """
        cur.execute(sql_query,pump_address)
        max_id=cur.fetchall()[0][0]
        print('max id is: {}'.format(max_id))
        if max_id:
                
            sql_query="""
                        delete * from transaction_details where nozzle_address ={};
                        """.format(pump_address)
            cur.execute(sql_query)
        con.commit()
        con.close()
        my_logger.debug('unauthorized transaction deleted')
        return True
    except Exception as e:
        print(e)
        return False

def set_transaction_details(device_address,nozzle_address,liters,amount,ppu,read_at):
    try:
        con,cur=connect_db()
        sql_query="""
                    insert into transaction_details (device_address,nozzle_address,liters,amount,unit_price,read_at) values (?,?,?,?,?,?)
                    """
        cur.execute(sql_query,(device_address,nozzle_address,liters,amount,ppu,read_at))
        con.commit()
        con.close()
        my_logger.debug('transaction end details inserted successfully')
        return True
    except Exception as e:
        print(e)
        my_logger.exception(e)
        return False

def set_end_transaction_details(nozzle_address,total_volume,total_money,liters,amount,ppu,read_at):
    try:
        con,cur=connect_db()
        sql_query="""
                    select MAX(id) from transaction_details where nozzle_address = {};
        
        """.format(nozzle_address)
        cur.execute(sql_query)
        max_id=cur.fetchall()[0][0]
        print('max id is: {}'.format(max_id))
        if max_id:
                
            sql_query="""
                        update transaction_details set end_totalizer={},end_totalizer_money={},end_time='{}',liters={},unit_price={},amount={},read_at='{}' where id= {};
                        """.format(total_volume,total_money,read_at,liters,ppu,amount,read_at,max_id)
            print(sql_query)
            cur.execute(sql_query)
        con.commit()
        con.close()
        my_logger.debug('transaction end details inserted successfully')
        return True
    except Exception as e:
        print(e)
        my_logger.exception(e)
        return False
    
def set_start_transaction_details(device_address,pump_address,total_volume,total_money,read_at,site_id,device_id):
    try:
        con,cur=connect_db()
        sql_query="""
                    insert into transaction_details (device_address,nozzle_address,start_totalizer,start_totalizer_money,start_time,site_id,device_id) values (?,?,?,?,?,?,?)
                    """
        cur.execute(sql_query,(device_address,pump_address,total_volume,total_money,read_at,site_id,device_id))
        con.commit()
        con.close()
        my_logger.debug('transaction start details inserted successfully')
        return True
    except Exception as e:
        print(e)
        my_logger.exception(e)
        return False


def set_transaction_end(nozzle_address,liters,amount,ppu,read_at):
    try:
        con,cur=connect_db()
        sql_query="""
                    select MAX(id) from transaction_details where nozzle_address = {};
        
        """.format(nozzle_address)
        cur.execute(sql_query)
        max_id=cur.fetchall()[0][0]
        print('max id is: {}'.format(max_id))
        if max_id:
                
            sql_query="""
                        update transaction_details set end_time='{}',liters={},unit_price={},amount={},read_at='{}' where id= {};
                        """.format(read_at,liters,ppu,amount,read_at,max_id)
            print(sql_query)
            cur.execute(sql_query)
        con.commit()
        con.close()
        my_logger.debug('transaction end details inserted successfully')
        return True
    except Exception as e:
        print(e)
        my_logger.exception(e)
        return False

def insert_totalizer(device_address,nozzle_address,totalizer_money,totalizer_volume,read_at):
    try:
        con,cur=connect_db()
        sql_query="""
                    insert into totalizers(device_address,nozzle_address,totalizer_money,totalizer_volume,read_at) values (?,?,?,?,?)
                    """
        cur.execute(sql_query,(device_address,nozzle_address,totalizer_money,totalizer_volume,read_at))
        
        con.commit()
        con.close()
        print('data inserted successfully')
    except Exception as e:
        print(e)

def get_last_updated_time(address):
    #print('*********price is: {}******** before insert'.format(price))
    try:
        con,cur=connect_db()
        sql_query="""
                    select updated_at from pump_status where pump_id = {};
        
        """.format(address)
        cur.execute(sql_query)
        updated_time=cur.fetchall()[0][0]
        print('*****', updated_time)
        print('data updated successfully')
        con.close()
        return updated_time
    except Exception as e:
        print(e)
        my_logger.exception(e)
        return None

def effect_price_change(address,status):
    #print('*********price is: {}******** before insert'.format(price))
    try:
        con,cur=connect_db()
        sql_query="""
                    select id,price from prices where nozzle_address = {} and in_use = 1 order by id asc;
        
        """.format(address)
        cur.execute(sql_query)
        id_price=cur.fetchall()
        print('*****', id_price)
        ids=[idx[0] for idx in id_price]
        prices=[pricex[1] for pricex in id_price]
        print('ids are: {}'.format(ids))
        if len(ids) > 1:
            print(prices[-1],address,1,status)
            result1=gvr_frontier.set_device_price(prices[-1],address,1,status)
            #result2=gvr_frontier.set_device_price(prices[-1],address,2,status)
            #if result1 and result2:
            if result1:
                ids=ids[:-1]
                print(ids)
                for id in ids:
                    sql_query="""
                                update prices set in_use = 0 where id = {};
                    
                    """.format(id)
                    print(sql_query)
                    cur.execute(sql_query)
            con.commit()
            my_logger.debug('price change effected succesfully for nozzle: {}'.format(address))
            print('data updated successfully')
        con.close()

        return True
    except Exception as e:
        print(e)
        my_logger.exception(e)
        return None


def set_price(device_address,nozzle_address,price,set_by,set_at):
    print('*********price is: {}******** before insert'.format(price))
    try:
        con,cur=connect_db()
        sql_query="""
                    insert into prices(device_address,nozzle_address,price,set_by,set_at) values (?,?,?,?,?);
        
        """
        print(price)
        cur.execute(sql_query,(device_address,nozzle_address,price,set_by,set_at))
        con.commit()
        print('data inserted successfully')
        con.close()
        my_logger.debug('new price inserted successfully {}'.format(device_address,nozzle_address,price,set_by,set_at))
        return True
    except Exception as e:
        print(e)
        my_logger.exception(e)
        return False
    
def set_scheduled_price(device_address,address,price,user,current_time,time_scheduled):
    print('*********price is: {}******** before insert'.format(price))
    try:
        con,cur=connect_db()
        sql_query="""
                    insert into scheduled_prices(device_address,nozzle_address,price,set_by,set_at,time_schedule) values (?,?,?,?,?,?);
        
        """
        print(price)
        cur.execute(sql_query,(device_address,address,price,user,current_time,time_scheduled))
        con.commit()
        print('data inserted successfully')
        con.close()
        my_logger.debug('new scheduled price inserted successfully {}'.format((device_address,address,price,user,current_time,time_scheduled)))
        return True
    except Exception as e:
        print(e)
        my_logger.exception(e)
        return False
    
def confirm_scheduled_price(ids):
    print('*********IDs recevied are : {}******** before update'.format(ids))
    try:
        con,cur=connect_db()
        sql_query="""
                    update scheduled_prices set used = 1 where id = ?;
        
        """
        print(sql_query)
        cur.executemany(sql_query,ids)
        con.commit()
        con.close()
        print('data updated successfully')
        return True
    except Exception as e:
        print(e)
        return None
            

def update_scheduled_price(device_address,address,price,user,current_time,time_scheduled):
    print('*********price is: {}******** before insert'.format(price))
    try:
        con,cur=connect_db()
        sql_query="""
                    insert into prices(device_address,nozzle_address,price,set_by,set_at,time_scheduled) values (?,?,?,?,?,?);
        
        """
        print(price)
        cur.execute(sql_query,(device_address,nozzle_address,price,set_by,set_at,time_scheduled))
        con.commit()
        print('data inserted successfully')
        my_logger.debug('scheduled price moved to instant price {}'.format((device_address,nozzle_address,price,set_by,set_at,time_scheduled)))
        con.close() 
        return True
    except Exception as e:
        print(e)
        my_logger.exception(e)
        return False
    
def get_due_unused_scheduled_price():
    current_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    #print('*********price is: {}******** before insert'.format(price))
    try:
        con,cur=connect_db()
        sql_query="""
                    select * from scheduled_prices where used = 0 and time_schedule <= '{}' order by set_at asc limit 1
        
        """.format(current_time)
        print(sql_query)
        cur.execute(sql_query)
        result=cur.fetchall()
        print('result is: {}'.format(result))
        con.close()
        my_logger.debug('due scheduled price exist: {}'.format(result))
        return result
    except Exception as e:
        print(e)
        my_logger.exception(e)
        return False
    
def get_unuploaded_totalizers():
    #print('*********price is: {}******** before insert'.format(price))
    totalizers=None
    try:
        con,cur=connect_db()
        sql_query="""
                    select * from totalizers where uploaded = 0;
        
        """
        #print(price)
        cur.execute(sql_query)
        result = cur.fetchall()
        #con.commit()
        if result:
            totalizers=result
            print('data collected successfully')
        else:
            print('no data to upload')
        con.close()
        #print('data collected successfully')
        return totalizers
    except Exception as e:
        print(e)
        return None
    
def reformat_unuploaded_transactions(logs):
    reformated_data=[]
    for log in logs:
        reformed_data={}
        reformated_data.appendd
    
def get_unuploaded_transactions():
    #print('*********price is: {}******** before insert'.format(price))
    transactions=None
    try:
        con,cur=connect_db()
        sql_query="""
                    select * from transaction_details where uploaded = 0 and end_time is not null;
        
        """
        #print(price)
        cur.execute(sql_query)
        result = cur.fetchall()
        #con.commit()
        if result:
            transactions=result
            print('data collected successfully')
            my_logger.debug('unuploaded transactions exists and are: {}'.format(result))
        else:
            print('no data to upload')
            my_logger.debug('no data to upload')
        con.close()
        #print('data collected successfully')
        return transactions
    except Exception as e:
        print(e)
        my_logger.exception(e)
        return None
    
def update_uploaded_transactions(ids):
    print('*********IDs recevied are : {}******** before update'.format(ids))
    try:
        con,cur=connect_db()
        sql_query="""
                    update transaction_details set uploaded = 1 where id = ?;
        
        """
        print(sql_query)
        cur.executemany(sql_query,ids)
        con.commit()
        con.close()
        print('data updated successfully')
        my_logger.debug('uploaded data updated successfully')
        return True
    except Exception as e:
        print(e)
        my_logger.exception(e)
        return None

def get_device_config_by_slug(slug):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    query = "SELECT value FROM device_config where slug = ?"
    cur.execute(query, (slug,))
    return cur.fetchone()

def count_transaction_since_last_totalizer(nozzle_address):
#print('*********price is: {}******** before insert'.format(price))
    try:
        con,cur=connect_db()
        sql_query="""
                    select last_checked_id from totalizer_check where nozzle_address = {} ;
        
        """.format(nozzle_address)
        cur.execute(sql_query)
        last_id=cur.fetchall()[0][0]
        print('*****', last_id)
        
        sql_query="""
                    select count(id) from transaction_details where nozzle_address = {} and id > {} ;
        
        """.format(nozzle_address,last_id)
        cur.execute(sql_query)
        number_of_transaction=cur.fetchall()[0][0]
        print('the number of transaction for nozzle: {} with last id {} is: {}'.format(nozzle_address,last_id,number_of_transaction))
        con.close()
        return number_of_transaction
    except Exception as e:
        print(e)
        my_logger.exception(e)
        return None
    
def update_totalizer_checker(nozzle_address):
    time=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print('time is: {}'.format(time))
    try:
        con,cur=connect_db()
        sql_query="""
                    update totalizer_check set last_checked_time = '{}' where nozzle_address = {};
        
        """.format(time,nozzle_address)
        print(sql_query)
        cur.execute(sql_query)
        con.commit()
        con.close()
        print('*****totalizer checker updated successfully*****')
        my_logger.debug('totalizer checker data updated successfully')
        return True
    except Exception as e:
        print(e)
        my_logger.exception(e)
        return None
   
    
def get_time_since_last_totalizer(nozzle_address):
#print('*********price is: {}******** before insert'.format(price))
    try:
        con,cur=connect_db()
        sql_query="""
                    select last_checked_time from totalizer_check where nozzle_address = {} ;
        
        """.format(nozzle_address)
        cur.execute(sql_query)
        last_time=cur.fetchall()[0][0]
        print('the last time totalizer was read for nozzle: {} is: {}'.format(nozzle_address,last_time))
        con.close()
        return last_time
    except Exception as e:
        print(e)
        my_logger.exception(e)
        return None

def new_update_device_config(slug,data):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("UPDATE device_config SET value = ? WHERE slug = ?", (data, slug))
    conn.commit()
    conn.close()

def update_uploaded_totalizers(ids):
    print('*********IDs recevied are : {}******** before update'.format(ids))
    try:
        con,cur=connect_db()
        sql_query="""
                    update totalizers set uploaded = 1 where id = ?;
        
        """
        print(sql_query)
        cur.executemany(sql_query,ids)
        con.commit()
        con.close()
        print('data updated successfully')
        return True
    except Exception as e:
        print(e)
        return None
    
if __name__=="__main__":
    #set_start_transaction_details('b8:27:eb:11:ef:cc',1,198759.5,'2021-07-07 20:42:53')
    #effect_price_change(1)
    #count_transaction_since_last_totalizer(1)
    #get_time_since_last_totalizer(1)
    #get_due_unused_scheduled_price()
    #get_last_updated_time(1)
    pass
    
