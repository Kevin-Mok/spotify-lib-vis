Before starting the setup, make sure **Python 3.6** is installed on your system.

1. Use the pip tool to install `virtualenv`. (See this [guide](http://docs.python-guide.org/en/latest/dev/virtualenvs/) for further details.)

	`pip install --user pipenv`

2. Create a virtual environment.

    `python3 -m venv /path/to/new/virtual/environment`

3. `cd` into the directory you just created a virtual environment in, and clone the GitHub repo.

4. Activate the virtual environment from the command line.

    `source bin/activate`

5. `cd` into the repository root directory and install all dependencies using `pip`.

    `pip install -r requirements.txt`

6. Run Django migrations.

    `python manage.py migrate`

7. Start the server.

    `python manage.py runserver`
