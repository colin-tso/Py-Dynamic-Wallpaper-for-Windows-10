import ephem
from datetime import datetime, timedelta, date, time
from time import localtime


def suntime(day_offset: int, lat: str, lon: str, elevation: int = 0):

    utc_offset = localtime().tm_gmtoff
    sun = ephem.Sun()
    home = ephem.Observer()
    home.lat = lat
    home.lon = lon
    home.elevation = elevation
    home.compute_pressure()

    home.date = datetime.combine(datetime.now().date(), time(
        00, 00, 00)) - timedelta(seconds=utc_offset) - timedelta(days=day_offset)

    print("Evaluating sunrise/sunset times for: %s UTC%+d" %
          ((home.date.datetime() + timedelta(seconds=utc_offset)).date(), utc_offset/3600))

    # Sunrise starting time
    sunrise_start = home.next_rising(
        sun).datetime() + timedelta(seconds=utc_offset)

    # Calculate sunrise ending time
    home.date = home.next_rising(sun).datetime()
    sunrise_alt = (ephem.Sun(home).alt - ephem.Sun(home).radius)
    while abs(sunrise_alt) > 1e-9:
        multiplier = -sunrise_alt * 150
        home.date = home.date.datetime() + timedelta(minutes=(1 * multiplier))
        sunrise_alt = (ephem.Sun(home).alt - ephem.Sun(home).radius)
    sunrise_end = home.date.datetime() + timedelta(seconds=utc_offset)

    # Sunset ending time
    sunset_end = home.next_setting(
        sun).datetime() + timedelta(seconds=utc_offset)

    # Calculate sunset starting time
    home.date = home.next_setting(sun).datetime()
    sunset_alt = (ephem.Sun(home).alt - ephem.Sun(home).radius)
    while abs(sunset_alt) > 1e-9:
        multiplier = -sunset_alt * 150
        home.date = home.date.datetime() - timedelta(minutes=(1 * multiplier))
        sunset_alt = (ephem.Sun(home).alt - ephem.Sun(home).radius)
    sunset_start = home.date.datetime() + timedelta(seconds=utc_offset)

    return sunrise_start, sunrise_end, sunset_start, sunset_end
