from flask import Flask, render_template, request
import BulletinDatabaseModule

app = Flask(__name__)
Config = BulletinDatabaseModule.Configure()
Database = BulletinDatabaseModule.DB(Config.get_config())

@app.route("/")
def home():
    # Get the boards from the database:
    boards = Database.get_boards()
    
    print(boards)
    # Render the home page, with the boards:
    return render_template("home.html", boards=boards)


#Using args

#@app.route('/my-route')
#def my_route():
#  page = request.args.get('page', default = 1, type = int)
#  filter = request.args.get('filter', default = '*', type = str)
#/my-route?page=34               -> page: 34  filter: '*'
#/my-route                       -> page:  1  filter: '*'
#/my-route?page=10&filter=test   -> page: 10  filter: 'test'
#/my-route?page=10&filter=10     -> page: 10  filter: '10'
#/my-route?page=*&filter=*       -> page:  1  filter: '*'

@app.route("/board")
def boardView():
    boardID = request.args.get('board', default = 1, type = int)
    pageID= request.args.get('page', default = 1, type = int)

    # Get the board information:
    boardInfo = Database.get_board_info(boardID)

    # Get the posts from the board:
    posts = Database.get_posts_from_board(boardID)

    # Reduce the list to 15 items (starting from the index specified by pageID).
    posts = posts[(pageID-1)*15:pageID*15]

    # Get the number of pages:
    numberOfPages = len(Database.get_posts_from_board(boardID))//15+1

    #debugging
    print(f"boardID: {boardID}")
    print(f"pageID: {pageID}")
    print(f"boardInfo: {boardInfo}")
    print(f"posts: {posts}")
    print(f"numberOfPages: {numberOfPages}")

    print(f"Type of boardID: {type(boardID)}")
    print(f"Type of pageID: {type(pageID)}")
    print(f"Type of boardInfo: {type(boardInfo)}")
    print(f"Type of posts: {type(posts)}")
    print(f"Type of numberOfPages: {type(numberOfPages)}")

    print(f"Type of index0 of boardInfo: {type(boardInfo[0])}")
    print(f"Type of index0 of posts: {type(posts[0])}")

    print(f"Length of boardInfo: {len(boardInfo)}")
    print(f"Length of posts: {len(posts)}")

    print("==============")
    for post in posts:
        print(post)
    print("==============")

    return render_template("board.html", title=boardInfo[0][1], description=boardInfo[0][2], posts=posts, numberOfPages=numberOfPages, boardID=boardID, pageID=pageID)

@app.route("/post")
def postView():
    # Get the post ID from the URL:
    postID = request.args.get('postid', default = 1, type = int)

    # Get the post information:
    postInfo = Database.get_post_info(postID)

    # Get the comments from the post:
    comments = Database.get_comments_from_post(postID)

    #debugging
    print(f"postID: {postID}")
    print(f"postInfo: {postInfo}")
    print(f"comments: {comments}")

    return render_template("post.html", post=postInfo, comments=comments)


if __name__ == "__main__":
    app.run(debug=True)