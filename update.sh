#!/bin/sh
cd /root/planet-midonet/
# We don't pull since we don't want to merge. Overwrite!
git fetch
git reset --hard origin/master
# update cronjob in case it changed
# note: crond reloads changed config automatically
# (use cp instead of ln/mv to avoid SELinux issues)
cp --remove-destination cronjob           /etc/cron.d/planet
# update httpd config in case it changed
# (use cp instead of ln/mv to avoid SELinux issues)
cp --remove-destination httpd-planet.conf /etc/httpd/conf.d/planet.conf
systemctl reload httpd
# Update the planet
/bin/python /root/planet-midonet/planet.py /root/planet-midonet/midonet.ini
