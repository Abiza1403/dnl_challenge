from fastapi import FastAPI
import uvicorn
import swagger_meta as sm
import db


app = FastAPI(
    title="CatalogueApp",
    description=sm.description
)


@app.get("/")
def read_root():
    """
    Displays root URL
    """
    return '''Welcome to Catalogue App'''


@app.get("/getInfo")
def get_manufacturer_info(manufacturer: str = None,
                          skip: int = 0,
                          limit: int = 10):
    """
    Retrieves the complete category and part info for a given manufacturer

    :param manufacturer: Provided by user from a list of manufacturers
    :param skip: defines the number of records to skip at start
    :param limit: defines a limit to the number of records that can be displayed at a time
    :return: data retrieved from database for a given manufacturer
    """
    try:
        if manufacturer not in sm.manufacturer_list:
            return f'Enter a valid manufacturer from {sm.manufacturer_list}'

        conn, cur = db.create_connection()

        sql_query = '''SELECT m.manufacturer, c.category, d.model, m.part, p.part_category
        FROM tbl_manufacturer m
        INNER JOIN tbl_category c
        ON c.id = m.category_id
        INNER JOIN tbl_model d
        ON d.id = m.model_id
        INNER JOIN tbl_part_category p
        ON p.id = m.part_category_id
        WHERE m.manufacturer = :manufacturer
        LIMIT :limit OFFSET :skip
        '''
        cur.execute(sql_query,
                    {'manufacturer': manufacturer, 'limit': limit, 'skip': skip})

        desc = cur.description
        column_names = [col[0] for col in desc]
        data = [dict(zip(column_names, row)) for row in cur.fetchall()]

        db.close_connection(conn)

        return data
    except Exception as err:
        print(f'Error in retrieving data from the SQLite database {err}')


if __name__ == '__main__':
    uvicorn.run('main:app', reload=True, port=8001, host='0.0.0.0')
