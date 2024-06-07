
import sqlite3
import threading
from __src__.AI.nlp.tiny_bert import TinyBERT
from __src__.AI.nlp.classifier import RequestClassifier
from __src__.DATA.manage_files import FileManager

files = FileManager()
bert = TinyBERT()
ml = RequestClassifier()

stored_path = files.locateDirectory("databases")

class Database:
    def __init__(self):
        self.local = threading.local()
        self.db_path = files.createFile(stored_path, "commands_database.sqlite")
        self.ensure_table()

    def get_connection(self):
        if not hasattr(self.local, 'connection'):
            self.local.connection = sqlite3.connect(self.db_path, check_same_thread=False)
            self.local.cursor = self.local.connection.cursor()
        return self.local.connection, self.local.cursor

    def ensure_table(self):
        conn, cursor = self.get_connection()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS commands(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                commandname TEXT,
                associatedcode TEXT,
                lastused TEXT
            )
        ''')
        conn.commit()

    def search(self, query):
        _, cursor = self.get_connection()
        cursor.execute('SELECT * FROM commands WHERE commandname LIKE ?', ('%' + query + '%',))
        return cursor.fetchall()

    def modify(self, commandname, newcode):
        conn, cursor = self.get_connection()
        cursor.execute('UPDATE commands SET associatedcode = ? WHERE commandname = ?', (newcode, commandname))
        conn.commit()

    def add(self, commandname, associatedcode):
        if self.get(commandname) is None:
            conn, cursor = self.get_connection()
            cursor.execute('INSERT INTO commands (commandname, associatedcode) VALUES (?, ?)', (commandname, associatedcode))
            conn.commit()
        else:
            self.modify(commandname, associatedcode)

    def remove(self, commandname):
        conn, cursor = self.get_connection()
        cursor.execute('DELETE FROM commands WHERE commandname = ?', (commandname,))
        conn.commit()

    def get(self, commandname):
        _, cursor = self.get_connection()
        cursor.execute('SELECT * FROM commands WHERE commandname = ?', (commandname,))
        return cursor.fetchone()

    def get_all(self):
        _, cursor = self.get_connection()
        cursor.execute('SELECT * FROM commands')
        return cursor.fetchall()

    def wipe_database(self):
        conn, cursor = self.get_connection()
        cursor.execute('DELETE FROM commands')
        conn.commit()
        

    # perform a semantic search on the database to find the most relevant command.
    # the function first cleans and normalizes the query text. It then checks for a subset match, 
    # where all words in a command are present in the cleaned query. If such a match is found, 
    # the command is immediately returned. If no command words are a subset but there are common 
    # words between any command and the query, the function proceeds to use BERT for 
    # a deeper semantic analysis to identify the most similar command. If there are no common words 
    # at all between the query and any command in the database, the function returns None, avoiding 
    # unnecessary BERT computation.
    def semantic_search(self, query):
        all_commands = self.get_all()
        if not all_commands:
            return None
        
        # normalize the query to compare only the words it contains
        query_words = set(query.lower().split())
        
        # prepare a dictionary mapping each command to its words set
        command_dict = {command[1]: set(command[1].lower().split()) for command in all_commands}
        
        # initialize list to store commands with any common words
        commands_with_common_words = []
        
        # check if any command's words have an intersection with the query words
        for command, cmd_words in command_dict.items():
            
            print(f"Comparing word sets: {cmd_words} vs {query_words}")
            if cmd_words & query_words:  # check for intersection
                commands_with_common_words.append(command)
                if cmd_words <= query_words:
                    print(f"Matching command found in database: {command}")
                    return command
        
        # if no verbatim or subset match is found but there are common words, use machine learning to find the most similar command
        if commands_with_common_words:
            print("Searching for the most similar command...")
            similarity, most_similar = bert.batch_similarity(query, commands_with_common_words, 0.35)
            print(f"Most similar command found: {most_similar}, with similarity: {similarity}")
            return most_similar
        else:
            print("No common words found between the query and database commands.")
            return None


if __name__ == "__main__":
    db = Database()
    print("Database class created.")
    all = db.get_all()
    print(all)
