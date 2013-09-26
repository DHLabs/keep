This is a brief documentation on the modules in the backend, and what
each of the modules general purpose is.  Most modules have further
documentation in each of their python files, so check those for more
detail.

api
---
The api module is relatively self explanatory, it contains the code
for interacting with the KEEP api.  It contains the following code:
__init__ : python initialization file, blank
authentication
authorization
data
repo : Used for interacting with the repositories (essentially the
       empty forms).
resources
serializers
study
user : Used to search for users.
vocab : interacts with the uploaded medical vocabularies, this is
        only used for autofilling text boxes so far.  Uploading 
        additional vocabularies is handled in the seperate vocab
        module.

backend
-------


openrosa
-------

organizations
-------------

privacy
-------

repos
-----
The repos module handles most of the direct interactions with a JSON
form, such as saving a completed form, and interacting directly with
the Mongo database to retrieve the JSON for the form creation. This
module also handles pulling up completed form data to view it, and form creation.  It contains the following:
templates -> : Folder containing most of the base html for forms.
               Most of the javascript for this is in the frontend.
    finish_survey.html : The page that is shown when a form is 
                         completed by a non-user. 
    map_visualize.html : The html for showing the map of geopoint
                         data. Shown when viewing data.
    new.html : The page shown when a user decides to create a form
               from scratch.  Seen only by the form creator.
    visualize.html : The page shown when the form creator views the
                     data submitted to the form.
    webform.html : Base template used when filling out the form.
forms.py : Handles form cleaning and creation for both csv files and
           the 'from scratch' form builder.
models.py
urls.py
views.py

templates
---------
This module contains much of the html used throughout the KEEP site.

tests
-----
The unit tests for the codebase.  The contained test files are:
__init__
test_data_api
test_http
test_http_organizations
test_openrosa_api
test_repo_api

twofactor
---------
This module contains the code used for the site's twofactor 
authentication.

vocab
-----
This module contains the code for uploading a new medical vocabulary
to the Mongo database.  It is used alongside the vocab api.
__init__ : python initialization file, blank
vocab_to_mongo : a command line utility for uploading a new vocab to
                 the database. This must be run on the 
                 server/computer containing the MongoDB database.