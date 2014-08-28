import re
import StringIO
import unicodecsv

from django.utils.text import slugify

from tastypie.serializers import Serializer


class CSVSerializer( Serializer ):
    formats = [ 'json', 'jsonp', 'csv' ]

    content_types = {
        'json': 'application/json',
        'jsonp': 'text/javascript',
        'csv': 'text/csv',
    }

    FLOAT_TYPE = re.compile(r'^(\d+\.\d*|\d*\.\d+)$')
    INT_TYPE   = re.compile(r'^\d+$')
    LOCATION_TYPE = re.compile(r'^(\-?\d+(\.\d+)?) \s*(\-?\d+(\.\d+)?) \s*(\d+) \s*(\d+)$')

    def _sniff_type( self, val ):
        '''
            A really stupid and bare-bones approach to data type detection.
        '''
        if self.FLOAT_TYPE.match( val ):
            return 'decimal'
        elif self.INT_TYPE.match( val ):
            return 'int'
        elif self.LOCATION_TYPE.match( val ):
            return 'geopoint'
        else:
            return 'text'

    def _format_data( self, field_type, field_value ):
        '''
            Given a certain data type, format the value into a string that could
            possibly be parsed later by our same code.

            Params
            ------
            field_type : string
                A string representation the type of data this field holds.

            field_value : Object
                A python object ( string, dict, etc ) that is our internal
                representation of this data. This will be converted to a
                standard string format that can be later parsed back into the
                system if necessary.
        '''

        # If the field_value is None, simply return an empty string.
        if field_value is None:
            return ''.encode('utf-8')

        if field_type == 'geopoint':
            # Converts geopoints into an X,Y coordinate string
            try:
                coords = field_value.get( 'coordinates' )
                props = field_value.get( 'properties' )
                value = '%s %s %s %s' % ( str( coords[1] ), str( coords[0]), str(props['altitude']), str(props['accuracy']) )
                return value.encode('utf-8')
            except Exception as e:
                return "".encode('utf-8')

        elif 'select all' in field_type:
            # Converts a list into a comma-seperated list of values
            return ','.join( field_value ).encode('utf-8')
        else:
            return field_value.encode('utf-8')

    def to_csv( self, data, options=None ):
        '''
            Converts the JSON representation from the data API into a CSV file.
        '''
        options = options or {}

        #data = self.to_simple( data, options )
        raw_data = StringIO.StringIO()

        writer = unicodecsv.DictWriter( raw_data,
                                        [ x[ 'name' ] for x in data[ 'meta' ][ 'fields' ] ],
                                        extrasaction='ignore')
        writer.writeheader()

        for item in data.get( 'data', [] ):

            # Loops through the field list and format each data value according to
            # the type.
            row = {}
            for field in data[ 'meta' ][ 'fields' ]:

                # Grab the field details and convert the field into a string.
                field_name = field.get( 'name' )
                field_type = field.get( 'type' )
                field_value = item.get( 'data' ).get( field_name, None )

                row[ field_name ] = self._format_data( field_type, field_value )

            writer.writerow( row )

        return raw_data.getvalue()

    def from_csv( self, csv_data ):
        fields, data = ( [], [] )

        csv_file = unicodecsv.DictReader( csv_data )

        # Grab the headers and create fields for the new repo
        headers = csv_file.fieldnames

        # Used to sniff the data types
        sniff = csv_file.next()

        # Go through each field name and attempt to parse the corresponding
        # data type.
        for idx, header in enumerate( headers ):

            if len( header ) == 0:
                raise Exception( 'Column headers can not be blank!' )

            fields.append({
                'name': slugify( unicode( header ) ),
                'label': header,
                'type': self._sniff_type( sniff[ header ] )
            })

        # Parse the first data row
        datum = {}
        for field in fields:
            datum[ field[ 'name' ] ] = sniff.get( field[ 'label' ], None )
        data.append( datum )

        # Now parse the rest of them
        for item in csv_file:
            datum = {}
            for field in fields:
                datum[ field[ 'name' ] ] = item.get( field[ 'label' ], None )
            data.append( datum )

        return ( fields, data )

