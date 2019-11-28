import sqlite3

import sqlite3
from sqlite3 import Error
from utils import timezone_time
from datetime import datetime
import os

def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file, check_same_thread=False )
        return conn
    except Error as e:
        print(e)

    return conn


database = r"sqlite3.db"
db_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), database)
conn = create_connection(database)


def create_table(create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    with conn:
        try:
            c = conn.cursor()
            c.execute(create_table_sql)
        except Error as e:
            print(e)


def create_track_record(track):
    with conn:
        sql = """ INSERT INTO music(telegram_file_id,deezer_link,performer,title,download_count,last_downloaded) 
        VALUES (:telegram_file_id,:deezer_link,:performer,:title,:download_count,:last_downloaded) """
        cur = conn.cursor()
        cur.execute(sql, track)
        return cur.lastrowid

def create_download_record(download_record):
    with conn:
        sql = """ INSERT INTO download(telegram_id, telegram_full_name, telegram_link, telegram_name, telegram_username, music_id) 
        VALUES (:telegram_id, :telegram_full_name, :telegram_link, :telegram_name, :telegram_username, :music_id) """
        cur = conn.cursor()
        cur.execute(sql, download_record)
        return cur.lastrowid

    
def update_track_record(track):
    with conn:
        sql = "UPDATE music SET download_count=download_count+1,last_downloaded=:last_downloaded, performer=:performer, title=:title WHERE deezer_link=:deezer_link "
        cur = conn.cursor()
        cur.execute(sql, track)

def retreive_track_record(track):
    with conn:
        sql = "SELECT * from music WHERE deezer_link=:deezer_link "
        cur = conn.cursor()
        cur.execute(sql, track)
        return cur.fetchone()   
        
def retreive_download_history():
    with conn:
        sql = "SELECT * from download"
        cur = conn.cursor()
        cur.execute(sql)
        return cur.fetchall()

def create_music_table():
    sql_create_music_table = """ CREATE TABLE IF NOT EXISTS music (
                                        id integer PRIMARY KEY,
                                        telegram_file_id text NOT NULL,
                                        deezer_link text NOT NULL,
                                        download_count integer NOT NULL,
                                        last_downloaded text NOT NULL
                                    ); """
    create_table(sql_create_music_table)
    with conn:
        sql = "CREATE UNIQUE INDEX IF NOT EXISTS idx_deezer_link ON music (deezer_link);"
        cur = conn.cursor()
        cur.execute(sql)
    
def create_download_table():
    sql_create_download_table = """ CREATE TABLE IF NOT EXISTS download (
                                        id integer PRIMARY KEY,
                                        telegram_id integer NOT NULL, 
                                        telegram_full_name text,
                                        telegram_link text,
                                        telegram_name text,
                                        telegram_username text,
                                        music_id integer NOT NULL,
                                        FOREIGN KEY (music_id) REFERENCES music (id)
                                    ); """
    create_table(sql_create_download_table)

def alter_music_table_add_music_info():
    with conn:
        cur = conn.cursor()
        a = cur.execute("PRAGMA table_info(music);")
        column_names = [item[1] for item in a.fetchall()]
        if 'title' not in column_names and 'performer' not in column_names:
            sql = "ALTER TABLE music ADD COLUMN performer;"
            cur.execute(sql)
            sql = "ALTER TABLE music ADD COLUMN title;"
            cur.execute(sql)
            

        


def main():
    alter_music_table_add_music_info()
    create_download_table()
    # create_music_table()
    # track = {
    #     "telegram_file_id": "jafasdfa",
    #     "deezer_link": "www.deezer.com/track/13128312",
    #     "download_count": 1,
    #     "last_downloaded": timezone_time(datetime.now()),
    # }
    # create_track_record(track)
    # track_update = {
    #     "last_downloaded":timezone_time(datetime.now()),
    #     "deezer_link":"www.deezer.com/track/13128312",
    # }
    # update_track_record(track_update)
    # track_retreive = {
    #     "deezer_link":"www.deezer.com/track/13128312",
    # }
    # item = retreive_track_record(track_retreive)
    # print(item)

if __name__ == "__main__":
    main()
