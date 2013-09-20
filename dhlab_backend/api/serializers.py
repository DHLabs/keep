import csv
import StringIO

from tastypie.serializers import Serializer


class CSVSerializer( Serializer ):
    formats = [ 'json', 'jsonp', 'csv' ]

    content_types = {
        'json': 'application/json',
        'jsonp': 'text/javascript',
        'csv': 'text/csv',
    }

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
        if field_type == 'geopoint':
            coords = field_value.get( 'coordinates' )
            return '%s, %s' % ( str( coords[0] ), str( coords[1] ) )
        else:
            return str( field_value )

    def to_csv( self, data, options=None ):
        '''
            Converts the JSON representation from the data API into a CSV file.
        '''
        options = options or {}

        data = self.to_simple( data, options )
        raw_data = StringIO.StringIO()

        writer = csv.DictWriter( raw_data,
                                 [ x.get( 'name' ) for x in data[ 'meta' ][ 'fields' ] ],
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
