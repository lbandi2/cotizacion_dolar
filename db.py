from mysql.connector import connect, Error
import os
from datetime import datetime

from utils import date_to_string
from dotenv import load_dotenv

load_dotenv()

class DB:
    DB_HOST = os.getenv('DB_HOST')
    DB_USER = os.getenv('DB_USER')
    DB_PASSWORD = os.getenv('DB_PASSWORD')
    DB = os.getenv('DB')
    DB_TABLE = "dolar_cotizacion"
    MAX_AMOUNT = 50

    def __init__(self, currency, name):
        self.currency = currency
        self.name = name

    def fetch(self, query, phrase='', dictionary=True):
        try:
            with connect(
                host=self.DB_HOST,
                user=self.DB_USER,
                password=self.DB_PASSWORD,
                database=self.DB,
            ) as connection:
                with connection.cursor(dictionary=dictionary) as cursor:
                    cursor.execute(query)
                    result = cursor.fetchall()
                    return result
        except Error as e:
            print(e)
        finally:
            if phrase != '':
                print(phrase)

    def execute_many(self, query, records, phrase=''):
        try:
            with connect(
                host=self.DB_HOST,
                user=self.DB_USER,
                password=self.DB_PASSWORD,
                database=self.DB,
            ) as connection:
                with connection.cursor() as cursor:
                    cursor.executemany(query, records)
                    connection.commit()
        except Error as e:
            print(e)
        finally:
            if phrase != '':
                print(phrase)

    def last_record(self):
        query = f"SELECT * FROM {self.DB_TABLE} WHERE name='{self.name}' AND currency='{self.currency}' ORDER BY datetime DESC LIMIT 1"
        records = self.fetch(query)
        return records

    def is_in_records(self, new_record):
        for record in self.last_record():
            if record['buy'] == new_record['buy']:
                if record['sell'] == new_record['sell']:
                    if record['other'] == new_record['other']:
                        return True
        return False

    def add_records(self, new_record, force=False):
        if not self.is_in_records(new_record) or force:

            query = f"""
            INSERT INTO {self.DB_TABLE}
            (datetime, currency, name, buy, sell, other)
            VALUES ( %s, %s, %s, %s, %s, %s )"""

            records = [
                new_record["datetime"],
                new_record["currency"],
                new_record["name"],
                new_record["buy"],
                new_record["sell"],
                new_record["other"]
                ],

            phrase = f"[MySQL] Entry for {new_record['currency'].upper()} {new_record['name'].upper()} added"
            
            self.execute_many(query, records, phrase)
        else:
            print(f"[MySQL] Entry is already in DB")
