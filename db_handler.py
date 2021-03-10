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
        self.cursor.row_factory = self.dict_factory



    def dict_factory(self, cursor, row):
        '''
        Used by sqlite3 to return data as dicts instead of tuples
        '''
        info = {}
        for idx, col in enumerate(cursor.description):
            info[col[0]] = row[idx]
        return info



    def increment(self, field: str, date: str):
        '''
        Increments either the ingress or egress field for a particular record.
        If that record doesn't exist, create one.

        Args:
            field (str): the field to increment
            date (str): the identifier for the record to edit. must be iso 8601 format (yyyy-mm-dd)
        '''
        self.create_record_if_needed(date)
        self.cursor.execute('SELECT ' + field + ' FROM entrants WHERE date=?', (date,))
        count = self.cursor.fetchall()[0][field]
        self.cursor.execute('UPDATE entrants SET ' + field + '=? WHERE date=?', (count+1, date))
        self.conn.commit()



    def create_record_if_needed(self, date: str):
        '''
        If a record with the given date doesn't exist, create one.

        Args:
            date (str): must be iso 8601 format (yyyy-mm-dd)
        '''
        self.cursor.execute(f'SELECT date FROM entrants WHERE rowid=(SELECT MAX(rowid) FROM entrants)')
        latest_date = self.cursor.fetchall()
        if not latest_date or date != latest_date[0]['date']:
            self.cursor.execute('INSERT INTO entrants VALUES (?, 0, 0)', (date,))
            self.conn.commit()



    def get_record(self, date: str) -> dict:
        '''
        Returns the ingress and egress fields from a particular record

        Args:
            date (str): must be iso 8601 format (yyyy-mm-dd)

        Returns:
            None: if no records exist with that date or
            dict: where keys are field names (str) and values are field values (str)
        '''
        self.cursor.execute('SELECT * FROM entrants WHERE date=?', (date,))
        data = self.cursor.fetchall()
        if not data:
            return None
        return data[0]



    def get_dates(self) -> [str]:
        '''
        Returns:
            [str]: all the dates
        '''
        self.cursor.execute('SELECT date FROM entrants')
        return self.cursor.fetchall()