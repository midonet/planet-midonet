#!/bin/sh
cd /root/planet-midonet/
# We don't pull since we don't want to merge. Overwrite!
git fetch
git reset --hard origin/master
# Update the planet
/bin/python /root/planet-midonet/planet.py /root/planet-midonet/midonet.ini
