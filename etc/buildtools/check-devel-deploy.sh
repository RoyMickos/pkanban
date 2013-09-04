#!/usr/bin/env bash

set -e

# Base directory for this entire project
# run the script in root (../..)
BASEDIR=$(cd $(dirname $0) && pwd)
TMPDIR="$BASEDIR/tmp"

# Source directory for dojo base package (development version)
DOJOPKG="$BASEDIR/etc/libs/dojo-release-1.9.1-src.tar.gz"

# Source directory for Django development site settings
# Django site settings are not part of the project as they contain
# passwords etc. This is a Django app, so you need to set up a
# site for it.
#DJANGOSITE="/home/roy/work/awork/devel-resources"

if [ ! -d "$BASEDIR/src/dojo" ]; then
	echo "Dojo not installed. Installing from $DOJOPKG"
	mkdir "$TMPDIR"
	cd "$TMPDIR"
	tar -zxvf "$DOJOPKG"
	DOJODIR=$(ls)
	mv "$DOJODIR/dojo/" "../src/"
	mv "$DOJODIR/dijit/" "../src/"
	mv "$DOJODIR/dojox/" "../src/"
	mv "$DOJODIR/util/" "../src/"
	cd ..
	rm -rf "$TMPDIR"
else
	echo "DOJO in place"
fi

if ([ ! -d "$BASEDIR/../devel-site" ] && [ ! -f "$BASEDIR/../manage.py" ]); then
	echo "Site settings absent. Copying from $DEVELSITESETTINGS"
	cp "$DEVELSITESETTINGS/manage.py" "$BASEDIR/../"
	cp -r "$DEVELSITESETTINGS/devel_site/" "$BASEDIR/../"
else
	echo "site settings in place"
fi

echo "Jenkins defines $DEVELSITESETTINGS"

