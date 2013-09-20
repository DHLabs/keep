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

    def to_csv(self, data, options=None):
        options = options or {}
        data = self.to_simple(data, options)
        raw_data = StringIO.StringIO()

        writer = csv.DictWriter( raw_data,
                                 data[ 'meta' ][ 'fields' ],
                                 extrasaction='ignore')
        writer.writeheader()

        for item in data.get( 'data', [] ):
            writer.writerow( item.get( 'data' ) )

        return raw_data.getvalue()
