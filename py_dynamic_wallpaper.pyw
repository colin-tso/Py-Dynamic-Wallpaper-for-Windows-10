'''
A python-based program for Windows 10 that dynamically changes and fades your desktop wallpaper
based on the time of day.
Unlike most implementations, this utility allows for:
1. Fading between wallpaper images by hooking onto the Windows API and enabling Active Desktop
via [pywin32].
2. Dynamic sunrise/sunset times based on your location and time of year.
3. Requires no internet connection.
'''

# General Dependencies
# Standard imports
import time
import datetime
import configparser
import math
import os
from collections import namedtuple

# Suntime
from suntime import suntime
# Active Desktop
import iad


def main():
    '''Main Function'''
    config_params = load_config()

    # Initialise wallpaper time variables
    suntime_last_update = None
    day_period = None
    period_duration = None
    last_day_period = None
    period_start_time = None
    last_selected_image = None

    # Start Loop #
    while True:

        now = datetime.datetime.now()
        now_seconds = now.hour * 3600 + now.minute * 60 + now.second

        if config_params.seasonal:
            if suntime_last_update != datetime.date.today():

                # Get sunrise/sunset time and durations
                suntime_params = suntime(
                    0, config_params.lat, config_params.lon, config_params.elevation)
                # prev_sunset_end = suntime(-1, lat, lon, elevation)[3]
                next_sunrise_start = suntime(
                    1, config_params.lat, config_params.lon, config_params.elevation).sunrise_start
                print(f"sunrise starts @: {suntime_params.sunrise_start}")
                print(f"sunrise ends @: {suntime_params.sunrise_end}")
                print(f"sunset starts @: {suntime_params.sunset_start}")
                print(f"sunset ends @: {suntime_params.sunset_end}")
                print(f"the time is now: {now}")
                suntime_last_update = datetime.date.today()

            day_period, period_duration, period_start_time = day_period_params(
                suntime_params, next_sunrise_start)

            if day_period != last_day_period:
                file_list = load_file_list(
                    config_params.pathname, config_params.image_format, day_period)

            selected_image, time_per_image = select_image_seasonal(
                config_params.pathname, day_period, file_list, period_duration, period_start_time)
            if selected_image != last_selected_image:
                set_wallpaper(selected_image, config_params.wallpaper_option)

            time.sleep(max(1, time_per_image))

        else:

            file_list = load_file_list(
                config_params.pathname, config_params.image_format)
            selected_image = select_image_nonseasonal(file_list, now_seconds)
            if selected_image != last_selected_image:
                set_wallpaper(selected_image, config_params.wallpaper_option)
            time.sleep(5)


def load_config():
    '''Loads config file variables and returns settings as a tuple.
    Fallback values are defined for each variable to catch errors.
    If "seasonal" option is selected (i.e. dynamic sunrise/sunset times) location data defaults to
    Melbourne, Australia if not defined.'''

    config = configparser.ConfigParser()
    with open("config.ini", "r", encoding="utf8") as config_file:
        config.read_file(config_file)

        pathname = config.get("GENERAL", "path", fallback=os.getcwd())
        pathname.encode("unicode_escape")
        print(f"Folder path: {pathname}")

        image_format = config.get("GENERAL", "image_format", fallback=r".jpg")
        image_format.lower()
        image_format.encode("unicode_escape")
        print(f"Image format: {image_format}")

        wallpaper_option = config.get(
            "GENERAL", "wallpaper_option", fallback=r"fill")
        wallpaper_option.lower()
        wallpaper_option.encode("unicode_escape")
        print(f"Wallpaper option: {wallpaper_option}")

        seasonal = config.getboolean("GENERAL", "seasonal", fallback=False)
        if seasonal:
            lat = config.get("LOCATION", "latitude", fallback="-37.840935")
            lon = config.get("LOCATION", "longitude", fallback="144.946457")
            elevation = config.getint("LOCATION", "elevation", fallback=31)

    config_return = namedtuple("config_return", [
                               "pathname", "image_format", "wallpaper_option", "seasonal", "lat",
                               "lon", "elevation"])
    return config_return(pathname, image_format, wallpaper_option, seasonal, lat, lon, elevation)


def load_file_list(pathname, image_format, day_period=None):
    '''Loads file list

    Loads file list depending on defined file path, image format, day period (optional) and current
    time (optional)

    If day period is given, file list is sorted numerically [1 ,2, 3] rather than alphabetically
    [1, 10, 11] by using a key that forces string length to take priority

    If day period is not given, then then "seasonal = False" is assumed, and a full file list is
    returned (not sorted)

    [Parameters]
    pathname (str):                 folder path to images
    image_format (str):             image file format, including the 'dot', e.g. .jpg
    day_period (str) [optional]:    "sunrise", "sunset", "day" or "night"

    [Returns]
    file_list(list):                list of images including the file extension

    '''

    if day_period:
        file_list = os.listdir(os.path.join(pathname, day_period))
        file_list = [k for k in file_list if k.isnumeric]
        file_list = [k for k in file_list if image_format in k]
        file_list = sorted(file_list, key=lambda x: (len(x), x))
    else:
        file_list = os.listdir(pathname)
        file_list = [k for k in file_list if image_format in k]
    return file_list


def select_image_seasonal(pathname, day_period, file_list, period_duration, period_start_time):
    '''Selects image when seasonal = True option is selected'''
    now = datetime.datetime.now()
    time_per_image = period_duration / len(file_list)
    index_number = min(int(round(
        (now - period_start_time).total_seconds() / time_per_image, 0)), len(file_list) - 1)
    filepath = os.path.join(pathname, day_period, file_list[index_number])
    print(f"showing file: {file_list[index_number]}")
    return filepath, time_per_image


def select_image_nonseasonal(file_list, now_seconds):
    '''Selects image when seasonal = False option is selected'''
    image_format = os.path.splitext(file_list[0])[1]
    file_list = [os.path.splitext(string)[0] for string in file_list]
    filepath = min(file_list, key=lambda x: abs(
        x-int(math.ceil(now_seconds, 0))))
    filepath = str(filepath).strip() + image_format
    return filepath


def day_period_params(suntime_params,
                      next_sunrise_start):
    '''Returns day period, duration and period start time based on suntime input'''
    now = datetime.datetime.now()
    sunrise_start = suntime_params.sunrise_start
    sunrise_end = suntime_params.sunrise_end
    sunset_start = suntime_params.sunset_start
    sunset_end = suntime_params.sunset_end

    if sunrise_start < now < sunrise_end:
        print("it's sunrise")
        day_period = "sunrise"
        period_duration = (sunrise_end - sunrise_start).total_seconds()
        period_start_time = sunrise_start
    elif sunset_start < now < sunset_end:
        print("it's sunset")
        day_period = "sunset"
        period_duration = (sunset_end - sunset_start).total_seconds()
        period_start_time = sunset_start
    elif sunrise_end < now < sunset_start:
        print("it's daytime")
        day_period = "day"
        period_duration = (sunset_start - sunrise_end).total_seconds()
        period_start_time = sunrise_end
    else:
        print("it's nighttime")
        day_period = "night"
        period_duration = (sunset_end - next_sunrise_start).total_seconds()
        period_start_time = sunset_end
    return day_period, period_duration, period_start_time


def set_wallpaper(filepath, wallpaper_option):
    '''Set wallpaper using Windows API (active desktop) via [pywin32]'''
    # Sets wallpaper by hooking onto the Active Desktop module
    # https://docs.microsoft.com/en-us/windows/win32/api/shlobj_core/ns-shlobj_core-wallpaperopt
    wallpaper_options_dict = {"center": 0x0, "tile": 0x1,
                              "stretch": 0x2, "fit": 0x3, "fill": 0x4, "span": 0x5}
    wallpaper_option = wallpaper_options_dict.get(wallpaper_option)
    iad.set_wallpaper(filepath, wallpaper_option)


if __name__ == "__main__":
    main()
