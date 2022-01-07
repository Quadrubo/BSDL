import os
import sqlite3
from sqlite3 import Error


class Database:
    def __init__(self, db_folder_path, db_file_name):
        self.db_folder_path = db_folder_path
        self.db_file_name = db_file_name

        if not os.path.isdir(db_folder_path):
            os.mkdir(db_folder_path)

        self.create_tables()

    def connect(self):
        conn = None
        try:
            conn = sqlite3.connect(os.path.join(self.db_folder_path, self.db_file_name))
        except Error as e:
            print(e)

        return conn

    def get_episode(self, url):
        conn = self.connect()

        if conn is not None:
            sql = """ SELECT * FROM episodes WHERE url = ? """

            cursor = conn.cursor()
            cursor.execute(sql, (url,))
            result = cursor.fetchone()

            return result

    def create_table(self, conn, query):
        try:
            c = conn.cursor()
            c.execute(query)
        except Error as e:
            print(e)

    def refresh_series_data(self, series):
        for season in series.seasons:
            for episode in season.episodes:
                if episode.downloaded:
                    self.create_episode(episode)

    def create_episode(self, episode):
        if self.get_episode(episode.url) is None:
            conn = self.connect()

            if conn is not None:
                sql = """ 
                INSERT INTO episodes(
                    url
                ) VALUES (
                    ?
                ); """

                cursor = conn.cursor()
                cursor.execute(sql, (episode.url,))
                conn.commit()

    def create_tables(self):

        sql_create_episodes_table = """ 
        CREATE TABLE IF NOT EXISTS episodes (
            url varchar PRIMARY KEY
        ); """

        # create a database connection
        conn = self.connect()

        # create tables
        if conn is not None:
            # create projects table
            self.create_table(conn, sql_create_episodes_table)
