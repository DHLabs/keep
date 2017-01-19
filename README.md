# KEEP (unmaintained)

:construction: *This project is no longer maintained.* :construction:

Keep is a general purpose platform that is designed to facilitate data
collection and analysis while providing a robust API to support its use in
other mediums. Put simply, Keep allows you to create forms, collect data, and
then share it.

### Features:

- Open-source, MIT licensed
- Store data in the cloud, access anywhere
- Build web-forms with branching and constraint logic
- Build forms that support multiple languages
- Use 2-factor authentication to secure your account
- Plot data on maps
- Share data with other users
- Provides API access to data
- Mobile-friendly
- [iOS][ios] and [Android][android] applications

[ios]: https://github.com/DHLabs/Keep_iOS
[android]: https://github.com/DHLabs/Keep_Android


## Tech Overview

The Keep repository consists of the main keep backend, as well as the front-end
web client. The backend is built on [Django][dj], a [Python][py] web framework.
Data is stored in MongoDB, while MySQL is used for user data and permissions.
Celery + Redis serve as the task queue. The front-end is built with
[Coffeescript][cs], [Sass][sass], and [BackboneJS][bb]. Additional technical
details are found in READMEs within directories.

[py]: https://www.python.org/
[dj]: https://www.djangoproject.com/
[bb]: http://backbonejs.org/
[cs]: http://coffeescript.org/
[sass]: http://sass-lang.com/

## Forms

While Keep provides a web-form builder, forms can also be built with
spreadsheet tools by using the XLSForm format. [XLSForm][xlsform] is based off
of [XForms][xform], a W3C standard for forms. These XLSForms can be uploaded to
Keep to generate web forms/repositories.

[XLSForm Documentation][xlsform]

[xform]: https://en.wikipedia.org/wiki/XForms
[xlsform]: http://xlsform.org/

## License

Keep is licensed under the terms of the [MIT License](LICENSE.txt)

---

# Getting Started

The following are instructions for setting up the keep backend server and web
client in a development environment.

## Install dependencies

Make sure the following dependencies are installed:

- MongoDB ( http://www.mongodb.org )
- MySQL ( http://www.mysql.com )
- Python 2.7 ( http://www.python.org )
- NodeJS/NPM ( https://nodejs.org/en/ )
- Redis ( http://redis.io/download )

Make sure you have the following Python modules installed:

- pip ( http://pypi.python.org/pypi/pip )
- virtualenv ( http://pypi.python.org/pypi/virtualenv )
- virtualenvwrapper ( http://www.doughellmann.com/projects/virtualenvwrapper )

## Create your development workspace

    mkvirtualenv dhlab_backend
    pip install -r deps.txt

## Initialize submodules

    git submodule init
    git submodule update

## Start services

All of the following must be running before starting the server:

    mongod
    redis-server
    python manage.py celeryd worker -E

## Set up databases

    python keep_backend/manage.py syncdb
    python keep_backend/manage.py migrate

After running these commands, there should be a sqlite file at ./local.db and a
mongodb database most likely at either /data/db/ or /var/lib/mongodb/.  The
mongo database might not be located at either location, check the --dbpath in
the mongodb.conf file for the general location.

**Note:** on an initial syncdb command, Django will ask you to create a
superuser. Create one, and use these as your login credentials for the logging
in portion.

## Install front-end dependencies

    npm install

## Build front-end assets

    grunt build

`grunt build` will continue to watch the front-end source files so any changes
that are made should cause the assets to be re-built.

## Run the Django server

    python keep_backend/manage.py runserver

## Log in

Navigate to `http://localhost:8000/`. You should see the Keep home page as well
as a login button. You should be able to log in with the super user account or
register a new account. Two-factor authentication is disabled in the
development environment. If registering a new account on development, the
confirmation email should appear in the server console output.
