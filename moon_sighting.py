import ephem
import math
from skyfield.api import N, W, load, wgs84
from py_calendrical import location, calendars, triganometry
from util import *
import timezonefinder
import pytz
from datetime import datetime

ts = load.timescale()
t = ts.now()

eph = load('de421.bsp')
# moon, earth = eph['moon'], eph['earth']
# rumailah = earth + wgs84.latlon(25.4140779 * N, 49.7235786 * W, elevation_m=129)

# MOON_RADIUS = 1737.4  # km
# appdiam = 360 / math.pi * math.asin(MOON_RADIUS / rumailah.at(t).observe(moon).distance().km)
# print('Appearant Diameter = %f' % appdiam)

# print('\nUsing py_calendrical')
# rum = location.Location(25.4140779, 49.7235786, 129, location.Clock.days_from_hours(3))
# tee = calendars.gregorian.GregorianDate(2021, 9, 19).to_fixed() + location.Clock(0, 13, 0).to_time()
# P_cal = rum.lunar_parallax(tee)  # in degress (type mpf)
# HP_cal = triganometry.sin_degrees(P_cal) / triganometry.cos_degrees(rum.lunar_altitude(tee))
# print('HP_cal = %f rad' % HP_cal)
# SD_cal = 0.27245 * HP_cal  # semi-diameter of the Moon
# print('SD = %f deg' % SD_cal)

lat = 31.81
lon = 34.644
elevation = 0

year = 2000
month = 5
day = 5
hour = 19
minute = 43
second = 0

tf = timezonefinder.TimezoneFinder()

# From the lat/long, get the tz-database-style time zone name (e.g. 'America/Vancouver') or None
timezone_str = tf.certain_timezone_at(lat=lat, lng=lon)

if timezone_str is None:
    print('Could not determine the time zone')
    tz_offset_hours = None
    tz = None
else:
    tz = pytz.timezone(timezone_str)
    tz_offset_hours = tz._utcoffset.total_seconds() / 60 / 60

lo37 = location.Location(lat, lon, elevation, tz_offset_hours / 24)
tee37 = calendars.gregorian.GregorianDate(year, month, day).to_fixed() + location.Clock(hour, minute, second).to_time()
P_cal37 = lo37.lunar_parallax(tee37)
HP = triganometry.sin_degrees(P_cal37) / triganometry.cos_degrees(lo37.lunar_altitude(tee37))
HP = rad2min(HP)  # convert from rad to minutes of arc
SD = 0.27245 * HP  # semi-diameter of the Moon
# print("SD = %.1f'" % SD)
SD_topo = SD * (1 + (math.sin(deg2rad(lo37.lunar_altitude(tee37))) * math.sin(min2rad(HP))))
# print("SD' = %.1f'" % SD)

moon, sun, earth = eph['moon'], eph['sun'], eph['earth']
loc = earth + wgs84.latlon(lat, lon, elevation_m=elevation)
dt = ts.from_datetime(datetime(year, month, day, hour, minute, second, tzinfo=tz))

moon_alt, moon_az, moon_distance = loc.at(dt).observe(moon).apparent().altaz()
sun_alt, sun_az, sun_distance = loc.at(dt).observe(sun).apparent().altaz()

ARCV = round(moon_alt.degrees - sun_alt.degrees, 2)
DAZ = round(sun_az.degrees - moon_az.degrees, 2)
ARCL = rad2deg(math.acos(math.cos(deg2rad(ARCV)) * math.cos(deg2rad(DAZ))))

W_topo = SD_topo * (1 - (math.cos(deg2rad(ARCV)) * math.cos(deg2rad(DAZ))))

q = (ARCV - (11.8371 - 6.3226*W_topo + 0.7319*W_topo**2 - 0.1018*W_topo**3)) / 10

print('date = %d/%d/%d %d:%d:%d' % (year, month, day, hour, minute, second))
print('lat= %.1f, lon= %.1f' % (lat, lon))
print('ARCL = %.1f deg' % ARCL)
print('ARCV = %.1f deg' % ARCV)
print('DAZ = %.1f deg' % DAZ)
print("HP = %.1f'" % HP)
print("W' = %.2f'" % W_topo)
print('q = %.3f' % q)




