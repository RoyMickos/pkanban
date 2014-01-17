#pkanban

Simple personal kanban application, created as a django <https://www.djangoproject.com/>
application. Django acts as a REST backbone, the template engine is not used, and 
front-end is based on dojo <http://dojotoolkit.org/>.

##Installation
This is a django application so you will need a django project to put it in.

1. Install the pkanban app as a python module using `pip install pkanban-version.tar.gz`.
Alternatively you can also clone from git <https://github.com/RoyMickos/pkanban> and drop
the sources under your project.

2. In your project's settings file, add the kanban app:

    INSTALLED_APPS = (...,'pkanban',...)

3. Configure your web front end to handle the static files. Note that the git clone will
only have the uncompiled resources in `pkanban/static/spa/src`. With the python package,
run `collectstatic` to place your sources where you want them. If you use django to serve
static files, then you need the following configuration:

    STATIC_URL = '/spa/lib/'

With apache, copy static files to the `DocumentRoot` of your virtual host. The front end
http calls will assume `/spa/lib` as the path. The urlconf is such that a http request to
`pkanban/` will cause a redirect to `/spa/lib/index.html`.



