# python standard libraries
import sqlite3



class DB_Handler:
    '''
    Handles all database connections and interactions

    Attributes:
        conn (sqlite3.Connection)
        cursor (sqlite3.Cursor)
    '''
    def __init__(self, filename):
        '''
        Args:
            filename (str): the file of the database
        '''
        self.conn = sqlite3.connect(filename)
        self.cursor = self.conn.cursor()
        self.cursor.execute('CREATE TABLE IF NOT EXISTS entrants (date TEXT, ingress INTEGER, egress INTEGER)')



    def increment(self, field: str, date: str):
        '''
        Increments either the ingress or egress field for a particular record.
        If that record doesn't exist, create one.

        Args:
            field (str): the field to increment
            date (str): the identifier for the record to edit. must be iso 8601 format (yyyy-mm-dd)
        '''
        self.create_record_if_needed(date)
        self.cursor.execute(f'SELECT {field} FROM entrants WHERE date={date}')
        count = self.cursor.fethcall()[0]
        self.cursor.execute(f'UPDATE entrants SET {field}={count+1} WHERE date={date}')
        self.conn.commit()



    def create_record_if_needed(self, date: str):
        '''
        If a record with the given date doesn't exist, create one.

        Args:
            date (str): must be iso 8601 format (yyyy-mm-dd)
        '''
        self.cursor.execute(f'SELECT {date} FROM entrants WHERE rowid=(SELECT MAX(rowid) FROM entrants)')
        latest_date = self.cursor.fetchall()[0]
        if date != latest_date:
            self.cursor.execute(f'INSERT INTO entrants VALUES ({date}, 0, 0)')
            self.conn.commit()