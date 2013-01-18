from fabric.api import local


def backup_db():
    '''Backup local MongoDB database'''
    local( 'mongodump -d dhlab -o _data/dhlab-backup' )


def restore_db():
    '''Restore MongoDB database from backup. DELETES DATA'''
    local( 'mongorestore --drop _data/dhlab-backup' )
