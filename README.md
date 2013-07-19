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

### Install Javascript/CSS dependencies
Next we make sure bower ( a javascript/css package manager ) is installed and 
accessible globally. You may need admin access to install globally.

    (sudo) npm install -g bower
    bower install
    
### Build Front-End
Finally, we used the tools we have just installed to build our javascript/css
files.

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
    fab restore_db

### Running the Django server
    python dhlab_backend/manage.py runserver

### Logging In
You may now log in to the system using the following credentials.

**Username:** admin

**Password:** test

