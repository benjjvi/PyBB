import bcrypt


def get_hashed_password(plain_text_password):
    # Hash a password for the first time
    #   (Using bcrypt, the salt is saved into the hash itself)
    return bcrypt.hashpw(plain_text_password.encode("utf-8"), bcrypt.gensalt())


def check_password(plain_text_password, hashed_password):
    # Check hashed password. Using bcrypt, the salt is saved into the hash itself
    return bcrypt.checkpw(plain_text_password.encode("utf-8"), hashed_password)


if __name__ == "__main__":
    x = get_hashed_password("sagetodz")
    print(check_password("sagetodz", x))
    print(check_password("todzsage", x))
    print(check_password("not_the_password", x))

    x = x.decode("utf-8")
    x = x.encode("utf-8")

    print(check_password("sagetodz", x))
    print(check_password("todzsage", x))
    print(check_password("not_the_password", x))
