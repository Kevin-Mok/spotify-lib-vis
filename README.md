# Spotify Data Visualizer

See charts of the artists, genres and features of tracks in your library. Also keep track of your listening history.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

Before starting the setup, make sure Python 3.6 and PostgreSQL is installed on your system.

<!---  installation steps {{{ --> 

### Installing

1. Use the pip tool to install `virtualenv`. See this [guide](http://docs.python-guide.org/en/latest/dev/virtualenvs/) for further details.

```
pip install --user pipenv
```

2. Create a virtual environment.

```
python3 -m venv /path/to/new/virtual/environment
```

3. `cd` into the directory you just created a virtual environment in, and clone the GitHub repo.

4. Activate the virtual environment from the command line.

```
source bin/activate
```

5. `cd` into the repository root directory and install all dependencies using `pip`.

```
pip install -r requirements.txt
```

6. Run Django migrations.

```
manage.py migrate
```

7. Start the server.

```
python manage.py runserver
```

<!---  }}} installation steps --> 

## Built With

* [Django](https://www.djangoproject.com/)
* [Spotify Web API](https://github.com/spotify/web-api)
* [pip packages used](requirements.txt)

## Authors

* [Kevin Mok](https://github.com/Kevin-Mok)
* [Chris Shyi](https://github.com/chrisshyi)

## License

This project is licensed under the GPL License - see the [LICENSE.md](LICENSE.md) file for details.
