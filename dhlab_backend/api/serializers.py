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

    def to_csv( self, data, options=None ):
        options = options or {}

        data = self.to_simple( data, options )
        raw_data = StringIO.StringIO()

        writer = None
        for item in data.get( 'data', [] ):

            sub_data = item[ 'data' ]

            if writer is None:
                writer = csv.DictWriter( raw_data,
                                         sub_data.keys(),
                                         extrasaction='ignore')
                writer.writeheader()

            writer.writerow( sub_data )

        print raw_data

        return raw_data.getvalue()
