import sqlite3

db_path = '/scraper/database/catalogue.db'


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


def create_table():
    """
    Creates the required tables for the given SQLite database
    """
    try:
        conn, cur = create_connection()

        # Create manufacturer table
        cur.execute('''CREATE TABLE IF NOT EXISTS tbl_manufacturer(
                 manufacturer text,
                 category_id integer,
                 model_id integer,
                 part text,
                 part_category_id integer
                )''')

        # Create model table
        cur.execute('''CREATE TABLE IF NOT EXISTS tbl_model(
                 id integer,
                 model text
                )''')

        # Create category table
        cur.execute('''CREATE TABLE IF NOT EXISTS tbl_category(
                 id integer,
                 category text
                )''')

        # Create part_category table
        cur.execute('''CREATE TABLE IF NOT EXISTS tbl_part_category(
                 id integer,
                 part_category text
                )''')

        close_connection(conn)
    except Exception as err:
        print(f'Error in creating tables in the SQLite database {err}')


def close_connection(conn):
    """
    Closes the connection with the SQLite database
    :param conn: Connection object for the database
    """
    try:
        conn.close()
    except Exception as err:
        print(f'Error in closing connection with the SQLite database {err}')
