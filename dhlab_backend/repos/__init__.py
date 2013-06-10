'''
    surveys module

    Views that have to do with manipulating/viewing forms and form data are
    placed in this module
'''


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
            elif 'select all' in etype:
                if isinstance( data, QueryDict ):
                    valid_data[ ename ] = data.getlist( ename, [] )
                else:
                    valid_data[ ename ] = data.get( ename, [] )
            else:
                valid_data[ ename ] = data[ ename ]

        elif ename in files:
            valid_data[ ename ] = files[ ename ].name
            valid_files[ ename ] = files[ ename ]

    return ( valid_data, valid_files )
