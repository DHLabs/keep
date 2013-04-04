

def validate_and_format( form, data ):
    '''
        Do some basic validation and convert strings to <type> where
        necessary.
    '''

    survey_data = {}
    for element in form[ 'children' ]:

        etype = element[ 'type' ]
        ename = element[ 'name' ]

        # Do type conversions
        if ename in data:

            # Convert to integer
            if etype is 'integer':
                survey_data[ ename ] = int( data[ ename ] )
            else:
                survey_data[ ename ] = data[ ename ]

    return survey_data
