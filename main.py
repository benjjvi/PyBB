from datetime import datetime

from flask import Flask, make_response, redirect, render_template, request

import BulletinDatabaseModule
import cryptography
import re
import captcha_module

app = Flask(__name__)
Config = BulletinDatabaseModule.Configure()
Database = BulletinDatabaseModule.DB(Config.get_config())

# Note for logging:
# To get the client's IP address, we use request.environ['REMOTE_ADDR'].
# To log to the database, we use Database.write_log(f"{request.environ['REMOTE_ADDR']}").

def generate_register(error):
    session_token = request.cookies.get("session_token")
    loggedInUsername = (
        Database.get_username_from_user_id(cryptography.lookup_session_token(session_token))
        if session_token is not None
        else None
    )

    if loggedInUsername != None:
        return redirect("/")

    # Get Captcha
    captcha = captcha_module.create_audio_and_image_captcha()

    captchaAnswer = captcha.split(":")[0]
    captchaHash = captcha.split(":")[1]

    audiocaptcha = f'captchas/{captchaAnswer}.wav'
    imagecaptcha = f'captchas/{captchaAnswer}.png'

    
    resp = make_response(render_template("register.html", audiocaptcha=audiocaptcha, imagecaptcha=imagecaptcha, username=loggedInUsername, error=error))
    resp.set_cookie("captcha", captchaHash)
    return resp

@app.route("/")
def home():
    session_token = request.cookies.get("session_token")
    loggedInUsername = (
        Database.get_username_from_user_id(cryptography.lookup_session_token(session_token))
        if session_token is not None
        else None
    )

    # Get the boards from the database:
    boards = Database.get_boards()

    # Write to the log:
    Database.write_log(
        f"Request to home page from {request.environ['REMOTE_ADDR']} with user token {session_token}.",
        request.environ["REMOTE_ADDR"],
    )

    # resp = make_response(render_template(
    #     "home.html",
    #     title=Config.get_config()["title"],
    #     description=Config.get_config()["short_description"],
    #     boards=boards,
    # ))
    # resp.set_cookie('userID', "test", max_age=2*60*60)

    # Render the home page, with the boards:
    return render_template(
        "home.html",
        title=Config.get_config()["title"],
        description=Config.get_config()["short_description"],
        boards=boards,
        username=loggedInUsername,
    )


@app.route("/about")
def about():
    session_token = request.cookies.get("session_token")
    loggedInUsername = (
        Database.get_username_from_user_id(cryptography.lookup_session_token(session_token))
        if session_token is not None
        else None
    )

    # Write to the log:
    Database.write_log(
        f"Request to about page from {request.environ['REMOTE_ADDR']} with user token {session_token}.",
        f"{request.environ['REMOTE_ADDR']}",
    )

    return render_template(
        "about.html",
        description=Config.get_config()["long_description"].split("<br>"),
        username=loggedInUsername,
    )


@app.template_filter("date")
def date_filter(s):
    return datetime.utcnow().strftime("%Y")


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
    session_token = request.cookies.get("session_token")
    loggedInUsername = (
        Database.get_username_from_user_id(cryptography.lookup_session_token(session_token))
        if session_token is not None
        else None
    )

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
    Database.write_log(
        f"Request to board page with id {boardID} and page with ID {pageID} from {request.environ['REMOTE_ADDR']} with user token {session_token}.",
        f"{request.environ['REMOTE_ADDR']}",
    )

    return render_template(
        "board.html",
        title=boardInfo[0][1],
        description=boardInfo[0][2],
        posts=posts,
        numberOfPages=numberOfPages,
        boardID=boardID,
        pageID=pageID,
        username=loggedInUsername,
    )


@app.route("/post")
def postView():
    session_token = request.cookies.get("session_token")
    loggedInUsername = (
        Database.get_username_from_user_id(cryptography.lookup_session_token(session_token))
        if session_token is not None
        else None
    )

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
    Database.write_log(
        f"Request to post page with id {postID} from {request.environ['REMOTE_ADDR']} with user token {session_token}.",
        f"{request.environ['REMOTE_ADDR']}",
    )

    return render_template(
        "post.html",
        user=userInfo,
        post=postInfo,
        comments=comments,
        username=loggedInUsername,
    )

@app.route("/loginuser", methods=["POST"])
def loginuser():
    # Get the username and password from the form:
    username = request.form["username"]
    password = request.form["password"]

    # Get the session token, to check if it already exists:
    session_token = request.cookies.get("session_token")
    loggedInUsername = (
        Database.get_username_from_user_id(cryptography.lookup_session_token(session_token))
        if session_token is not None
        else None
    )

    # If the session token exists, we can redirect to the home page:
    if loggedInUsername is not None:
        return redirect("/")

    # Check if the username and password are correct:
    if len(Database.check_user_credentials(username, password)) != 0:
        try:
            # If they are, generate a session token:
            uid = Database.get_user_id_from_username(username)

            if uid == None:
                raise Exception("User ID is None.")
            else:
                Database.write_log(f"INFO: User {username} logged in.", request.environ["REMOTE_ADDR"])
                session_token = cryptography.create_session(uid)
                # And set the cookie:
                resp = make_response(redirect("/"))
                resp.set_cookie("session_token", session_token)
                return resp
        except Exception:
            # Write a log to the log.
            Database.write_log(f"ERROR: User {username} tried logging in, but upon searching for userid, {Database.get_user_id_from_username(username)} was recieved.", request.environ["REMOTE_ADDR"])
    else:
        # If they aren't, redirect to the login page, with an error message passed through as error:
        Database.write_log(f"WARN: User {username} tried logging in with password {password}, but the credentials were incorrect.", request.environ["REMOTE_ADDR"])
        return render_template("login.html", username=loggedInUsername, error="Incorrect username or password.")


@app.route("/login")
def login():
    session_token = request.cookies.get("session_token")
    loggedInUsername = (
        Database.get_username_from_user_id(cryptography.lookup_session_token(session_token))
        if session_token is not None
        else None
    )

    if loggedInUsername is None: 
        return render_template("login.html", username=loggedInUsername, error=None)
    else:
        return redirect("/")


@app.route("/logout")
def logout():
    resp = make_response(redirect('/'))
    resp.set_cookie('session_token', '', expires=0)
    return resp



@app.route("/createaccount", methods=["POST"])
def create_account():
    username = request.form["username"]
    email = request.form["email"]
    password = request.form["pwd"]
    password_confirmed = request.form["pwd-confirm"]
    captchaHash = request.cookies.get("captcha")
    captchaResponse = request.form["captcha"]

    # First, check the username is not already in database.
    if Database.get_user_id_from_username(username) != None:
        return generate_register("Username already exists.")
    
    # Next, check the email is not already in database.
    if Database.get_user_id_from_email(email) != None:
        return generate_register("Email already exists.")
    
    # Next, let's check if the email is in the xxx@xxx.xxx format using regex.
    if re.match(r"[^@]+@[^@]+\.[^@]+", email) == None:
        return generate_register("Email is not in the correct format.")
    
    # Next, check the passwords match.
    if password != password_confirmed:
        return generate_register("Passwords do not match.")
    
    # Next, check password is at least 8 characters long with at least one number, one letter, and one special character.
    if re.match(r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$", password) == None:
        return generate_register("Password is not in the correct format. You must have at least 8 characters, of which having one number, one letter, and one special character.")
    
    # Next, check the captcha is correct.
    if captcha_module.check_captcha(captchaHash, captchaResponse) == False:
        return generate_register("Captcha is incorrect.")
    
    # If all of these checks pass, we can create the account.
    # To do this, we can use the create_user() function from the database module.
    # This function takes in the username, email, and password, and returns the user ID.
    # We can then use this user ID to create a session token, and set the cookie.
    uid = Database.create_user(username, email, password)
    session_token = cryptography.create_session(uid)
    resp = make_response(redirect("/"))
    resp.set_cookie("session_token", session_token)
    return resp


@app.route("/register")
def register():
    session_token = request.cookies.get("session_token")
    loggedInUsername = (
        Database.get_username_from_user_id(cryptography.lookup_session_token(session_token))
        if session_token is not None
        else None
    )

    if loggedInUsername != None:
        return redirect("/")

    # Get Captcha
    captcha = captcha_module.create_audio_and_image_captcha()

    captchaAnswer = captcha.split(":")[0]
    captchaHash = captcha.split(":")[1]

    audiocaptcha = f'captchas/{captchaAnswer}.wav'
    imagecaptcha = f'captchas/{captchaAnswer}.png'

    
    resp = make_response(render_template("register.html", audiocaptcha=audiocaptcha, imagecaptcha=imagecaptcha, username=loggedInUsername, error=None))
    resp.set_cookie("captcha", captchaHash)
    return resp




if __name__ == "__main__":
    app.run(debug=True)
