import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from datetime import datetime
import db


def get_content(url: str):
    """
    Fetches the HTML content for a given URL

    :param url: defines the input URL whose HTML content has to be fetched
    :return: HTML content of the page
    """
    try:
        headers = {
            'User-Agent':
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 12_0_1) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/96.0.4664.45 Safari/537.36 '
        }
        r = requests.get(url, headers=headers)
        content = BeautifulSoup(r.content, 'lxml')
        return content
    except Exception as err:
        print(f'Error in fetching HTML content {err}')


def scraping_process(base_url: str):
    """
    Scrape the static website and add the data to a list

    :param base_url: defines the input URL that is to be scraped
    :return: list of manufacturers, models, categories and parts
    """
    try:

        start = datetime.now()
        print('Scraping request started')

        soup = get_content(base_url)
        temp_man = soup.find('div',
                             attrs={'class': 'c_container allmakes'}).find_all('a')
        manufacturers = [man.string.strip() for man in temp_man]
        print('Scraping manufacturers - done!')

        # Scrape the website for category names for a given manufacturer
        for a_man in manufacturers:
            print(f'Scraping started for manufacturer - {a_man}!')
            categories, models, parts = [], [], []
            soup = get_content(base_url + a_man)
            temp_cat = soup.find('div',
                                 attrs={'class': 'c_container allmakes allcategories'}).find_all('a')
            categories.extend([[a_man, cat.string.strip()] for cat in temp_cat])
            print('Scraping categories - done!')

            # Scrape the website for model names for a given category
            for man, cat in categories:
                soup = get_content(base_url + man + '/' + cat)
                temp_mod = soup.find('div',
                                     attrs={'class': 'c_container allmodels'}).find_all('a')
                models.extend([[man, cat, mod.string.strip()] for mod in temp_mod])
            print('Scraping models - done!')

            # Scrape the website for part names for a given model
            print('Scraping parts - started!')
            for man, cat, mod in models:
                soup = get_content(base_url + man + '/' + cat + '/' + mod)
                sub_sections = soup.find('div',
                                         attrs={'class': 'c_container modelSections'})

                if sub_sections:  # Some links contain subsections
                    sub_sections = [sub_section.get_text().strip()
                                    for sub_section in sub_sections.find_all('a')]

                    for sub_section in sub_sections:
                        sub_soup = get_content(base_url + man + '/' + cat + '/' + mod + '/' + sub_section)
                        temp_part = sub_soup.find('div',
                                                  attrs={'class': 'c_container allparts'})

                        if temp_part:
                            temp_part = temp_part.find_all('a')
                            parts.extend([[man, cat, mod, part.contents[0].strip(), part.span.text.strip()]
                                          if part.span is not None
                                          else [man, cat, mod, part.contents[0].strip(), None]
                                          for part in temp_part])
                else:
                    temp_part = soup.find('div',
                                          attrs={'class': 'c_container allparts'})

                    if temp_part:
                        temp_part = temp_part.find_all('a')
                        parts.extend([[man, cat, mod, part.contents[0].strip(), part.span.text.strip()]
                                      if part.span is not None
                                      else [man, cat, mod, part.contents[0].strip(), None]
                                      for part in temp_part])
            print('Scraping parts - done!')
            print(f'Complete scraping done for {a_man}!\nTime taken - {datetime.now() - start}')

            database_load_df = create_load_dataframes(parts)

            for table_name, df in database_load_df.items():
                load_df_to_db(df, table_name, db_conn)
            print('Database loaded')

    except Exception as err:
        print(f'Error in scraping the static website {err}')


def create_load_dataframes(parts: list):
    """
    Creates a dataframe from the list of models, categories and parts for a manufacturer
    Removes null values, formats the data and creates separate dataframes for database loading

    :param parts: defines the list of manufacturer, models, categories and parts
    :return: dict object with dataframes for table creation
    """
    try:
        # Strip the last occurrence of '-' from Part IDs
        for part in parts:
            if part[3][-1] == '-':
                part[3] = part[3][:-1].strip()

        manufacturer_df = pd.DataFrame(parts,
                                       columns=['manufacturer', 'category', 'model', 'part', 'part_category'])
        manufacturer_df['part_category'] = manufacturer_df['part_category'].replace(np.nan, 'Unknown')  # Replace nan

        # Creation of Model dataframe
        model_df = pd.DataFrame(columns=['id', 'model'])
        model_df['model'] = manufacturer_df.model.dropna().unique()
        model_df['id'] = model_df.index + 1

        # Creation of Category dataframe
        category_df = pd.DataFrame(columns=['id', 'category'])
        category_df['category'] = manufacturer_df.category.dropna().unique()
        category_df['id'] = category_df.index + 1

        # Creation of Part category dataframe
        part_category_df = pd.DataFrame(columns=['id', 'part_category'])
        part_category_df['part_category'] = manufacturer_df.part_category.dropna().unique()
        part_category_df['id'] = part_category_df.index + 1

        # Creation of Manufacturer dataframe
        manufacturer_df = manufacturer_df.merge(category_df)
        manufacturer_df = manufacturer_df.drop(['category'], axis=1)
        manufacturer_df = manufacturer_df.rename(columns={'id': 'category_id'})
        manufacturer_df = manufacturer_df.merge(model_df)
        manufacturer_df = manufacturer_df.drop(['model'], axis=1)
        manufacturer_df = manufacturer_df.rename(columns={'id': 'model_id'})
        manufacturer_df = manufacturer_df.merge(part_category_df)
        manufacturer_df = manufacturer_df.drop(['part_category'], axis=1)
        manufacturer_df = manufacturer_df.rename(columns={'id': 'part_category_id'})

        print('Dataframes created for DB loading!')

        df_tbl_dict = {'tbl_manufacturer': manufacturer_df, 'tbl_model': model_df,
                       'tbl_category': category_df, 'tbl_part_category': part_category_df}

        return df_tbl_dict
    except Exception as err:
        print(f'Error in creating dataframes to load database {err}')


def load_df_to_db(data, table, conn):
    """
    Loads database from dataframes

    :param data: defines the dataframe to be pushed into the database
    :param table: defines the table name to be loaded
    :param conn: defines the database connection to be used
    """
    try:
        data.to_sql(name=table, con=conn, if_exists='append', index=False)
        conn.commit()
    except Exception as err:
        print(f'Error in loading the SQLite database tables {err}')


if __name__ == '__main__':
    scrape_url = 'https://www.urparts.com/index.cfm/page/catalogue/'

    db_conn, _ = db.create_connection()

    scraping_process(scrape_url)

    db.close_connection(db_conn)
