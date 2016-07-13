from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User

from backend.db import db
from repos.models import Repository


class Command( BaseCommand ):
    help = 'Recreate repos from mongodb'

    def handle( self, *args, **options ):

        mike = User.objects.get( username='mikepreziosi' )

        for repo in db.repo.find():

            mongo_id = str( repo[ '_id' ] )

            new_repo = Repository( mongo_id=mongo_id, name=mongo_id, user=mike )
            new_repo.save()
