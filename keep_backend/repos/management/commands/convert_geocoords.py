from bson import ObjectId
from django.core.management.base import BaseCommand

from backend.db import db


class Command( BaseCommand ):
    help = 'Go through all data in '

    def _flatten( self, root ):
        '''
            Flattens a repository field list into an array of fields. We also
            filter for specifically "geopoint" field types.

            Params
            ------
            root : list
                Root represents a list of "fields". If the field type is a group,
                we jump deeper until we reach the end of that group. Otherwise,
                we filter for geopoint fields and only add those to our list
                of fields.
        '''
        fields = []

        for field in root:

            if field.get( 'type' ) == 'group':
                fields.append( self._flatten( field.get( 'children' ) ) )
            elif field.get( 'type' ) == 'geopoint':
                fields.append( field )

        return fields

    def handle( self, *args, **options ):
        '''
            Filter through *all* data elements in the MongoDB database. This
            may take a while depending on the number of elements in the database.

            We search for geopoint fields and convert them into the more useful
            "geocoord" dictionary which separates out lat/lng/altitude into
            useful attributes that can be search/filtered/etc.
        '''
        for repo in db.repo.find():

            geofields = self._flatten( repo.get( 'fields' ) )

            # If this repository has no geopoint fields, continue onto the
            # next data repo.
            if len( geofields ) == 0:
                continue

            # Filter out for all data elements for this repository.
            for item in db.data.find( { 'repo': ObjectId( repo.get( '_id' ) ) } ):

                data = item.get( 'data' )

                # Loop through each geofield and convert into our geodata object
                # when possible.
                for gfield in geofields:
                    field_name = gfield.get( 'name' )

                    if field_name in data:
                        geodata = {
                            'type': 'Point',
                            'coordinates': [],
                            'properties': {
                                'altitude': 0,
                                'accuracy': 0,
                                'comment': '' }}

                        geostring = data[ field_name ]

                        # If for some reason, this item was already generated
                        # skip it. ( did we run this twice? )
                        if not isinstance( geostring, basestring ):
                            print 'Already converted... did you run this twice?'
                            continue

                        geostring = geostring.split( ' ' )

                        if len( geostring ) == 4:
                            # Attempt to convert location string into the geodata
                            # object.
                            try:
                                # GeoJSON coordinates are stored <lng, lat>
                                geodata[ 'coordinates' ].append( float( geostring[1] ) )
                                geodata[ 'coordinates' ].append( float( geostring[0] ) )
                                geodata[ 'properties' ][ 'altitude' ] = float( geostring[2] )
                                geodata[ 'properties' ][ 'accuracy' ] = float( geostring[3] )
                            except ValueError:
                                # If for some reason we can't convert this string
                                # save the string as a "comment" metadata in the
                                # new geodata object
                                geodata[ 'properties' ][ 'comment' ] = data[ field_name ]
                        else:
                            geodata[ 'properties' ][ 'comment' ] = data[ field_name ]

                        # Finally go in and update the said field in the actual
                        # database!
                        print 'Updating %s' % ( item.get( '_id' ) )
                        full_field = 'data.%s' % ( field_name )
                        db.data.update( { '_id': item.get( '_id' ) },
                                        { '$set': { full_field: geodata } } )
