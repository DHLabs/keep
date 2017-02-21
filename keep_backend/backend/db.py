from datetime import datetime
from bson import ObjectId

from django.conf import settings
from django.contrib.auth.models import User

from pymongo import MongoClient

from organizations.models import Organization

connection = MongoClient( settings.MONGODB_HOST, settings.MONGODB_PORT )
db = connection[ settings.MONGODB_DBNAME ]

RECURRING_FORMS = [
    'p03_daily_clinical_lab_data',
    'p04_new_illness',
]

class DataSerializer( object ):

    def dehydrate( self, data, repository, linked=None ):

        hydrated = []
        fields = repository.fields()
        for row in data:
            copy = dict( row )

            # Hydrate the base data keys.
            # 1. Remove the "repo" key if it exists.
            # 2. Rename the "_id" key into the more common "id" key.
            # 3. Convert the python timestamp into a JSON friendly one.
            repo = copy.pop( 'repo' )
            copy[ 'id' ] = str(copy.pop( '_id' ))
            copy[ 'timestamp' ] = copy[ 'timestamp' ].strftime( '%Y-%m-%dT%X' )

            # ISN Hack:
            # Options needed to determine form completeness
            opts = {
                'repo': repository,
                'linked': linked,
            }

            # Now serialize the data according to the field data.
            copy[ 'data' ] = self.serialize_data( data=copy[ 'data' ],
                                                  fields=fields,
                                                  repo_id=repo,
                                                  data_id=copy[ 'id' ],
                                                  options=opts)

            #if repository.is_tracker and repository.study and linked:
            #    link_dict = {}
            #    tracker_id = 'data.' + repository.study.tracker
            #    data_id = dict(row)['data'].get(repository.study.tracker)

            #    # Create list of results
            #    repo_datas = db.data.find( { tracker_id: data_id } )
            #    repo_dict = dict( (repo['label'], repo) for repo in repo_datas )

            #    # Check if data is complete or not
            #    for linked_repo in linked:
            #        if linked_repo in repo_dict:
            #            if repo_dict[linked_repo]['is_finished']:
            #                link_dict[ linked_repo.name ] = 'finished'
            #            else:
            #                link_dict[ linked_repo.name ] = 'incomplete'
            #        else:
            #            link_dict[ linked_repo.name ] = 'empty'

            #    copy['linked'] = link_dict

            hydrated.append( copy )

        return hydrated

    def serialize_data( self, data, fields, repo_id, data_id, options=None ):
        options = options or {}
        copy = {}

        # ISN hack: add completion status
        ######### BEGIN HACK ###########
        ineligible = False
        checkin_date = data.get('checkin_dtime', None)
        if checkin_date:
            checkin_date = datetime.strptime(checkin_date, "%Y-%m-%dT%H:%M:%S.%fZ")
        if 'repo' in options and 'patient_list' in options['repo'].name:
            linked = options.get('linked', [])
            patient_id = data.get('patient_id')
            copy['_status'] = {}
            for repo in linked:
                copy['_status'][repo.name] = ''
                #submissions = { 'repo': ObjectId(repo.mongo_id), 'data.patient_id': patient_id }
                #submissions = db.data.find(submissions)
                #recurring = repo.name in RECURRING_FORMS
                #expected_count = (datetime.now() - checkin_date).days
                #if not recurring:
                #    if submissions.count() > 0:
                #        copy['_status'][repo.name] = 'complete'
                #    elif submissions.count() == 0:
                #        copy['_status'][repo.name] = 'data_required'
                #else:
                #    if submissions.count() == 0:
                #        copy['_status'][repo.name] = 'data_required'
                #    elif submissions.count() >= expected_count:
                #        copy['_status'][repo.name] = 'complete'
                #    else:
                #        copy['_status'][repo.name] = 'incomplete'

                #if repo.name == 'p01_screening_form' and submissions.count() > 0:
                #    form = list(submissions)[0]
                #    enrolled = form['data'].get('enrolled', 'no')
                #    if enrolled != 'yes':
                #        ineligible = True


        # if not enrolled, mark all forms as complete
        if ineligible:
            for key, __ in copy['_status'].iteritems():
                copy['_status'][key] = 'complete'

        ######### END HACK ##########

        for field in fields:

            key = field.get( 'name' )
            val = data.get( key )

            # Convert strings into a unicode representation.
            if field.get( 'type' ) in [ 'text', 'note' ]:
                val = unicode( val ).encode( 'utf-8' )
                copy[ key ] = val

            # Give a full URL for media
            elif field.get( 'type' ) in [ 'photo' ]:

                if settings.DEBUG or settings.TESTING:
                    host = 'localhost:8000/media'
                else:
                    host = settings.AWS_S3_MEDIA_DOMAIN

                val = 'http://%s/%s/%s/%s' % ( host, repo_id, data_id, val )
                copy[ key ] = val

            # Correctly recurse through groups
            elif field.get( 'type' ) == 'group':

                val = self.serialize_data( data=data,
                                            fields=field.get( 'children' ),
                                            repo_id=repo_id,
                                            data_id=data_id )
                for k in val:
                    copy[ k ] = val[ k ]

            else:
                copy[ key ] = val


        return copy

def dehydrate( survey ):

    # Reformat python DateTime into JS DateTime
    if 'timestamp' in survey:
        survey[ 'timestamp' ] = survey[ 'timestamp' ].strftime( '%Y-%m-%dT%X' )

    if '_id' in survey:
        survey[ 'id' ] = survey.pop( '_id' )

    for key in survey.keys():
        if isinstance( survey[key], dict ):
            survey[ key ] = dehydrate( survey[key] )
        elif isinstance( survey[key], list ):
            survey[ key ] = dehydrate_list( survey[key] )
        else:
            survey[ key ] = unicode( survey[ key ] ).encode( 'utf-8' )

    return survey


def dehydrate_list( target ):

    hydrated = []
    for el in target:
        if isinstance( el, dict ):
            hydrated.append( dehydrate( el ) )
        elif isinstance( el, list ):
            hydrated.append( dehydrate_list( el ) )
        else:
            hydrated.append( unicode( el ).encode( 'utf-8' ) )

    return hydrated


def dehydrate_survey( cursor ):
    '''
        Decrypt survey data and turn any timestamps into javascript-readable
        values.
    '''
    if isinstance( cursor, dict ):
        return dehydrate( cursor )

    return [ dehydrate( row ) for row in cursor ]


def user_or_organization( name ):
    results = User.objects.filter( username=name )

    if len( results ) > 0:
        return results[0]

    results = Organization.objects.filter( name=name )

    if len( results ) > 0:
        return results[0]

    return None
