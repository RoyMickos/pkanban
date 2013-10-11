import os
from setuptools import setup

README = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='pkanban',
    version='0.3.1',
    packages=['pkanban'],
    package_dir={'pkanban': 'pkanban'},
#    package_data={'pkanban': ['../client/lib/index.html','../client/lib/app/resources/*.ico','../client/lib/app/resources/*.css',
#                              '../client/lib/app/resources/images/*.png','../client/lib/app/resources/audio/*.mp3',
#                              '../client/lib/dojo/dojo.js','../client/lib/app/run.js',
#                              '../client/lib/dijit/layout/templates/*.html', '../client/lib/dijit/form/templates/*.html',
#                              '../client/lib/dijit/templates/*.html',
#                              '../client/lib/dijit/themes/claro/form/images/buttonArrows.png']},
    include_package_data=True,
    license='BSD License',  # example license
    description='A simple Django web app for personal kanban task management',
    long_description=README,
    url='http://rmickos.kapsi.fi/',
    author='Roy Mickos',
    author_email='roy.mickos@gmail.com',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License', # example license
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
