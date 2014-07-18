'''
    surveys module

    Views that have to do with manipulating/viewing forms and form data are
    placed in this module
'''
import logging
from django.core.files import File
from django.http import QueryDict

logger = logging.getLogger( __name__ )


def validate_and_format( fields, data, files ):
    """Do some basic validation and convert strings to <type> where
       necessary.

       Parameters
       ----------
       fields : []
           The JSON empty fields of the form.
       data : array of strings
           All user data provided to the form.
       files : array of strings
           All user files provided to the form.

       Returns
       -------
       valid_data : dictionary
           Dictionary of all validated data and corresponding questions
       valid_files : dictionary
           Dictionary of all validated files and corresponding questions
    """
    valid_data = {}
    valid_files = {}

    for element in fields:

        etype = element[ 'type' ]
        ename = element[ 'name' ]

        # Flatten groups by making a recursive call
        if 'group' in etype:
            temp_data = validate_and_format( element[ 'children' ], data, files )
            valid_data.update( temp_data[0] )
            valid_files.update( temp_data[1] )

        # Do type conversions
        if ename in data:
            # Convert to integer
            if etype == 'integer':
              try:
                valid_data[ ename ] = int( data[ ename ] )
              except ValueError:
                pass

            elif 'select all' in etype:

                # If data is a QueryDict ( from a HttpRequest ), grab the list like so
                if isinstance( data, QueryDict ):
                    valid_data[ ename ] = data.getlist( ename, [] )
                # Otherwise attempt to parse the data value
                else:

                    list_data = data.get( ename, [] )

                    if isinstance( list_data, basestring ):
                        valid_data[ ename ] = list_data.split( ',' )
                        logger.info( list_data.split( ',' ) )
                    else:
                        valid_data[ ename ] = list_data

            elif etype in [ 'photo', 'video' ] and isinstance( data.get( ename ), File ):

                valid_data[ ename ] = data.get( ename ).name
                valid_files[ ename ] = data.get( ename )

            elif etype == 'geopoint':

                # Convert a X,Y string into a geocoordinate.
                geodata = { 'type': 'Point',
                            'coordinates': [],
                            'properties': {
                                'altitude': 0,
                                'accuracy': 0,
                                'comment': '' }}

                # TODO: Handle potential errors parsing the string?
                coords = data.get( ename )
                coords = coords.split( ' ' )
                # If the row doesn't have a geopoint, set to None
                try:
                  geodata[ 'coordinates' ] = [ float( coords[0] ), float( coords[1] ) ]
                except ValueError:
                  geodata[ 'coordinates' ] = [ None, None ]

                valid_data[ ename ] = geodata

            else:
                # Otherwise treat the piece of data as whatever it came in as.
                valid_data[ ename ] = data[ ename ]

        if files is not None and ename in files:
            valid_data[ ename ] = files[ ename ].name
            valid_files[ ename ] = files[ ename ]

    return ( valid_data, valid_files )
