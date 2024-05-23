import os
import sqlite3
from sqlite3 import Error
import platform
import logging

import sqlite3
import subprocess

# name of video "IdUser_original_STT"
# name of video "IdUser_converted_STT"
# name of image "IdUser_portrait_image"

def main():
    create_table('SocialMedia.db')

def create_table(database_name:str):
    if not isinstance(database_name, str):
        raise ValueError("database_name must be an str")

    try:
        sqliteConnection = sqlite3.connect(database_name)
        sqlite_create_table_query = '''CREATE TABLE Media(
                                    id INTEGER PRIMARY KEY,
                                    user_id INTEGER,
                                    file_name TEXT NOT NULL UNIQUE,
                                    video_path text NOT NULL UNIQUE,
                                    target_path text NOT NULL,
                                    input_image_path text NOT NULL
                                    );'''

        cursor = sqliteConnection.cursor()
        logging.info("Successfully Connected to SQLite")
        cursor.execute(sqlite_create_table_query)
        sqliteConnection.commit()
        logging.info("SQLite table created")

        cursor.close()

    except sqlite3.Error as error:
        logging.error("Error while creating a sqlite table", error)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            logging.info("sqlite connection is closed")
def insert_data_into_database(database_name:str, user_id: int, file_name: str , video_path:str, target_path:str , input_image_path:str) -> None:
    if not isinstance(database_name, str):
        raise ValueError("database_name must be an str")
    if not isinstance(user_id, int):
        raise ValueError("user_id must be an integer")
    if not isinstance(file_name, str):
        raise ValueError("file_name must be an str")
    if not isinstance(video_path, str):
        raise ValueError("video_path must be an str")
    if not isinstance(target_path, str):
        raise ValueError("target_path must be an str")
    if not isinstance(database_name, str):
        raise ValueError("input_image_path must be an str")
    try:
        conn = sqlite3.connect(database_name)
        logging.info("[INFO] : Successful connection database!")
        cur = conn.cursor()
        sql_insert_file_query = '''INSERT INTO Media(user_id ,file_name, video_path ,target_path, input_image_path)
        VALUES(?, ?, ?, ?, ?)'''

        cur = conn.cursor()
        cur.execute(sql_insert_file_query, (user_id ,file_name, video_path ,target_path, input_image_path, ))
        conn.commit()
        logging.info("[INFO] : The data for ", file_name, " is in the database.")
    except Error as e:
        print(e)
    finally:
        if conn:
            conn.close()
        else:
            error = "Oh shucks, something is wrong here."

def select_data_by_userid(database_name:str ,user_id:int) -> dict:
    if not isinstance(database_name, str):
        raise ValueError("database_name must be an str")
    if not isinstance(user_id, int):
        raise ValueError("user_id must be an integer")
    try:
        conn = sqlite3.connect(database_name)
        cur = conn.cursor()
        logging.info("[INFO] : Connected to SQLite to select_data_by_userid")
        sql_fetch_blob_query = """SELECT * from Media where user_id = ?"""
        cur.execute(sql_fetch_blob_query, (user_id,))
        record = cur.fetchall()
        data = []
        for row in record:
            row_data = {
                "id": row[0],
                "file_name": row[1],
                "id_user": row[2],
                "video_path" : row[3],
                "target_path" : row[4],
                "input_image_path": row[5]
            }
            data.append(row_data)
        cur.close()
        logging.info("[INFO] : Select successfully.\n")
        return data
    except sqlite3.Error as error:
        logging.error("[ERROR] : Failed to select data from sqlite table", error)
    finally:
        if conn:
            conn.close()

def convert_into_binary(file_path):
    with open(file_path, 'rb') as file:
        binary = file.read()
    return binary
def insert_image_into_database(database_name:str , user_id:int, file_name:str, file_path, file_blob, type_file):
    try:
        conn = sqlite3.connect(database_name)
        print("[INFO] : Successful connection!")
        cur = conn.cursor()
        sql_insert_file_query = '''INSERT INTO uploads(user_id ,file_name, file_path ,file_blob, type_file)
        VALUES(?, ?, ?, ?, ?)'''

        cur = conn.cursor()
        cur.execute(sql_insert_file_query, (user_id , file_name, file_path, file_blob, type_file ))
        conn.commit()
        print("[INFO] : The blob for ", file_path, " is in the database.")
    except Error as e:
        print(e)
    finally:
        if conn:
            conn.close()
        else:
            error = "Oh shucks, something is wrong here."
def database_to_file_image(database_name:str ,entry_id):
    try:
        conn = sqlite3.connect(database_name)
        cur = conn.cursor()
        print("[INFO] : Connected to SQLite to read_blob_data")
        sql_fetch_blob_query = """SELECT * from uploads where id = ?"""
        cur.execute(sql_fetch_blob_query, (entry_id,))
        record = cur.fetchall()
        for row in record:
            converted_file_name = row[1]
            photo_binarycode  = row[2]
            # parse out the file name from converted_file_name
            # Windows developers should reverse "/" to "\" to match your file path names
            if platform.system() == "Windows":
                last_slash_index = converted_file_name.rfind(r"\\") + 1
            else:
                last_slash_index = converted_file_name.rfind("/") + 1

            # Chạy lệnh `dir` trên Windows
            # last_slash_index = converted_file_name.rfind("/") + 1
            final_file_name = converted_file_name[last_slash_index:]
            write_to_file(photo_binarycode, "test.mp3")
            print("[DATA] : Image successfully stored on disk. Check the project directory. \n")
        cur.close()
    except sqlite3.Error as error:
        print("[INFO] : Failed to read blob data from sqlite table", error)
    finally:
        if conn:
            conn.close()

def write_to_file(binary_data, file_name):
    with open(file_name, 'wb') as file:
        file.write(binary_data)
    print("[DATA] : The following file has been written to the project directory: ", file_name)



if __name__ == '__main__':
    main()
