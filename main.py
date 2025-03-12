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
    # cursor.execute("CREATE TABLE category (id INT PRIMARY KEY AUTO_INCREMENT,name VARCHAR(255));")
    # cursor.execute("CREATE TABLE product (id INT PRIMARY KEY AUTO_INCREMENT,name VARCHAR(255),description TEXT,price INT,quantity INT,id_category INT,FOREIGN KEY (id_category) REFERENCES category(id));")
   
    # cursor.execute("INSERT INTO category (name) VALUES ('Électronique'),('Vêtements'),('Alimentation'),('Maison'),('Sport');")
    # cursor.execute("INSERT INTO category (name) VALUES ('Électronique'),('Vêtements'),('Alimentation'),('Maison'),('Sport');")
    # results= cursor.fetchall()
    # print(results)
    
    cursor.execute("SELECT * from category;")
    results= cursor.fetchall()
    print(results)
    
    
    cursor.close()
    mydb.close()
    
    