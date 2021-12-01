import sqlite3

db_path = '/restapi/database/catalogue.db'


def create_connection():
    """
    Creates connection with the SQLite database
    :return: Connection and Cursor object
    """
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        return conn, cur
    except Exception as err:
        print(f'Error in establishing connection with SQLite database {err}')


def close_connection(conn):
    """
    Closes the connection with the SQLite database
    :param conn: Connection object for the database
    """
    try:
        conn.close()
    except Exception as err:
        print(f'Error in closing the connection with SQLite database {err}')
