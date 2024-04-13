# a database class that has the ability to perform a semantic search on itself and return the most relevant result.

# The database class will have the following methods:
# - search: searches the database for a given query and returns the most relevant result
# - add: adds a new entry to the database
# - remove: removes an entry from the database
# - update: updates an entry in the database
# - get: retrieves an entry from the database
# - get_all: retrieves all entries from the database
# - clear: clears the database
# - save: saves the database to disk
# - load: loads the database from disk

import os
import sys
import sqlite3

stored_path = os.path.join(os.getcwd(), 'modus-reborn', '__storage__')

class Database:
    def __init__(self):
        # create the sqlite database if it does not exist
        self.db = sqlite3.connect(stored_path + '/command_database.sqlite')
        # create a cursor object to interact with the database
        self.cursor = self.db.cursor()
        # create the table if it does not exist
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS commands(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                commandname TEXT,
                associatedcode TEXT
                lastused TEXT
            )
        ''')
        pass
    
    def search(self, query):
        # search the database for the given query
        self.cursor.execute('SELECT * FROM commands WHERE commandname LIKE ?', ('%' + query + '%',))
        return self.cursor.fetchall()
    
    def modify(self, commandname, newcode):
        # update the associated code for the given command
        self.cursor.execute('UPDATE commands SET associatedcode = ? WHERE commandname = ?', (newcode, commandname))
        self.save()
        
    def add(self, commandname, associatedcode):
        # add a new entry to the database
        self.cursor.execute('INSERT INTO commands(commandname, associatedcode) VALUES(?, ?)', (commandname, associatedcode))
        self.save()
        
    def remove(self, commandname):
        # remove an entry from the database
        self.cursor.execute('DELETE FROM commands WHERE commandname = ?', (commandname,))
        self.save()
        
    def get(self, commandname):
        # retrieve an entry from the database
        self.cursor.execute('SELECT * FROM commands WHERE commandname = ?', (commandname,))
        return self.cursor.fetchone()
    
    def get_all(self):
        # retrieve all entries from the database
        self.cursor.execute('SELECT * FROM commands')
        return self.cursor.fetchall()
    
    def clear(self):
        # clear the database
        self.cursor.execute('DELETE FROM commands')
        self.save()
    
    def save(self):
        # save the database to disk
        self.db.commit()
        
        



if __name__ == "__main__":
    db = Database()
    print("Database class created.")
    all = db.get_all()
    # test the search function
    print(all)
