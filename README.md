# Installing Dependencies

Make sure the following dependencies are installed:

- MongoDB ( http://www.mongodb.org )
- MySQL ( http://www.mysql.com )
- Python 2.7 ( http://www.python.org )


# Setting up your Python Dev Environment


Make sure you have the following Python modules installed:

- pip ( http://pypi.python.org/pypi/pip )
- virtualenv ( http://pypi.python.org/pypi/virtualenv )
- virtualenvwrapper ( http://www.doughellmann.com/projects/virtualenvwrapper )

Ensure that virtualenvwrapper is correctly setup. You should be able to run mkvirtualenv_help from the command line.


## Create your development workspace

    mkvirtualenv dhlab_backend
    pip install -r deps.txt


## Setting up the Databases

    python manage syncdb
    fab restore_db

## Running the Django server

    python manage runserver

# Setting up Two Factor Authentication

Download the Google Authenticator app on your smartphone.

Scan the following barcode:
![2FA Token](https://chart.googleapis.com/chart?chl=otpauth%3A%2F%2Ftotp%2Fadmin%40DHLab%3Fsecret%3DNTSRUTMVFKM44XTW&chs=200x200&cht=qr&chld=M%7C0)


