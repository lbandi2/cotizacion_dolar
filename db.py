from mysql.connector import connect, Error
import os
from utils import date_to_string
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB = os.getenv('DB')
DB_TABLE = "dolar_cotizacion"
MAX_AMOUNT = 50

# TODO: Add check for db and table existence

def fetch(query, phrase=''):
    try:
        with connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB,
        ) as connection:
            with connection.cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchall()
                return result
    except Error as e:
        print(e)
    finally:
        if phrase != '':
            print(phrase)

def execute(query, phrase=''):
    try:
        with connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB,
        ) as connection:
            with connection.cursor() as cursor:
                cursor.execute(query)
                connection.commit()
    except Error as e:
        print(e)
    finally:
        if phrase != '':
            print(phrase)

def execute_many(query, records, phrase=''):
    try:
        with connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB,
        ) as connection:
            with connection.cursor() as cursor:
                cursor.executemany(query, records)
                connection.commit()
    except Error as e:
        print(e)
    finally:
        if phrase != '':
            print(phrase)

def get_all_records(table):
    query = f"SELECT * FROM {table}"
    records = fetch(query)
    return records

def delete_all_records(table):
    delete_movies = f"DELETE FROM {table}"
    execute(delete_movies)
    print(f"[MySQL] Deleting all records from table '{table}'")

def is_in_records(dic, table):
    records = get_all_records(table)
    for record in records:
        if len(set(record) - set(dic.values())) == 2: # Skip if last value is equal to current value (except id and date)
            # if date_to_string(record[1]) == dic["datetime"]: 
            return True
    return False

def add_records(dic, table=DB_TABLE, force=False):
    if not is_in_records(dic, table) or force:

        query = f"""
        INSERT INTO {table}
        (datetime, currency, name, buy, sell, other)
        VALUES ( %s, %s, %s, %s, %s, %s )"""

        records = [
            dic["datetime"],
            dic["currency"],
            dic["name"],
            dic["buy"],
            dic["sell"],
            dic["other"]
            ],

        phrase = f"[MySQL] Entry for {dic['currency'].upper()} {dic['name'].upper()} added"
        
        execute_many(query, records, phrase)
    else:
        print(f"[MySQL] Entry is already in DB")

