# API

Keep exposes an API to programmatically interact with repositories and data.

## API Keys

API keys can be created and managed from the settings page of the web app.

## Repositories

    /api/v1/repos/
    /api/v1/repos/?format=json

Returns all the XForms that the user has access to, either as XML or JSON.

Form data can be submitted by sending a POST request with the form data to
`/api/v1/data/<repo_id>/webform`.

## Data

`/api/v1/data/<repo_id>/`

Returns the data for the repository, along with metadata including the fields
(ie. field types, options, labels, etc.), and pagination info.

```
curl -v \
     -X POST \
     -F "patient_name=luke skywalker" \
     -F "patient_id=J3D1" \
     -F "doctor_id=doctorbob" \
     http://localhost:8000/api/v1/repos/<repo_id>/?user=jsmith&key=9f42b2b609781344d2730ee1839e592c
```

Note that a user/key pair is **required** to use the API routes (`user` is the
owner of the key). If the form is public then you can also POST to the
`/webform/` URL.

Filters can be added to the querystring to restrict the data returned. Filters
have the form of `data__KEY=VALUE` or `data__KEY__CONSTRAINT=VALUE`, e.g.
`/api/v1/data/<repo_id>/?data__country=usa&data__age__gt=65`

Multiple filters can be applied, but if two filters for the same field are
submitted, only one of them will be applied.
