import celery
import csv

from celery import current_task
from celery.utils.log import get_task_logger

from django.conf import settings
from django.core.files.storage import default_storage as storage

from pyxform.xls2json import SurveyReader
from openrosa.xform_reader import XFormReader

from api.serializers import CSVSerializer
from repos.models import Repository

logger = get_task_logger( __name__ )


@celery.task( default_retry_delay=5*60, max_retries=10 )
def create_repo_from_file( file, file_type, repo ):
    '''
        In this case the file will be turned into an entire repo. The headers
        will be used as the "fields" for this repo and then if there is data
        after the header, the data is added to the repo.

        Params
        ------
        file : string
            This points to a temporary file in our S3 bucket

        repo : string
            This is the mongo_id of the repo that we will modify.
    '''

    logger.info( 'Processing file %s for repo %s' % ( file, repo ) )

    repo = Repository.objects.get( mongo_id=repo )

    # Change the bucket we're checking
    if not settings.DEBUG and not settings.TESTING:
        storage.bucket_name = settings.AWS_TASK_STORAGE_BUCKET_NAME

    if not storage.exists( file ):
        try:
            raise Exception( 'File %s doesn\'t exist' % ( file ) )
        except Exception as exc:
            create_repo_from_file.retry( exc=exc )

    if file_type == 'csv':

        # Parse CSV headers & data
        serializer = CSVSerializer()
        fields, data = serializer.from_csv( storage.open( file, 'r' ) )

        # Modify repo's fields.
        repo.update_fields( fields )

        # If the study doesn't already have a tracker, assign the first field
        # of the repo to be the tracker name
        if repo.study and len( repo.study.tracker ) == 0:
            repo.study.tracker = fields[ 0 ].get( 'name' )
            repo.study.save()

        # Add data to repo
        for datum in data:
            repo.add_data( data=datum, files=None )

    elif file_type == 'xml':
        # This should be an xform.
        xform = storage.open( file, 'r' )
        fields = XFormReader( xform )
        fields = fields.to_json_dict()

        repo.update_fields( fields.get( 'children' ) )

    elif file_type == 'xls':
        # This should be an xform.
        xform = storage.open( file, 'r' )
        fields = SurveyReader( xform )
        fields = fields.to_json_dict()

        valid_tracker_field = True if repo.study and repo.study.tracker != '' else False

        # if this repo is a registry, add tracker field as the second question
        # (calculate fields can't be the first field)
        if repo.is_tracker:

            # If new repo is a tracker repo, and the study does not currently
            # have a tracker repo/registry, set this repo as the registry.
            if repo.study.tracker == '':
                repo.study.tracker = 'id'
                repo.study.save()

            fields['children'].insert( 1, {
                    'type':'calculate',
                    'name': repo.study.tracker,
                    'label': repo.study.tracker,
                } )

        # if this repo is not a registry but part of a study with tracked
        # objects, add a tracking field to the form.
        elif not repo.is_tracker and valid_tracker_field:
            fields['children'].insert( 0, {
                    'type':'text',
                    'name':repo.study.tracker,
                    'label':repo.study.tracker,
                } )

        repo.update_fields( fields.get( 'children' ) )

    # Remove the task from our list of "tasks"
    repo.remove_task( current_task.request.id )

    # Finally, remove the file from our S3
    logger.info( 'Processing complete. Removing file %s' % ( file ) )
    storage.delete( file )

    return True


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
    storage.bucket_name = settings.AWS_TASK_STORAGE_BUCKET_NAME
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
