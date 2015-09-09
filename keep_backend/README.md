## Overview

This is a brief overview on the modules in the backend, and what each of the
modules general purpose is. Most modules have further documentation in each of
their Python files, so check those for more detail.

### api

Contains serializers and configuration for the RESTful API.

### backend

Initializes all the urls/routes, and contains the entry level views (e.g.
home page, registration, etc.)

### openrosa

Handles serialization of XForm schemas.

### organizations

Users can create Organizations, which can have members and repositories. Users
can also share repos with an Organization (and thus with all its members).

### privacy

Privacy-preserving GIS code.

### repos

The `repos` module handles most of the direct interactions with a JSON form, such
as saving a completed form, and interacting directly with the Mongo database to
retrieve the JSON for the form creation. This module also handles pulling up
completed form data to view it, and form creation.

### settings

Contains configuration code for Django and the databases.

### studies

Studies are groups of repositories, usually with a registry. A registry form
allows objects to be tracked across multiple forms.

### templates

Contains all of the generic HTML templates for the KEEP site. Sub-apps like
`repos` and `organizations` also have template directories for their respective
functionality. Most BackboneJS templates are defined as partials in this
module.

### tests

Contains unit tests for the codebase.

### twofactor

This is a Git submodule that contains the code used for the site's twofactor
authentication.

### visualizations

Models representing visualizations.

### vocab

This module contains the code for uploading a new medical vocabulary
to the Mongo database. It is used alongside the vocab api.
