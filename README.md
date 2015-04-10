mgxrace
=======

MGXRace website and Racesow stats backend

Development Setup
-----------------

The MGXRace website runs on CPython and supports versions 2.7, 3.3 and 3.4. The
first step is to [fork] clone the repo and setup the virtual environment.

```bash
# Clone the Repository
$ git clone https://github.com/MGXRace/website
$ cd website

# Setup the virtual environment
$ virtualenv venv
$ source venv/bin/activate

# Install the dependencies
$ pip install -r requirements.txt
$ pip install -r dev-requirements.txt
```

Running the Development Server
------------------------------

Nothing special here, exactly the same as a standard Django project.

```bash
$ python manage.py migrate
$ python manage.py runserver
```

Running Tests
-------------

Tests are automated against all python versions with coverage reports using
tox. To run the tests, just use the `tox` command inside the website directory.
See the tox.ini file for a list of included testing enviroments and further
details.
