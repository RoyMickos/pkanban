#pkanban

Simple personal kanban application, created as a django application. Django acts as
a REST backbone, and the static files are self-sufficient, i.e. the django template
framework is not used except for authentication.

##Installation
You need to add pkanban as an application to your settings file as usual.

    INSTALLED_APPS = (...,'pkanban',...)

The tricky part is deploying static files.

###Using Django's staticfiles middleware
This is not the preferred way, as pkanban 'steals' the project's static files
configuration. The app assumes that they are located in a directory called
`spa/lib` at the django project root:

    STATIC_URL = '/spa/lib/'
    STATICFILES_DIRS = (..., '/django/project/root/spa/lib', ...)

Reason being I did not find any better way to make Django's static files
and JavaScript AMD loader work together.

###Using Apache
Simply copy static files to the `DocumentRoot` of your virtual host. For example,
if your DocumentRoot is `/var/www`:

    STATIC_ROOT = '/var/www/'
    STATIC_URL = '/spa/lib'


