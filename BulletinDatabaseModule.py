import sqlite3
import cryptography
from datetime import datetime

# SQLite3 supports TEXT, INTEGER, REAL, BLOB and NULL only by default.
# https://www.sqlite.org/datatype3.html

class DB:
    def __init__(self, config):
        self.config = config
    
    def connect(self):
        return sqlite3.connect('db/bb.db3')

    def get_boards(self):
        db = self.connect() 
        c = db.cursor()
        c.execute("select * from boards")

        boards = c.fetchall()

        # Close cursor.
        c.close()

        # Close connection.
        db.close()

        return boards
    
    def get_board_info(self, boardid):
        db = self.connect() 
        c = db.cursor()
        c.execute(f"select * from boards where boardid = '{boardid}'")

        board = c.fetchall()

        # Close cursor.
        c.close()

        # Close connection.
        db.close()

        return board
    
    def get_posts_from_board(self, boardid):
        db = self.connect() 
        c = db.cursor()
        c.execute(f"select * from posts where boardid = '{boardid}'")

        posts = c.fetchall()

        # Close cursor.
        c.close()

        # Close connection.
        db.close()

        return posts
    
    def get_post_info(self, postid):
        db = self.connect() 
        c = db.cursor()
        c.execute(f"select * from posts where postid = '{postid}'")

        post = c.fetchone()

        # Close cursor.
        c.close()

        # Close connection.
        db.close()

        return post
    
    def get_comments_from_post(self, postid):
        db = self.connect() 
        c = db.cursor()
        c.execute(f"select * from comments where postid = '{postid}'")

        comments = c.fetchall()

        # Close cursor.
        c.close()

        # Close connection.
        db.close()

        return comments
    
    def create_comment(self, postid, commentcontent, commentauthorid, commentauthorname, \
                       commentdate=datetime.utcnow().strftime('%Y%m%d'), commenttime=datetime.utcnow().strftime('%H%M%S')):
        db = self.connect()
        c = db.cursor()

        #Get total amount of comments on all posts, so we can add one to that and give this comment an ID
        c.execute("select count(*) from comments")
        commentid = c.fetchone()[0]+1

        c.execute(f"""insert into comments
                values ({postid}, {commentid}, '{commentcontent}', {commentauthorid}, '{commentauthorname}', {commentdate}, {commenttime})""")
        
        # Save (commit) the changes.
        db.commit()

        # Close cursor.
        c.close()

        # Close connection.
        db.close()
    
    def create_board(self, boardid, boardtitle, boarddescription, boardicon):
        db = self.connect() 
        c = db.cursor()
        c.execute(f"""insert into boards
                values ({boardid}, '{boardtitle}', '{boarddescription}', '{boardicon}')""")

        # Save (commit) the changes.
        db.commit()

        # Close cursor.
        c.close()

        # Close connection.
        db.close()

    def create_post(self, boardid, posttitle, postcontent, postauthorid, \
                    postdate=datetime.utcnow().strftime('%Y%m%d'), posttime=datetime.utcnow().strftime('%H%M%S')):
        db = self.connect() 
        c = db.cursor()

        #Get total amount of posts on all boards, so we can add one to that and give this post an ID
        c.execute("select count(*) from posts")
        postid = c.fetchone()[0]+1

        c.execute(f"""insert into posts
                values ({boardid}, {postid}, '{posttitle}', '{postcontent}', {postauthorid}, {postdate}, {posttime})""")

        # Save (commit) the changes.
        db.commit()

        # Close cursor.
        c.close()

        # Close connection.
        db.close()


    def write_log(self, log_message):
        #Make entry.
        db = self.connect() 
        c = db.cursor()

        # Insert a row of data.
        c.execute(f"""insert into log
                values ({datetime.utcnow().strftime('%Y%m%d')}, {datetime.utcnow().strftime('%H%M%S')}, '{log_message}')""")

        # Save (commit) the changes.
        db.commit()

        # Close cursor.
        c.close()

        # Close connection.
        db.close()

    
class Configure:
    def __init__(self):
        import ast
        try:
            f = open("pybb.conf", "r")
            conf = f.read()
            self.conf = ast.literal_eval(conf)
            f.close()
        except Exception as e:
            self.reset_database()
            self.__init__()

    def get_config(self):
        return self.conf
            

    def reset_database(self):
        print("pybb.conf not found. Creating pybb.conf.")
        with open("pybb.conf", "w") as f:
            with open("defaults.conf", "r") as defaults:
                f.write(defaults.read())
        print("pybb.conf created. Please edit pybb.conf to your liking.")

        print("Creating database files.")
        self.create_database_files()
        print("Database files created.")
        
        print("Setup complete. Please restart the program.")
    
    def create_database_files(self):
        import os
        os.system("echo >> ./db/bb.db3") # echo >> to be OS agnostic
        del os # try and increase security in program. if os is only available for milliseconds during the setup process alone,
            #     security of program is massively increased

        self.create_tables()

    def create_tables(self):
        for db in ["users", "log", "boards", "posts", "comments"]:
            tmp_conn  = sqlite3.connect(f'db/bb.db3')

            c = tmp_conn.cursor()

            if db == "users":
                # Create table
                c.execute(f'''create table {db}
                (userid integer, username text, hashedpassword text, email text, datejoined integer, locked integer)''')
            elif db == "log":
                c.execute(f'''create table {db}
                (date integer, time integer, log text)''') #follow structure 20231231 as 31st Dec 2023. time as 23:59
            elif db == "boards":
                c.execute(f'''create table {db}
                (boardid integer, boardtitle text, boarddescription text, boardicon text)''') #boardicon is base64 encoded image.
            elif db == "posts":
                c.execute(f'''create table {db}
                (boardid integer, postid integer, posttitle text, postcontent text, postauthorid integer, postdate integer, posttime integer)''')
            elif db == "comments":
                c.execute(f'''create table {db}
                (postid integer, commentid integer, commentcontent text, commentauthorid integer, commentauthorname string, commentdate integer, commenttime integer)''')

            # closing cursor and connection to db
            tmp_conn.commit()
            c.close()
            tmp_conn.close()

        self.fill_with_defaults()

    def fill_with_defaults(self):
        for db in ["users", "boards", "posts", "log", "comments"]:
            tmp_conn  = sqlite3.connect(f'db/bb.db3')

            c = tmp_conn.cursor()
            if db == "users":
                # Create table
                c.execute(f"""insert into users
                    values (0, 'admin', '{cryptography.get_hashed_password('admin').decode('utf-8')}', 'admin@pybb.net', {datetime.utcnow().strftime('%Y%m%d')}, 1)""")
            elif db == "log":
                c.execute(f"""insert into log
                    values ({datetime.utcnow().strftime('%Y%m%d')}, {datetime.utcnow().strftime('%H%M%S')}, 'Created database files and populated them with tables.')""")
            elif db == "boards":
                c.execute("""insert into boards
                    values (1, 'General', 'General discussion', '')""")
            elif db == "posts":
                #Get total amount of posts, so we can give a post ID to this post.
                c.execute("select count(*) from posts")
                postid = c.fetchone()[0]+1
                c.execute(f"""insert into posts
                    values (1, {postid}, 'Welcome to PyBB', 'Welcome to PyBB. This is a test post.', 0, {datetime.utcnow().strftime('%Y%m%d')}, {datetime.utcnow().strftime('%H%M%S')})""")
            elif db == "comments":
                c.execute(f"""insert into comments
                    values (1, 1, 'This is a test comment.', 0, "admin", {datetime.utcnow().strftime('%Y%m%d')}, {datetime.utcnow().strftime('%H%M%S')})""")

            tmp_conn.commit()
            c.close()
            tmp_conn.close()

if __name__ == "__main__":
    c = Configure()
    db = DB(c.get_config())
    db.write_log("Test log message.")
    print(db.get_boards())
    print(db.get_posts_from_board(1))
    db.create_board(2, "Test", "Test board", "")
    for i in range(0,100):
        db.create_post(2, f"Test post {i}", f"Test post content {i}", 0)

    for i in range(1,101):
        for j in range(0,10):
            db.create_comment(i, f"Test comment {j}", 0, "admin")
    print(db.get_boards())
    print(db.get_posts_from_board(2))