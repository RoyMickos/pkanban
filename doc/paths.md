#Serving dojo as django static files
This is a single-page application where the role of django is maily to serve as back-end for REST calls. After struggling for a while with csrf - wanting to keep that in, it seems that the best way is to separate concerns. That is, the SPA together with dojo libraries are served completely as static content, and we use authentication as a countermeasure for forgery.

##The Problem with marrying dojo and django
The dojo boilerplate comes with an app/run.js file which idea is to configure AMD
loader to find the necessary submodules. The key is the `baseUrl` definition which servers as the root of the module definition.

Django, on the other hand, has a `STATIC_URL` definition which it uses to detect files that are served as static content. In development, these need to match. Hence, the simplest option is to merge the content of run.js into index.html, which is ran through django's template engine:

    baseUrl: {{ STATIC_URL }},

This is handy because the `STATIC_URL` definition is changed between development and production.
