from flask import Flask, render_template, request
from datetime import datetime

import BulletinDatabaseModule

app = Flask(__name__)
Config = BulletinDatabaseModule.Configure()
Database = BulletinDatabaseModule.DB(Config.get_config())

# Note for logging:
# To get the client's IP address, we use request.environ['REMOTE_ADDR'].
# To log to the database, we use Database.write_log(f"{request.environ['REMOTE_ADDR']}").

@app.route("/")
def home():
    # Get the boards from the database:
    boards = Database.get_boards()

    # Write to the log:
    Database.write_log(f"Request to home page from {request.environ['REMOTE_ADDR']}.", request.environ['REMOTE_ADDR'])

    # Render the home page, with the boards:
    return render_template(
        "home.html",
        title=Config.get_config()["title"],
        description=Config.get_config()["short_description"],
        boards=boards,
    )

@app.route("/about")
def about():
    # Write to the log:
    Database.write_log(f"Request to about page from {request.environ['REMOTE_ADDR']}.", f"{request.environ['REMOTE_ADDR']}")

    return render_template(
        "about.html",
        description=Config.get_config()["long_description"].split("<br>"),
    )

@app.template_filter('date')
def date_filter(s):
    return datetime.utcnow().strftime('%Y')

# Using args

# @app.route('/my-route')
# def my_route():
#  page = request.args.get('page', default = 1, type = int)
#  filter = request.args.get('filter', default = '*', type = str)
# /my-route?page=34               -> page: 34  filter: '*'
# /my-route                       -> page:  1  filter: '*'
# /my-route?page=10&filter=test   -> page: 10  filter: 'test'
# /my-route?page=10&filter=10     -> page: 10  filter: '10'
# /my-route?page=*&filter=*       -> page:  1  filter: '*'


@app.route("/board")
def boardView():
    boardID = request.args.get("board", default=1, type=int)
    pageID = request.args.get("page", default=1, type=int)

    # Get the board information:
    boardInfo = Database.get_board_info(boardID)

    # Get the posts from the board:
    posts = Database.get_posts_from_board(boardID)

    # Reduce the list to 15 items (starting from the index specified by pageID).
    posts = posts[(pageID - 1) * 15 : pageID * 15]

    # Get the number of pages:
    numberOfPages = len(Database.get_posts_from_board(boardID)) // 15 + 1

    # Write to the log:
    Database.write_log(f"Request to board page with id {boardID} and page with ID {pageID} from {request.environ['REMOTE_ADDR']}.", f"{request.environ['REMOTE_ADDR']}")

    return render_template(
        "board.html",
        title=boardInfo[0][1],
        description=boardInfo[0][2],
        posts=posts,
        numberOfPages=numberOfPages,
        boardID=boardID,
        pageID=pageID,
    )


@app.route("/post")
def postView():
    # Get the post ID from the URL:
    postID = request.args.get("postid", default=1, type=int)

    # Get the post information:
    postInfo = Database.get_post_info(postID)

    # Get the comments from the post:
    comments = Database.get_comments_from_post(postID)

    # Get the user information:
    userInfo = Database.get_user_info(postInfo[4])

    # We need to turn postInfo from a tuple to a list.
    postInfo = list(postInfo)

    # We also need to turn each comment in the array to a list from a tuple.
    comments = [list(comment) for comment in comments]

    # We can handle turning the date from &Y&M&d in the postInfo[5] into a &d &M &Y format here.
    # We can also handle turning the date from &Y&M&d in the comments[5] into a &d &M &Y format here.
    postInfo[5] = datetime.strptime(str(postInfo[5]), "%Y%m%d").strftime("%d %B %Y")
    for comment in comments:
        comment[5] = datetime.strptime(str(comment[5]), "%Y%m%d").strftime("%d %B %Y")

    # We can also handle times here. Turn postInfo[6] and comments[6] into a 24 hour clock.
    postInfo[6] = datetime.strptime(str(postInfo[6]), "%H%M%S").strftime("%H:%M UTC")
    for comment in comments:
        comment[6] = datetime.strptime(str(comment[6]), "%H%M%S").strftime("%H:%M UTC")

    # We want to add a new index, 7, which will be the comment author's author profile.
    # To do this, we can use get_user_info() from the database module, feeding in index 3 of the comment.
    for comment in comments:
        commentAuthorInfo = Database.get_user_info(comment[3])
        commentAuthorInfo = list(commentAuthorInfo)
        comment.append(commentAuthorInfo)

    # Write to the log:
    Database.write_log(f"Request to post page with id {postID} from {request.environ['REMOTE_ADDR']}.", f"{request.environ['REMOTE_ADDR']}")

    return render_template("post.html", user=userInfo, post=postInfo, comments=comments)


if __name__ == "__main__":
    app.run(debug=True)
