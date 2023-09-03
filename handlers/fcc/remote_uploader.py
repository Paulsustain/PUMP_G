import datetime
import os
# Make it work for Python 2+3 and with Unicode
import io
import sqlite3
import sys
#sys.path.append('/home/pi/smarteye/helpers')
import helpers
import services
import db_handler

#db_path = 'store.db'

def upload_local_transaction_logs():
    txn=services.get_unuploaded_transactions()
    if not txn: return None
    print(txn)
    #ids=[tuple(list(data[0])) for data in txn]
    ids = []
    for value in txn:
        id = []
        id.append(value[0])
        ids.append(tuple(id))
    print(txn)
    print(ids)
    trimmed=[tx[1:-1] for tx in txn]
    result=db_handler.insert_transaction_details(trimmed)
    if result:
        services.update_uploaded_transactions(ids)
        return True
    else:
        return False
     


def upload_local_totalizer_logs():
    ttlz=services.get_unuploaded_totalizers()
    if not ttlz: return None
    ids = []
    for value in ttlz:
        id = []
        id.append(value[0])
        ids.append(tuple(id))
    print(ttlz)
    print(ids)
    trimmed=[tz[1:-1] for tz in ttlz]
    result=db_handler.insert_totalizer(trimmed)
    print(result)
    if result:
        services.update_uploaded_totalizers(ids)
        return True
    else:
        return False


if __name__=="__main__":
    upload_local_transaction_logs()
#upload_local_totalizer_logs()