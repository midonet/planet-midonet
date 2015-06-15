#!/bin/sh
cd /root/planet-midonet/
# We don't pull since we don't want to merge. Overwrite!
git fetch
git reset --hard origin/master
# These configuration files are symlinked from the proper locations,
# but git isn't SELinux aware
chcon -t system_cron_spool_t cronjob
chcon -t httpd_config_t      httpd-planet.conf
# Just in case the configuration changed...
# (note: crond reloads changed files automatically)
systemctl reload httpd
# Update the planet
/bin/python /root/planet-midonet/planet.py /root/planet-midonet/midonet.ini
