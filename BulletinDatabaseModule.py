import sqlite3
import cryptography

# SQLite3 supports TEXT, INTEGER, REAL, BLOB and NULL only by default.

class DB:
    def __init__(self):
        self.conn  = sqlite3.connect('db/users.db3')
        self.log  = sqlite3.connect('db/log.db3')

        #Make start up entry.
        c = self.log.cursor()

        # Create table
        c.execute('''create table stocks
        (date text, trans text, symbol text,
        qty real, price real)''')

        # Insert a row of data
        c.execute("""insert into stocks
                values ('2006-01-05','BUY','RHAT',100,35.14)""")

        # Save (commit) the changes
        self.log.commit()

        # We can also close the cursor if we are done with it
        c.close()

    def write_log(self, log):
        #Make start up entry.
        c = self.log.cursor()

        # Insert a row of data
        c.execute("""insert into stocks
                values ('2006-01-05','BUY','RHAT',100,35.14)""")

        # Save (commit) the changes
        self.log.commit()

        # We can also close the cursor if we are done with it
        c.close()

    
class Conf:
    def __init__(self):
        return NotImplemented
    
    def create_database_files(self):
        import os
        os.system("echo >> ./db/users.db3") # echo >> to be OS agnostic
        os.system("echo >> ./db/log.db3")
        os.system("echo >> ./db/board.db3")
        del os # try and increase security in program. if os is only available for milliseconds during the setup process alone,
            #     security of program is massively increased

        self.create_tables()

    def create_tables(self):
        for db in ["users", "log", "boards"]:
            tmp_conn  = sqlite3.connect(f'db/{db}.db3')

            c = tmp_conn.cursor()

            if db == "users":
                # Create table
                c.execute(f'''create table {db}
                (username text, password text, email text)''')
            elif db == "log":
                c.execute(f'''create table {db}
                (date integer, time integer, log text)''') #follow structure 20231231 as 31st Dec 2023. time as 23:59
            elif db == "boards":
                c.execute(f'''create table boards
                (boardtitle text)''') 

            # closing cursor and connection to db
            tmp_conn.commit()
            c.close()
            tmp_conn.close()