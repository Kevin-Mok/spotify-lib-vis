1. Use the pip tool to install `virtualenv`

    [Guide](http://docs.python-guide.org/en/latest/dev/virtualenvs/)

2. Create a virtual environment in an empty directory: 

    `virtualenv -p <path to python3 executable> <path to empty directory>`

3. cd into the directory you just created a virtual environment in, and clone our GitHub repo

4. Activate the virtual environment from the command line

    `source bin/activate`

5. cd into the repository root directory, install all dependencies using pip

    `pip -r requirements.txt`

6. Run Django migrations

    `python manage.py migrate`

7. Start the server

    `python manage.py runserver`


