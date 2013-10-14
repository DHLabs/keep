import celery
import csv

from celery import current_task
from celery.utils.log import get_task_logger

from django.core.files.storage import default_storage as storage

from repos.models import Repository

logger = get_task_logger( __name__ )


@celery.task
def create_repo_from_file( file, repo ):
    '''
        In this case the CSV file will be turned into an entire repo. The headers
        will be used as the "fields" for this repo and then if there is data
        after the header, the data is added to the repo.
    '''
    pass


@celery.task
def insert_csv_data( file, repo ):
    '''
        The upload_csv_data task will push an entire CSV to a repo if the headers
        match fields within the data repo.

        Params
        ------
        file : string
            This points to a temporary file in our S3 bucket.

        repo : string
            This is the mongo_id of the repo this data will be pushed into.
    '''

    logger.info( 'Processing file %s for repo %s' % ( file, repo ) )

    repo = Repository.objects.get( mongo_id=repo )

    # Change the bucket we're checking
    storage.bucket_name = 'keep-test'
    if not storage.exists( file ):
        raise Exception( 'File doesn\'t exist' )

    # Open the file and parse it baby! Any errors will be raised and captured
    # by the celery task for us to check later.
    csv_file = csv.reader( storage.open( file, 'r' ) )
    headers = csv_file.next()

    for row in csv_file:

        row_map = {}
        for idx, header in enumerate( headers ):
            row_map[ header ] = row[ idx ]

        repo.add_data( data=row_map, files=None )

    # Remove the task from our list of "tasks"
    repo.remove_task( current_task.request.id )

    # Finally, remove the file from our S3
    logger.info( 'Processing complete. Removing file %s' % ( file ) )
    storage.delete( file )

    # Push each row into the database.
    return True
