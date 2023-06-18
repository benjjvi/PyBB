import os
import re

print("Welcome to the PyBB configuration script.")
print("This script will help you configure your PyBB installation.")
print("If you would like to use the default value, simply press enter.")
print("If you would like to exit, press Ctrl+C.")
print("This will overwrite your existing pybb.conf file.")
print(
    "Text inside [] indicates the response we need, and text in () indicates the default value."
)
print("Please answer the following questions to continue.")
print()
print("Section 1: WSGI Configuration.")

# Get host
host = ""
# run a regex until host follows x.x.x.x pattern
while re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", host) is None:
    host = input(
        "What host interface would you like to run PyBB on? [x.x.x.x] (default: 0.0.0.0)\n> "
    )
    if host == "":
        host = "0.0.0.0"

# Get port
port = ""
# run a regex until port is a number between 1 and 65535
while re.match(r"^\d{1,5}$", port) is None or int(port) < 1 or int(port) > 65535:
    port = input(
        "What port would you like to run PyBB on? [1-65535] (default: 5001)\n> "
    )
    if port == "":
        port = "5001"

port = int(port)
if port < 1024 and port > 1:
    print(
        "Warning: ports below 1024 are reserved for system use. You may need to run deploy as an administrator to use these ports."
    )

# Get workers
workers = ""
# run a regex until workers is a number between 1 and 100
while re.match(r"^\d{1,3}$", workers) is None or int(workers) < 1 or int(workers) > 100:
    workers = input("How many workers would you like to run? [1-100] (default: 8)\n> ")
    if workers == "":
        workers = "8"

workers = int(workers)

# Get use-https
use_https = ""
# run a regex until use_https is 0 or 1
while use_https != 0 and use_https != 1:  # re.match(r"^[01]$", use_https) is None:
    use_https = input(
        "Would you like to use HTTPS? [0/1, where 0 is no, and 1 is yes.] (default: 0)\n> "
    )
    if use_https == "":
        use_https = 0
    else:
        use_https = int(use_https)

certfile = ""
keyfile = ""
self_sign = False
if use_https == 1:
    print(
        "PyBB gives you the option to use HTTPS. If you would like to use HTTPS, you can either provide a certificate and key, or we can generate a 'self-signed' certificate and key for you."
    )
    print(
        "If you would like to use your own certificate and key, please provide the path to the certificate and key files."
    )
    print(
        "If you would like to generate a self-signed certificate and key, please leave the certificate and key fields blank."
    )

    # run a regex until certfile is a valid UNIX path, or follows structure ./path.pem
    while re.match(r"^\.?\/?[\w\/\.]+$", certfile) is None:
        certfile = input(
            "What is the path to your certificate file? [path] (default: self-signage)\n> "
        )
        if certfile == "":
            self_sign = True
            break

    if not self_sign:
        # run a regex until keyfile is a valid UNIX path, or follows structure ./path.pem
        while re.match(r"^\.?\/?[\w\/\.]+$", keyfile) is None:
            keyfile = input(
                "What is the path to your key file? [path] (default: ./key.pem)\n> "
            )
            if keyfile == "":
                keyfile = "./key.pem"

if self_sign:
    print("Generating self-signed certificate and key...")
    os.system(
        "openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -sha256 -days 365 -nodes"
    )
    certfile = "./cert.pem"
    keyfile = "./key.pem"

print()
print("Section 2: Database Configuration.")
print()

title = ""
# run a regex until title is text of length 1-64
while re.match(r"^.{1,64}$", title) is None:
    title = input(
        "What is the title of your bulletin board? [text length 1-64] (default: PyBB)\n> "
    )
    if title == "":
        title = "PyBB"

short_description = ""
# run a regex until short_description is text of length 1-512
while re.match(r"^.{1,512}$", short_description) is None:
    short_description = input(
        "What is the short description of your bulletin board? [text length 1-512] (default: A Python Bulletin Board)\n> "
    )
    if short_description == "":
        short_description = "A Python Bulletin Board"

long_description = ""
# run a regex until long_description is text of length 1-8192
while re.match(r"^.{1,8192}$", long_description) is None:
    long_description = input(
        "What is the long description of your bulletin board? [text length 1-8192] (default: A Python Bulletin Board)\n> "
    )
    if long_description == "":
        long_description = "A Python Bulletin Board"

# Make a dictionary of this data.
data = {
    "wsgi": {
        "host": host,
        "port": int(port),
        "workers": workers,
        "use-https": int(use_https),
        "https": {"certfile": certfile, "keyfile": keyfile},
    },
    "app": {
        "title": title,
        "short_description": short_description,
        "long_description": long_description,
    },
}

# Write to file
with open("pybb.conf", "w") as f:
    f.write(str(data))

import os

os.system("mkdir db")
os.system("mkdir static/captchas")

# Now, import BulletinDatabaseModule.py and build.
import BulletinDatabaseModule as bdbm

c = bdbm.Configure()
c.create_tables()

print(
    "Configuration complete. You can now run deploy.py to deploy your PyBB installation."
)
