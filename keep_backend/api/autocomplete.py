import json
import pdb
from django.http import HttpResponse
from django.views.decorators.http import require_GET
from django.contrib.auth.models import User
from organizations.models import Organization

@require_GET
def autocomplete(request, endpoint):

    if 'q' in request.GET:
        query = request.GET['q']

    if endpoint == 'accounts':
        user_matches = User.objects.filter(username__icontains=query).values_list('username')
        user_matches = map(lambda m: m[0], user_matches)
        org_matches = Organization.objects.filter(name__icontains=query).values_list('name')
        org_matches = map(lambda m: m[0], org_matches)
        results = user_matches + org_matches

        return HttpResponse(json.dumps(results), status=200)

    return HttpResponse("Unknown endpoint", status=400)
