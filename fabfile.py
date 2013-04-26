from __future__ import with_statement

from fabric.api import local, cd, env, run
from fabric.colors import green

PRODUCTION_DIR  = 'backend'
PRODUCTION_SETTINGS = 'settings.production'

SUPERVISOR_NAME = 'dhlab_backend'

MONGODB_NAME    = 'dhlab'

env.use_ssh_config = True
env.user = 'ubuntu'
env.hosts = [ 'dhlab-backend' ]


def backup_db():
    '''Backup local MongoDB database'''
    local( 'mongodump -d %s -o _data/dhlab-backup' % ( MONGODB_NAME ) )


def restore_db():
    '''Restore MongoDB database from backup. DELETES DATA'''
    local( 'mongorestore --drop _data/dhlab-backup' )


def build_static():
    local( 'python dhlab_backend/manage.py collectstatic --settings="%s"' %
           ( PRODUCTION_SETTINGS ) )


def clean():
    '''Clean up project directory.'''
    local( "find . -name '*.pyc' -delete" )


def deploy():
    '''Deploy the backend to the server'''
    print green( 'Deploy to EC2 instance...' )
    with cd( PRODUCTION_DIR ):
        # Stop all running processes
        run( 'supervisorctl stop %s' % ( SUPERVISOR_NAME ) )

        # Pull latest code from git
        run( 'git pull origin master' )

        # Ensure we have the latest dependencies
        run( 'workon dhlab_backend' )
        run( 'pip install -r deps.txt' )

        # Start up all processes again
        run( 'supervisorctl start all' )


def test():
    print green( 'Running tests...' )
    local('coverage run dhlab_backend/manage.py test --settings=settings.test')

    print green( 'Generating coverage report...' )
    local( 'coverage html --omit="*.pyenvs*"' )
