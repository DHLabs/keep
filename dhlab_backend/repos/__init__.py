'''
    surveys module

    Views that have to do with manipulating/viewing forms and form data are
    placed in this module
'''
from django.core.files import File
from django.http import QueryDict


def validate_and_format( fields, data, files ):
    '''
        Do some basic validation and convert strings to <type> where
        necessary.
    '''
    valid_data = {}
    valid_files = {}

    for element in fields:

        etype = element[ 'type' ]
        ename = element[ 'name' ]

        # Do type conversions
        if ename in data:
            # Convert to integer
            if etype is 'integer':
                valid_data[ ename ] = int( data[ ename ] )
            # Flatten groups by making a recursive call
            elif 'group' in etype:
                temp_data = validate_and_format( element[ 'children' ], data, files )
                valid_data.update(temp_data[0])
                valid_files.update(temp_data[1])
            elif 'select all' in etype:
                if isinstance( data, QueryDict ):
                    valid_data[ ename ] = data.getlist( ename, [] )
                else:
                    valid_data[ ename ] = data.get( ename, [] )
            elif etype in [ 'photo', 'video' ] and isinstance( data.get( ename ), File ):
                valid_data[ ename ] = data.get( ename ).name
                valid_files[ ename ] = data.get( ename )
            else:
                valid_data[ ename ] = data[ ename ]

        if files is not None and ename in files:
            valid_data[ ename ] = files[ ename ].name
            valid_files[ ename ] = files[ ename ]

    return ( valid_data, valid_files )
