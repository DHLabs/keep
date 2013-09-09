from bson import ObjectId
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User

from backend.db import db
from repos.models import Repository


class Command( BaseCommand ):
    help = 'Go through all data in '

    def _flatten( self, root ):
        fields = []

        for field in root:

            if field.get( 'type' ) == 'group':
                fields.append( self._flatten( field.get( 'children' ) ) )
            elif field.get( 'type' ) == 'geopoint':
                fields.append( field )

        return fields

    def handle( self, *args, **options ):

        for repo in db.repo.find():

            geofields = self._flatten( repo.get( 'fields' ) )

            if len( geofields ) == 0:
                continue

            for item in db.data.find( { 'repo': ObjectId( repo.get( '_id' ) ) } ):

                data = item.get( 'data' )

                for gfield in geofields:
                    field_name = gfield.get( 'name' )

                    if field_name in data:
                        geodata = {
                            'lat': None,
                            'lng': None,
                            'altitude': None,
                            'accuracy': None,
                            'comment': '' }

                        geostring = data[ field_name ]

                        if not isinstance( geostring, basestring ):
                            continue

                        geostring = geostring.split( ' ' )

                        if len( geostring ) == 4:
                            geodata[ 'lat' ] = float( geostring[0] )
                            geodata[ 'lng' ] = float( geostring[1] )
                            geodata[ 'altitude' ] = float( geostring[2] )
                            geodata[ 'accuracy' ] = float( geostring[3] )
                        else:
                            geodata[ 'comment' ] = data[ field_name ]

                        full_field = 'data.%s' % ( field_name )

                        print 'Updating %s' % ( item.get( '_id' ) )
                        db.data.update( { '_id': item.get( '_id' ) },
                                        { '$set': { full_field: geodata } } )
