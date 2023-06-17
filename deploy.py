# gunicorn --certfile=server.crt --keyfile=server.key --bind 0.0.0.0:443 main:app

x = {
    "host": "0.0.0.0",
    "port": 5001,
    "use-https": 1,
    "https": {
        "certfile": "./cert.cer",
        "keyfile": "./cert.key",
    }
}

import os
import ast

# Read config file
conf = {}
try:
    with open('pybb.conf') as f:
        conf = ast.literal_eval(f.read())["wsgi"]
except Exception:
    exit('Error: pybb.conf not found')

# Get variables
host = conf["host"]
port = conf["port"]
use_https = conf["use-https"]
https_certfile = conf["https"]["certfile"]
https_keyfile = conf["https"]["keyfile"]
workers = conf["workers"]

# If not using https, we don't need to pass through keyfile and certfiles.
if not use_https:
    del https_certfile
    del https_keyfile
    os.system(f"gunicorn --bind {host}:{port} --workers {workers} --timeout 100 --log-level info --access-logfile access.log main:app")
else:
    os.system(f"gunicorn --certfile={https_certfile} --workers {workers} --timeout 100 --log-level info --access-logfile access.log --keyfile={https_keyfile} --bind {host}:{port} main:app")