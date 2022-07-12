import json
import os
import boto3
from botocore.config import Config
from botocore.exceptions import ClientError
# import redshift_connector
import psycopg2
from math import ceil
import ast
import base64

# conn = redshift_connector.connect(
#      host='redshift-cluster-3.c8ww2g0fe5tg.us-east-1.redshift.amazonaws.com:5439',
#      database='dev',
#      user='muellerdelta',
#      password='Muellerdelta0'
#   )

conn = psycopg2.connect(user = 'muellerdelta',
                        password = 'Muellerdelta0',
                        host = 'redshift-cluster-3.c8ww2g0fe5tg.us-east-1.redshift.amazonaws.com',
                        dbname = 'dev',
                        port = 5439)


def flatten_json(event):
    """"modified funct to flatten data reading from kinesis stream to a list of tuples"""
    records = []
    for readings in event['rs']:
        record = (event['did'], str(int(readings['t']) * 1000), readings['r'])
        records.append(record)
    return records


def write_to_redshift(records):
    """create a table & ingest records
    """
    cursor = conn.cursor()

    try:
        cursor.execute("CREATE TABLE IF NOT EXISTS mwp_consumption(deviceid bigint, time varchar, reading double precision);")
        conn.commit()
    except Exception as err:
        raise f'fail to create table: {err}'

    try:
        cursor.executemany("insert into mwp_consumption (deviceid, time, reading) values (%s, %s, %s)", records)
        conn.commit()
    except Exception as err:
        raise f'fail to ingest data to table: {err}'


def lambda_handler(event, context):

    # print(type(event))
    print(event)
    print(len(event['Records']))

    records_list =[]
    for i in range(len(event['Records'])):
        data_encoded = event['Records'][i]['kinesis']['data']
        data_decoded = ast.literal_eval(base64.b64decode(data_encoded).decode("utf-8"))
        print(data_decoded)
        records = flatten_json(data_decoded)
        # records_list.append(records)
        records_list += records

    print('length of records_list: ', len(records_list))
    #This is for the begining part of the list slice in the for loop
    b=0

    for n in range(1,ceil(len(records_list)/100)+1):
        print(b,'-',n*100)
        print(type(records_list[b:n*100]))
        write_to_timestream(records_list[b:n*100])
        b = n*100


    return {
        'statusCode': 'OK'
    }
