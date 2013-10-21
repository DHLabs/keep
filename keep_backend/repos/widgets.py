from django.forms import widgets

from django.utils.html import format_html
from django.utils.translation import ugettext_lazy

class GeopointInput(widgets.TextInput):
	is_hidden = False
	template = '<div'
