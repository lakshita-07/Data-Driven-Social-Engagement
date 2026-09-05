from connection import get_connection

connection = get_connection()

if connection.is_connected():
    print("Database connected successfully")

connection.close()