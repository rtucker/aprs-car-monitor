#!/usr/bin/python
"""
Queries aprs.fi for current object location.  Sends notification using the
NotifyOSD subsystem.

Requires aprsfi.py from: http://github.com/rtucker/pyaprsfi
"""

import aprsfi
import math
import pynotify
import sys
import time

try:
    import secrets
except ImportError:
    sys.stderr.write("Please copy secrets.py.dist to secrets.py and configure it to taste.\n")
    sys.exit(1)

if not pynotify.init("summary-body"):
    sys.stderr.write("pynotify isn't happy\n")
    sys.exit(1)

def notifyosd(title, message):
    """send a notification via pynotify"""
    n = pynotify.Notification(title, message)
    n.show()

def metersGeoDistance(lat1, lon1, lat2, lon2):
    """
    Calculate distance between two lat lons in meters
    adapted from http://www.zachary.com/s/blog/2005/01/12/python_zipcode_geo-programming
    """

    nauticalMilePerLat = 60.00721
    nauticalMilePerLongitude = 60.10793
    rad = math.pi / 180.0
    metersPerNauticalMile = 1852

    yDistance = (lat2 - lat1) * nauticalMilePerLat
    xDistance = (math.cos(lat1 * rad) + math.cos(lat2 * rad)) * (lon2 - lon1) * (nauticalMilePerLongitude / 2)

    distance = math.sqrt( yDistance**2 + xDistance**2 )

    return distance * metersPerNauticalMile

aprs = aprsfi.Api(key=secrets.APRS_FI_API_KEY)

response = aprs.loc(name=secrets.MONITOR_CALLSIGN)

if response['found'] == 0:
    notifyosd("Can't find " + secrets.MONITOR_CALLSIGN, "No results returned from aprs.fi")
    sys.exit(0)

for i in response['entries']:
    if i['speed'] > 0:
        title = "%(name)s is heading %(course)i degrees at %(speed)i km/h" % i
    else:
        title = "%(name)s: %(comment)s" % i

    i['position_age'] = int(i['lasttime']) - int(i['time'])

    i['nice_time'] = time.strftime('%b %d at %H:%M', time.localtime(int(i['time'])))

    i['meters_from_home'] = metersGeoDistance(secrets.HOME_LAT, secrets.HOME_LNG, float(i['lat']), float(i['lng']))

    i['kilometers_from_home'] = i['meters_from_home']/1000

    message = "At %(lat)s %(lng)s as of %(nice_time)s. " % i
    if i['altitude'] > 0:
        message += "Altitude is %(altitude)i meters. " % i

    if i['kilometers_from_home'] > 2:
        message += "Currently %(kilometers_from_home)i km from home. " % i
    elif i['meters_from_home'] > 100:
        message += "Currently %(meters_from_home)i meters from home. " % i
    else:
        message += "Currently at home. "

    if i['position_age'] > 30:
        message += "Beaconing same posn for %(position_age)i seconds. " % i

    notifyosd(title, message)

