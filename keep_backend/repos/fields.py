from django import forms

from django.utils.translation import ugettext_lazy as _, ungettext_lazy

class GeopointField(forms.Field):
	default_error_messages = {
		'not_geopoint': _(u'Invalid geopoint data.  Please use the map for data.'),
	}

