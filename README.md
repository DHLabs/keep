# Keep

Keep is a general purpose platform that is designed to facilitate data collection and analysis while providing a robust API to support its use in other mediums.

## Forms

The data collection is defined through forms.  The form structure itself is based on [XForms](https://en.wikipedia.org/wiki/XForms).  Specifically, the OpenRosa subset.  While xforms are originally an xml specification, there is now a JSON representation for them, and both formats are available for use through our API. XForms can created using XLS documents as well with our system.  need documentation of JSON Form)

XForm Documentation:

- [Form Design](http://opendatakit.org/help/form-design/)
- [Building XForms](https://bitbucket.org/javarosa/javarosa/wiki/buildxforms)
- [XForm Binding](http://opendatakit.org/help/form-design/binding/)

XLSForm Documentation:

- [XLSForm Overview](http://formhub.org/syntax/)
- [XLSForm Standard](https://docs.google.com/spreadsheet/ccc?key=0AgpC5gsTSm_4dDRVOEprRkVuSFZUWTlvclJ6UFRvdFE#gid=0)

# Getting Started

# Setting Up Your Dev Environment
Make sure the following dependencies are installed:

- MongoDB ( http://www.mongodb.org )
- MySQL ( http://www.mysql.com )
- Python 2.7 ( http://www.python.org )

## Frontend Dev Environment
**You must setup Frontend Dev even if you're only doing backend development.**
The Front-end development environment will set up the resources needed to compile
and minify your frontend assets. To correctly ensure that you have a working local
development environment, follow these instructions:

### Install Ruby & RubyGems
After installing Ruby, run the following command to install the first set of
front-end dependencies.

    gem update --system && gem install compass

### Install Node.js requirements
Make sure you are in the root of the project where the package.json file is located.

    npm install

### Alternative npm and Node.js Installation
If you are having problems with installing npm, or installing Node.js, try one of these alternatives: [https://gist.github.com/isaacs/579814](https://gist.github.com/isaacs/579814).

### Install Javascript/CSS dependencies
Next we make sure bower ( a javascript/css package manager ) is installed and
accessible globally. You may need admin access to install globally.

    (sudo) npm install -g bower
    bower install

### Build Front-End
Finally, we used the tools we have just installed to build our javascript/css
files. When the build task is completed, grunt will watch for changes in the
frontend directory and rebuild when necessary.

    grunt build

## Backend Dev Environment
Make sure you have the following Python modules installed:

- pip ( http://pypi.python.org/pypi/pip )
- virtualenv ( http://pypi.python.org/pypi/virtualenv )
- virtualenvwrapper ( http://www.doughellmann.com/projects/virtualenvwrapper )

Ensure that virtualenvwrapper is correctly setup. You should be able to run
mkvirtualenv_help from the command line.

### Create your development workspace
    mkvirtualenv dhlab_backend
    pip install -r deps.txt

### Initializing Submodules
    git submodule init
    git submodule update

### Startup MongoDB
Run mongod to ensure MongoDB is running

    mongod

### Setting up the Databases
    python dhlab_backend/manage.py syncdb
    python dhlab_backend/manage.py migrate
    fab restore_db

**Note:** on a syncdb command, Django will ask you to create a superuser.  If you create one, use that username and password to log in to your local KEEP, rather than the below credentials.

### Running the Django server
    python dhlab_backend/manage.py runserver

### Logging In
You may now log in to the system using the following credentials.

**Username:** admin

**Password:** test

# License

Keep is licensed under the terms of the [MIT License](LICENSE.txt)

