### Install dependencies for Python

```
sudo apt-get install python-dev libjpeg8-dev python3-dev libpq-dev
```

### Setup

1. Install [PostgreSQL](https://help.ubuntu.com/community/PostgreSQL#Installation)
2. Create a [user](https://help.ubuntu.com/community/PostgreSQL#Alternative_Server_Setup) with superuser role
3. `createdb mystery_shopping`
4. [Install](https://github.com/yyuu/pyenv-installer) `pyenv` for installing the appropriate python version
5. `pyenv install 3.4.3` *the python version running on production server*
6. [Install](https://virtualenvwrapper.readthedocs.io/en/latest/) `virtualenvwrapper`
7. Create the project virtualenv `mkvirtualenv --python=$(pyenv global 3.4.3 && pyenv which python) mystery_venv`
8. `workon mystery_venv` to load the newly added variables
9. `git clone git@github.com:SparkResearchLabs/MysteryShopping.git`
10. `cd MysteryShopping`
11. `pip install -r requirements/local.txt`
12. `python manage.py test` Try to fix the test errors if any occur
13. `python manage.py createsuperuser`
14. `python manage.py migrate` Make migration
14. `python manage.py runserver`

If the server is up and running you're golden and can start working.
