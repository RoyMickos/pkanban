import os
from setuptools import setup

README = open(os.path.join(os.path.dirname(__file__), 'README.md')).read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='pkanban',
    version='0.3.',
    packages=['pkanban'],
    package_dir={'pkanban': 'pkanban'},
    include_package_data=True,
    install_requires=['MySQL-python'],
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
