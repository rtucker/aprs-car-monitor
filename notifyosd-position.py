#!/usr/bin/python
"""
Queries aprs.fi for current object location.  Sends notification using the
NotifyOSD subsystem.

Requires aprsfi.py from: http://github.com/rtucker/pyaprsfi
"""

import aprsfi
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

    message = "At %(lat)s %(lng)s as of %(nice_time)s. " % i
    if i['altitude'] > 0:
        message += "Altitude is %(altitude)i meters. " % i
    if i['position_age'] > 30:
        message += "Beaconing same posn for %(position_age)i seconds. " % i

    notifyosd(title, message)

