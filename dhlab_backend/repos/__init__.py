'''
    surveys module

    Views that have to do with manipulating/viewing forms and form data are
    placed in this module
'''


def validate_and_format( fields, data ):
    '''
        Do some basic validation and convert strings to <type> where
        necessary.
    '''
    survey_data = {}
    for element in fields:

        etype = element[ 'type' ]
        ename = element[ 'name' ]

        # Do type conversions
        if ename in data:

            # Convert to integer
            if etype is 'integer':
                survey_data[ ename ] = int( data[ ename ] )
            elif 'select all' in etype:
                survey_data[ ename ] = data.getlist( ename, [] )
            else:
                survey_data[ ename ] = data[ ename ]

    return survey_data
