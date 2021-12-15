def main():
    # General Dependencies
    import datetime
    import time
    from suntime import suntime

    pathname, image_format, wallpaper_option, seasonal, lat, lon, elevation = load_config()

    # Initialise wallpaper time variables
    suntime_last_update = None
    day_period = None
    period_duration = None
    last_day_period = None
    period_start_time = None
    last_selected_image = None

    # Start Loop #
    while(True):

        now = datetime.datetime.now()
        now_seconds = now.hour * 3600 + now.minute * 60 + now.second

        if seasonal:
            today = datetime.date.today()  # get today's date without time
            if today != suntime_last_update:

                # Get sunrise/sunset time and durations
                sunrise_start, sunrise_end, sunset_start, sunset_end = suntime(
                    0, lat, lon, elevation)
                # prev_sunset_end = suntime(-1, lat, lon, elevation)[3]
                next_sunrise_start = suntime(1, lat, lon, elevation)[0]
                print("sunrise starts @: %s" % sunrise_start)
                print("sunrise ends @: %s" % sunrise_end)
                print("sunset starts @: %s" % sunset_start)
                print("sunset ends @: %s" % sunset_end)
                print("the time is now: %s" % now)
                suntime_last_update = today

            day_period, period_duration, period_start_time = day_period_params(
                now, sunrise_start, sunrise_end, sunset_start, sunset_end, next_sunrise_start)

            if day_period != last_day_period:
                file_list = load_file_list(pathname, image_format, day_period)

            selected_image, time_per_image = select_image_seasonal(
                pathname, day_period, file_list, period_duration, period_start_time, now)
            if selected_image != last_selected_image:
                set_wallpaper(selected_image, wallpaper_option)

            time.sleep(max(1, time_per_image))

        else:

            file_list = load_file_list(pathname, image_format)
            selected_image = select_image_nonseasonal(file_list, now_seconds)
            if selected_image != last_selected_image:
                set_wallpaper(selected_image, wallpaper_option)
            time.sleep(5)


def load_config():
    # Loads config file variables and returns settings as a tuple.
    # Fallback values are defined for each variable to catch errors.
    # If "seasonal" option is selected (i.e. dynamic sunrise/sunset times) location data defaults to Melbourne, Australia if not defined.

    import configparser
    config = configparser.ConfigParser()
    config.read_file(open("config.ini"))

    import os
    pathname = config.get("GENERAL", "path", fallback=os.getcwd())
    pathname.encode("unicode_escape")
    print("Folder path: %s" % pathname)

    image_format = config.get("GENERAL", "image_format", fallback=r".jpg")
    image_format.lower()
    image_format.encode("unicode_escape")
    print("Image format: %s" % image_format)

    wallpaper_option = config.get(
        "GENERAL", "wallpaper_option", fallback=r"fill")
    wallpaper_option.lower()
    wallpaper_option.encode("unicode_escape")
    print("Wallpaper option: %s" % wallpaper_option)

    seasonal = config.getboolean("GENERAL", "seasonal", fallback=False)
    if seasonal:
        lat = config.get("LOCATION", "latitude", fallback="-37.840935")
        lon = config.get("LOCATION", "longitude", fallback="144.946457")
        elevation = config.getint("LOCATION", "elevation", fallback=31)

    return pathname, image_format, wallpaper_option, seasonal, lat, lon, elevation


def load_file_list(pathname, image_format, day_period=None):
    # Loads file list depending on defined file path, image format, day period (optional) and current time (optional)
    # If day period is given, file list is sorted numerically [1 ,2, 3] rather than alphabetically [1, 10, 11] by using a key that forces string length to take priority
    # If day period is not given, then then "seasonal = False" is assumed, and a full file list is returned (not sorted)
    import os
    if day_period:
        file_list = os.listdir(os.path.join(pathname, day_period))
        file_list = [k for k in file_list if k.isnumeric()]
        file_list = [k for k in file_list if (image_format) in k]
        file_list = sorted(file_list, key=lambda x: (len(x), x))
    else:
        file_list = os.listdir(pathname)
        file_list = [k for k in file_list if (image_format) in k]
    return file_list


def select_image_seasonal(pathname, day_period, file_list, period_duration, period_start_time, now):
    import os
    time_per_image = period_duration / len(file_list)
    index_number = min(int(round(
        (now - period_start_time).total_seconds() / time_per_image, 0)), len(file_list) - 1)
    filepath = os.path.join(pathname, day_period, file_list[index_number])
    print("showing file: %s" % file_list[index_number])
    return filepath, time_per_image


def select_image_nonseasonal(file_list, now_seconds):
    import os
    import math
    image_format = os.path.splitext(file_list[0])[1]
    file_list = [os.path.splitext(string)[0] for string in file_list]
    filepath = min(file_list, key=lambda x: abs(
        x-int(math.ceil(now_seconds, 0))))
    filepath = str(filepath).strip() + image_format
    return filepath


def day_period_params(now, sunrise_start, sunrise_end, sunset_start, sunset_end, next_sunrise_start):
    if (now > sunrise_start) and (now < sunrise_end):
        print("it's sunrise")
        day_period = "sunrise"
        period_duration = (sunrise_end - sunrise_start).total_seconds()
        period_start_time = sunrise_start
    elif (now > sunset_start) and (now < sunset_end):
        print("it's sunset")
        day_period = "sunset"
        period_duration = (sunset_end - sunset_start).total_seconds()
        period_start_time = sunset_start
    elif (now > sunrise_end) and (now < sunset_start):
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
    # Sets wallpaper by hooking onto the Active Desktop module
    import iad
    # https://docs.microsoft.com/en-us/windows/win32/api/shlobj_core/ns-shlobj_core-wallpaperopt
    wallpaper_options_dict = {"center": 0x0, "tile": 0x1,
                              "stretch": 0x2, "fit": 0x3, "fill": 0x4, "span": 0x5}
    wallpaper_option = wallpaper_options_dict.get(wallpaper_option)
    iad.set_wallpaper(filepath, wallpaper_option)


if __name__ == "__main__":
    main()
