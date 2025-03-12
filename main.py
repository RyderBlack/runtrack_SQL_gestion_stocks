import os
import mysql.connector
from dotenv import load_dotenv


load_dotenv()

PASSKEY = os.getenv('PASSKEY')



mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password= PASSKEY,
    database="store_SQL"
)

if mydb.is_connected():
    db_info = mydb.get_server_info()
    print(f"Connected to MySQL version {db_info}")
    
    cursor = mydb.cursor()
    # cursor.execute("CREATE TABLE animal (id INT PRIMARY KEY NOT NULL AUTO_INCREMENT, name varchar(255), breed varchar(100), id_cage_type INT, birthdate INT, country varchar(100) );")
    # cursor.execute("DESCRIBE animal;")
    # results= cursor.fetchall()
    # print(results)
    
    # cursor.execute("CREATE TABLE cage (id INT PRIMARY KEY NOT NULL AUTO_INCREMENT, surface INT, max_capacity INT);")
    # cursor.execute("DESCRIBE cage;")
    # results= cursor.fetchall()
    # print(results)
    
    cursor.execute("SELECT * from animal;")
    results= cursor.fetchall()
    print(results)
    
    
    cursor.close()
    mydb.close()