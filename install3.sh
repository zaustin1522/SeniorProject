#!/bin/bash


# Remove all prior migrations and load database with music data from the specified csv file

rm -f db.sqlite3 sharify/migrations/0*.py sharify/migrations/__pycache__/0*.pyc


# Initial migration ...
python3 manage.py makemigrations && python3 manage.py migrate
python3 manage.py makemigrations sharify && python3 manage.py migrate sharify



# Now load music data from the csv file into Django's database
# It will ask you for the music data file name

python3 manage.py shell -c "import importdata"

echo "*********************************************"
echo "If needed, now create a super user"

# Windows: Remove the # at the beginning of the line below
#$SHELL
