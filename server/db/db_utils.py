import sqlite3
from sqlite3 import Error

from typing import Any
class DBUtils:
    @staticmethod    
    def create_connection(db_file : str, timeout:float=20., logger=None)-> sqlite3.Connection:
        """ create a database connection to a SQLite database """
        conn = None
        try:
            conn = sqlite3.connect(db_file, timeout=timeout)
        except Error as e:
            logger.error(e)
        return conn
    @staticmethod
    def create_table(table:str, fields:list[str], conn:sqlite3.Connection, logger=None) -> None:
        query = f'CREATE TABLE IF NOT EXISTS {table} ({",".join(fields)});'
        cur = conn.cursor()
        cur.execute(query)
        conn.commit()

    @staticmethod
    def insert_row(table:str, fields:list[str], values:list[str], conn:sqlite3.Connection, logger=None) -> int:
        query = f'INSERT INTO {table}({",".join(fields)}) VALUES({",".join(["?" for _ in range(len(fields))])})'
        cur = conn.cursor()
        cur.execute(query, values)
        conn.commit()
        return cur.lastrowid
    @staticmethod
    def select_rows(table:str, fields:list[str], condition:str, values:list[str], conn:sqlite3.Connection, logger=None) -> list:
        query = f'SELECT {",".join(fields)} FROM {table} WHERE {condition}'
        cur = conn.cursor()
        cur.execute(query, values)
        rows = cur.fetchall()
        return rows
    @staticmethod
    def delete_row(table:str, condition:str, values:list[str], conn:sqlite3.Connection, logger=None) -> None:
        query = f'DELETE FROM {table} WHERE {condition}'
        cur = conn.cursor()
        cur.execute(query, values)
        conn.commit()
    @staticmethod
    def delete_table(table:str, conn:sqlite3.Connection, logger=None) -> None:
        query = f'DROP TABLE {table}'
        cur = conn.cursor()
        cur.execute(query)
        conn.commit()
    @staticmethod
    def update_row(table:str, fields:list[str], values:list[str], condition:str, condition_values:list[str], conn:sqlite3.Connection, logger=None) -> None:
        query = f'UPDATE {table} SET {",".join([f"{fields[i]}=?" for i in range(len(fields))])} WHERE {condition}'
        cur = conn.cursor()
        cur.execute(query, values + condition_values)
        conn.commit()
    @staticmethod
    def get_tables(conn:sqlite3.Connection, logger=None) -> list:
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
        rows = cur.fetchall()
        return rows
    @staticmethod
    def get_table_fields(table:str, conn:sqlite3.Connection, logger=None) -> list:
        cur = conn.cursor()
        cur.execute(f"PRAGMA table_info({table});")
        rows = cur.fetchall()
        return rows
    @staticmethod
    def update_table(table:str, fields:list[str], conn:sqlite3.Connection, logger=None) -> None:
        cur = conn.cursor()
        for field in fields:
            cur.execute(f"ALTER TABLE {table} ADD COLUMN {field};")
        conn.commit()
    @staticmethod
    def apply_query(query:str, values:list[Any],conn:sqlite3.Connection, logger=None) -> None:
        cur = conn.cursor()
        cur.execute(query,values)
        conn.commit()
    @staticmethod
    def return_query(query:str,values:list[Any],conn:sqlite3.Connection, logger=None) -> list:
        cur = conn.cursor()
        cur.execute(query,values)
        rows = cur.fetchall()
        return rows
if __name__ == '__main__':
    db_file = 'test.sqlite3'
    conn = DBUtils.create_connection(db_file)
    DBUtils.create_table('test', ['id INTEGER PRIMARY KEY', 'name TEXT NOT NULL'], conn)
    DBUtils.insert_row('test', ['name'], ['test'], conn)
    DBUtils.insert_row('test', ['name'], ['test2'], conn)
    DBUtils.insert_row('test', ['name'], ['test3'], conn)
    DBUtils.delete_row('test', 'id=?', [1], conn)
    DBUtils.delete_table('test', conn)
    DBUtils.create_table('test2', ['id INTEGER PRIMARY KEY', 'name TEXT NOT NULL'], conn)
    DBUtils.insert_row('test2', ['name'], ['test'], conn)
    a = DBUtils.select_row('test2', ['name'], 'id=?', [1], conn)
    print(a)
    DBUtils.get_table_fields('test2', conn)
    DBUtils.update_row('test2', ['name'], ['test2'], 'id=?', [1], conn)
    b = DBUtils.get_table_fields('test2', conn)
    print (b)
    DBUtils.update_table('test2', ['age INTEGER'], conn)
    DBUtils.update_row('test2', ['age'], [1], 'id=?', [1], conn)
    print(conn)
    conn.close()