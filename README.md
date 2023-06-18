# PyBB

An open source bulletin board, designed to run on the lowest end hardware.

## To Do List
1. Add the ability to customise the bulletin board.
2. Add an administration page.
3. General tidy up.

## Getting started with an example database.
### Step 1: Creating the database.
PyBB comes with an "example" database mode, that can be found by running "reset.sh" in a terminal. This will create the file "bb.db3" in the "db" folder. Feel free to poke around with a SQLite viewer, and take a look at the tables and values.

### Step 2: Modifying the configuration.
Taking a look at the configuration file can be a bit daunting, especially with some of the large values. That's why we have a small terminal program that can be run to create the configuration file for you! pybb.conf will be automatically generated at the time of creating the example database, if you are using the example data. Or, you can run the file named `configure.py` by typing `python3 configure.py` in your terminal, and run through all of the steps there.

### Step 3: Running your server!
Congratulations. After this short setup, you're ready to get your server started. Simply run `deploy.py`, and you'll be able to see your web server on your browser at the host/port you provided.
Just pop on over to your web browser, and input the IP of the machine you are connecting to (or DNS domain, if the server has been port-forwarded properly), as well as the port (which is not needed if you are using the default HTTP port 80 with http://, or the default HTTPS port 443 with https://). 