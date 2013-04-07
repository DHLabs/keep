from __future__ import with_statement

from fabric.api import local, cd, env, run
from fabric.colors import green

env.use_ssh_config = True
env.user = 'ubuntu'
env.hosts = [ 'dhlab-backend' ]

PRODUCTION_DIR = 'dhlab-backend'


def backup_db():
    '''Backup local MongoDB database'''
    local( 'mongodump -d dhlab -o _data/dhlab-backup' )


def restore_db():
    '''Restore MongoDB database from backup. DELETES DATA'''
    local( 'mongorestore --drop _data/dhlab-backup' )


def clean():
    '''Clean up project directory.'''
    local( "find . -name '*.pyc' -delete" )


def deploy():
    '''Deploy the backend to the server'''
    print green( 'Deploy to EC2 instance...' )
    with cd( PRODUCTION_DIR ):
        # Stop all running processes
        run( 'supervisorctl stop all' )

        # Pull latest code from git
        run( 'git pull origin master' )

        # Start up all processes again
        run( 'supervisorctl start all' )
