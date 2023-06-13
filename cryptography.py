import secrets
import time

import bcrypt


def get_hashed_password(plain_text_password):
    # Hash a password for the first time
    #   (Using bcrypt, the salt is saved into the hash itself)
    return bcrypt.hashpw(plain_text_password.encode("utf-8"), bcrypt.gensalt())


def check_password(plain_text_password, hashed_password):
    # Check hashed password. Using bcrypt, the salt is saved into the hash itself
    return bcrypt.checkpw(plain_text_password.encode("utf-8"), hashed_password.encode("utf-8"))


def make_token():
    return secrets.token_urlsafe(64)


def lookup_session_token(session_token):
    # The sessions are all stored in a file that follows the structure sessionid:userid:expiry, and each entry is separated by a \n.

    # Open the file:
    try:
        with open("db/sessions", "r") as f:
            sessions = f.read().split("\n")
    except Exception:
        with open("db/sessions", "w") as f:
            f.write("")
            return None

    while "\n" in sessions:
        sessions.remove("\n")

    # Loop through the sessions:
    for session in sessions:
        # Split the session:
        session = session.split(":")

        # Check if the session token matches:
        if session[0] == session_token:
            # Check if the session has expired:
            if float(session[2]) < time.time():
                # Delete the session:
                session = f"{session[0]}:{session[1]}:{session[2]}"
                sessions.remove(session)

                # Write the new sessions to the file:
                with open("db/sessions", "w") as f:
                    f.write("\n".join(sessions))

                # Return None:
                return None

            # Return the user ID:
            return session[1]

    return None


def create_session(userid):
    token = make_token()
    session = f"{token}:{userid}:{round(time.time() + 60 * 60 * 2)}"

    with open("db/sessions", "a") as f:
        f.write(session + "\n")

    return token


# if __name__ == "__main__":
# a = get_hashed_password("sagetodz")
# b = get_hashed_password("sagetodz")
# c = get_hashed_password("sagetodz")

# print(a)
# print(b)
# print(c)

# print(check_password("sagetodz", a))
# print(check_password("sagetodz", b))
# print(check_password("sagetodz", c))

# x = get_hashed_password("sagetodz")

# print(check_password("sagetodz", x))
# print(check_password("todzsage", x))
# print(check_password("not_the_password", x))

# x = x.decode("utf-8")
# x = x.encode("utf-8")

# print(check_password("sagetodz", x))
# print(check_password("todzsage", x))
# print(check_password("not_the_password", x))

# x = create_session("aaaaba")
# a = lookup_session_token("9FBjBUeWgf0rXcTe3TBN53Kkhg4bG3ZDCbyhht8b1H8NpSlmzkgezL54kgYZuD_wQZfipb8QYrPO8z-FBBTu8Q")
# print(a)
