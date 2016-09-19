import StringIO
import unicodecsv
from datetime import datetime
from django.core.management.base import BaseCommand
from django.core.mail import EmailMessage
from backend.db import db
from bson import ObjectId
from studies.models import Study
from repos.models import Repository

def format_data(field_type, field_value ):
    # If the field_value is None, simply return an empty string.
    if field_value is None:
        return ''

    if field_type == 'geopoint':
        # Converts geopoints into an X,Y coordinate string
        coords = field_value.get( 'coordinates' )
        props = field_value.get( 'properties' )
        return '%s %s %s %s' % ( str( coords[1] ), str( coords[0]), str(props['altitude']), str(props['accuracy']) )

    elif 'select all' in field_type:
        # Converts a list into a comma-seperated list of values
        return ','.join( field_value )
    else:
        return str( field_value )


def create_csv_from_repo(repo):
    # Get the data
    query = { 'repo': ObjectId(repo.mongo_id) }
    cursor = db.data.find(query)
    data = list(cursor)

    fields = repo.flatten_fields()

    output = StringIO.StringIO()

    writer = unicodecsv.DictWriter( output,
                                    [ x[ 'name' ] for x in fields ],
                                    extrasaction='ignore')
    writer.writeheader()

    for item in data:

        # Loops through the field list and format each data value according to
        # the type.
        row = {}
        for field in fields:

            # Grab the field details and convert the field into a string.
            field_name = field.get( 'name' )
            field_type = field.get( 'type' )
            field_value = item.get( 'data' ).get( field_name, None )

            row[ field_name ] = format_data( field_type, field_value )

        writer.writerow( row )

    return output.getvalue()


class Command(BaseCommand):
    args = 'None'
    help = 'Emails CSV reports to the study admins'

    def handle(self, *args, **options):
        self.stdout.write('Sending email reports...')

        # For each repo in Phase 2
        phase2 = Study.objects.filter(user__username='isn', name='Phase 2')
        repos = Repository.objects.filter(study=phase2)
        for repo in repos:
            csv = create_csv_from_repo(repo)

            # Send the CSV via email
            subject = "Data Download: {0}".format(repo.name)
            body = "Data collected at {0}".format(datetime.now())
            sender = 'noreply@keep.org'
            recipients = [ 'wes.vetter@gmail.com', ]
            filename = "{0}__{1}".format(datetime.now().date(), repo.name)
            message = EmailMessage(subject, body, sender, recipients)
            message.attach(filename, csv, 'text/csv')
            message.send()

        self.stdout.write('Reports successfully sent.')
