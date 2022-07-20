from mysql.connector import connect, Error
import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB = os.getenv('DB')

try:
    with connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB,
    ) as connection:

        create_dolar_table_query = """
        CREATE TABLE cotizacion(
            id INT AUTO_INCREMENT PRIMARY KEY,
            datetime DATETIME,
            currency VARCHAR(50),
            name VARCHAR(50),
            buy FLOAT(10,2),
            sell FLOAT(10,2),
            other FLOAT(10,2)
        )
        """
        with connection.cursor() as cursor:
            cursor.execute(create_dolar_table_query)
            connection.commit()

        print('Table created.\n')
    

except Error as e:
    print(e)

