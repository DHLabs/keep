from django.core.serializers.python import Serializer
from django.db import models


class VisualizationSerializer( Serializer ):
    """
        Converts a QuerySet of Visualization objects into a specific JSON
        format.
    """

    def end_object( self, obj ):
        self._current[ 'repo' ] = obj.repo.mongo_id
        self._current[ 'id' ] = obj.id

        self.objects.append( self._current )

class Visualization( models.Model ):

    name = models.CharField( max_length=255, blank=False )

    repo = models.ForeignKey( 'repos.Repository',
                              related_name='visualizations' )

    x_axis = models.CharField( max_length=255, blank=False )
    y_axis = models.CharField( max_length=255, blank=False )

    class Meta:
        ordering = [ 'name' ]
        verbose_name = 'visualization'
        verbose_name_plural = 'visualizations'


    def __unicode__( self ):
        return '%s - %s' % ( self.repo.name, self.name )


class FilterSet( models.Model ):
    """
        Represents a group of TastyPie filters that can be applied and viewed
        in the Filters view.
    """

    name = models.CharField( max_length=255, blank=False )
    repo = models.ForeignKey( 'repos.Repository', related_name='filters' )
    user = models.ForeignKey( 'auth.User', related_name='user')
    is_public = models.BooleanField(default=False)
    querystring = models.CharField( max_length=1024, blank=False )

    def __unicode__(self):
        return self.name
