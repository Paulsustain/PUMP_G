import psycopg2
import sys
from datetime import datetime
sys.path.append('/home/pi/smartpump/helpers')
import helper
database='d74eoknfvrkdgt'
user='yxfjskqgtrfwyh'
password='231b11470bab8a3e385a3af3fe7a1fbeb1eec58a307ecdd1162df866070ea3d5'
port='5432'
host='ec2-44-194-225-27.compute-1.amazonaws.com'

def connect_db():
    con=None
    cur=None
    try: 
        con = psycopg2.connect(database=database,user=user,password=password,host=host,port=port)
        if con:
            print(con,'database connection successful')
            cur=con.cursor()
    except Exception as e:
        print(e)    
    return (con,cur)
        
def migration():
    con,cur=connect_db()
    sql_query="""
                alter table totalizers rename column totalizer to totalizer_money;
                alter table 
                """
    cur.execute(sql_query)
    
    con.commit()
    con.close()


def insert_transaction_details_trimmed(logs):
    print('*********transaction logs is: {}******** before insert'.format(logs))
    try:
        con,cur=connect_db()
        for log in logs:
            device_address,pump_id,start_time,end_time,liters,unit_price,amount,read_at=log
            sql_query="""
                        insert into transactions(device_address,pump_id,start_time,end_time,liters,unit_price,amount,read_at) values (%s,%s,%s,%s,%s,%s,%s,%s)
                        """
            cur.execute(sql_query,(device_address,pump_id,start_time,end_time,liters,unit_price,amount,read_at))
            
        con.commit()
        con.close()
        print('data inserted successfully')
        return True
    except Exception as e:
        print(e)
        return False

def insert_transaction_details(logs):
    print('*********transaction logs is: {}******** before insert'.format(logs))
    try:
        con,cur=connect_db()
        for log in logs:
            device_address,pump_id,start_totalizer,end_totalizer,start_totalizer_money,end_totalizer_money,start_time,end_time,liters,unit_price,amount,read_at=log
            sql_query="""
                        insert into transactions(device_address,pump_id,start_totalizer,end_totalizer,start_totalizer_money,end_totalizer_money,start_time,end_time,liters,unit_price,amount,read_at) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                        """
            cur.execute(sql_query,(device_address,pump_id,start_totalizer,end_totalizer,start_totalizer_money,end_totalizer_money,start_time,end_time,liters,unit_price,amount,read_at))
            
        con.commit()
        con.close()
        print('data inserted successfully')
        return True
    except Exception as e:
        print(e)
        return False
        
def insert_totalizer(logs):
    try:
        con,cur=connect_db()
        for log in logs:
            device_address,pump_id,totalizer_money,totalizer_volume,read_at=log
            sql_query="""
                        insert into totalizers(device_address,pump_id,totalizer_money,totalizer_volume,read_at) values (%s,%s,%s,%s,%s)
                        """
            cur.execute(sql_query,(device_address,pump_id,totalizer_money,totalizer_volume,read_at))
        
        con.commit()
        con.close()
        print('data inserted successfully')
        return True
    except Exception as e:
        print(e)
        return False
    
def get_remote_price(device_address):
    #device_address='b8:27:eb:62:ec:1b'
    print('got into dbhandler remote price')
    print('*********device address is: {}*******'.format(device_address))
    try:
        #select price from prices where device_address = '{}' and pump_id= {} order by set_at desc limit 1
        price_details=None
        con,cur=connect_db()
        print(con,cur)
        sql_query="""

                    select * from prices where device_address = '{}' and sent= 0 order by set_at desc
                    
                    """.format(device_address)
        print(sql_query)
        cur.execute(sql_query)
        result=cur.fetchall()
        print(result)
        if result:
            price_details=result
        con.close()
        print('price_detalis returned is: {}'.format(price_details))
        return price_details
    except Exception as e:
        print(e)
        return None
    
def confirm_remote_prices(ids):
    print('*********the ids are: {}********'.format(ids))
    print(type(ids))
    id_list=[]
    for _id in ids:
        id=[]
        print('********')
        id.append(_id)
        print('********'*2)
        id_list.append(tuple(id))
        print(id_list)
        print('********'*3)
    print('id_list is: {}'.format(id_list))
    try:
        con,cur=connect_db()
        sql_query="""
                    update prices set sent = 1 where id = %s;
        
        """
        #print(price)
        cur.executemany(sql_query,id_list)
        con.commit()
        con.close()
        print('data updated successfully')
        return True
    except Exception as e:
        print(e)
        return False
    
def set_remote_price(device_address,pump_id,price,set_by,set_at):
    print('*********price is: {}******** before insert'.format(price))
    try:
        con,cur=connect_db()
        sql_query="""
                    insert into prices(device_address,pump_id,price,set_by,set_at) values (%s,%s,%s,%s,%s);
        
        """
        print(price)
        cur.execute(sql_query,(device_address,pump_id,price,set_by,set_at))
        con.commit()
        con.close()
        print('data inserted successfully')
        return price
    except Exception as e:
        print(e)
        return None
    
def upload_online_status(statuses):
    device_address=helper.get_device_mac_address()
    try:
        con,cur=connect_db()
        sql_query="""
                    update pump_status set statuses='{}' where device_address='{}';
        
        """.format(statuses,device_address)
        print(sql_query)
        cur.execute(sql_query)
        con.commit()
        con.close()
        print('data inserted successfully')
        return True
    except Exception as e:
        print(e)
        return None