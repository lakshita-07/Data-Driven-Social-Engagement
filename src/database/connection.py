import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()

def get_connection():
    connection = mysql.connector.connect(
        host=os.getenv("DB_host"),
        user=os.getenv("DB_user"),
        password=os.getenv("DB_password"),
        database=os.getenv("DB_name")
    )
    return connection
