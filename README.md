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
If you are having problems with installing npm, or installing Node.js, try typing the following lines into the command line:

    echo 'export PATH=$HOME/local/bin:$PATH' >> ~/.bashrc
    . ~/.bashrc
    mkdir ~/local
    mkdir ~/node-latest-install
    cd ~/node-latest-install
    curl http://nodejs.org/dist/node-latest.tar.gz | tar xz --strip-components=1
    ./configure --prefix=~/local
    make install  #This will take a couple minutes to run
    curl https://npmjs.org/install.sh | sh

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

### Install and Run Redis
In addition to the Python modules, redis is also a required install for this project.

- redis ( http://redis.io/download )

If it is installed this way, run redis from the installation directory with

    src/redis-server

Or, if you feel comfortable with the command line:

    sudo apt-get install redis-server

Then just run

    redis-server

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
    python keep_backend/manage.py syncdb
    python keep_backend/manage.py migrate
    fab restore_db

After running these commands, there should be a sqlite file at ./local.db and a mongodb database
most likely at either /data/db/ or /var/lib/mongodb/.  The mongo database might not be located
at either location, check the --dbpath in the mongodb.conf file for the general location.

**Note:** on a syncdb command, Django will ask you to create a superuser.  Create one, and use these as your login credentials for the Logging in portion.

### All Server Prereqs
All the following must be running before starting the server:

    mongod
    redis-server
    python manage.py celeryd worker -E

If you are editing any static, coffeescript, or javascript files, the following should also be
running:

    grunt build

### Running the Django server
    python keep_backend/manage.py runserver

### Logging In
You may now log in to the system using the following credentials.

**Username:** admin

**Password:** test

# License

Keep is licensed under the terms of the [MIT License](LICENSE.txt)

