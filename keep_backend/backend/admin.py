from django.contrib import admin
from visualizations.models import Visualization

class VizAdmin( admin.ModelAdmin ):
	pass

admin.site.register( Visualization, VizAdmin )