# General Dependencies
import configparser
import datetime
import time
import os

# Load suntime module
from suntime import suntime

# Load Active Desltop module
import iad

# Load Config File
config = configparser.ConfigParser()
config.read_file(open("config.ini"))

# Get folder path for images
pathname = config.get("GENERAL", "path", fallback = os.getcwd())
pathname.encode("unicode_escape")
print("Folder path: %s" % pathname)

# Get image format
image_format = config.get("GENERAL", "image_format", fallback = r".jpg")
image_format.lower()
image_format.encode("unicode_escape")
print("Image format: %s" % image_format)

# Get wallpaper option
wallpaper_option = config.get("GENERAL", "wallpaper_option", fallback = r"fill")
wallpaper_option.lower()
wallpaper_option.encode("unicode_escape")
print("Wallpaper option: %s" % wallpaper_option)
wp_options_dict = {"center": 0x0, "tile": 0x1, "stretch": 0x2, "fit": 0x3, "fill": 0x4, "span": 0x5} # https://docs.microsoft.com/en-us/windows/win32/api/shlobj_core/ns-shlobj_core-wallpaperopt
wallpaper_option = wp_options_dict.get(wallpaper_option)

# Check if config file asks for dynamic sunrise/sunset
seasonal = config.getboolean("GENERAL", "seasonal", fallback = False)
if seasonal:
        today = now = datetime.date.today() # get today's date without time
        # Get location data from config file - defaults to Melbourne, Australia
        lat = config.get("LOCATION", "latitude", fallback = "-37.840935")
        lon = config.get("LOCATION", "longitude", fallback = "144.946457")
        elevation = config.getint("LOCATION", "elevation", fallback = 31)

# Initialise wallpaper time
wallpaper_time = -1
suntime_date = None
day_period = None
period_duration = None
new_file_list = False
transition_start_time = None
index_number = None

# Start Loop #

#time.sleep(1)

while(True):

        now = datetime.datetime.now() # get current time
        now_seconds = now.hour * 3600 + now.minute * 60 + now.second # calculate current time in seconds

        if seasonal:
                
                today = datetime.date.today() # get today's date without time
                if today != suntime_date:

                        # Get sunrise/sunset time and durations
                        sunrise_start, sunrise_end, sunset_start, sunset_end = suntime(0, lat, lon, elevation)
                        prev_sunset_end = suntime(-1, lat, lon, elevation)[3]
                        next_sunrise_start = suntime(1, lat, lon, elevation)[0]
                        print("sunrise starts @: %s" % sunrise_start)
                        print("sunrise ends @: %s" % sunrise_end)
                        print("sunset starts @: %s" % sunset_start)
                        print("sunset ends @: %s" % sunset_end)
                        print("the time is now: %s" % now)
                        suntime_date = today

                if (now > sunrise_start) and (now < sunrise_end):
                        print("it's sunrise")
                        if day_period != "sunrise":
                                new_file_list = True
                                day_period = "sunrise"
                                period_duration = (sunrise_end - sunrise_start).total_seconds()
                                transition_start_time = sunrise_start
                elif (now > sunset_start) and (now < sunset_end):
                        print("it's sunset")
                        if day_period != "sunset":
                                new_file_list = True
                                day_period = "sunset"
                                period_duration = (sunset_end - sunset_start).total_seconds()
                                transition_start_time = sunset_start
                elif (now > sunrise_end) and (now < sunset_start):
                        print("it's daytime")
                        if day_period != "day":
                                new_file_list = True
                                day_period = "day"
                                period_duration = (sunset_start - sunrise_end).total_seconds()
                                transition_start_time = sunrise_end
                else:
                        print("it's nighttime")
                        if day_period != "night":
                                new_file_list = True
                                day_period = "night"
                                period_duration = (sunset_end - next_sunrise_start).total_seconds()
                                transition_start_time = sunset_end

                if new_file_list:
                        file_list = os.listdir(os.path.join(pathname, day_period)) # List all files in directory defined by 'pathname' and under folder 'sunrise'
                        file_list = [string.lower() for string in file_list] # Convert filename list to lowercase
                        file_list = [k for k in file_list if (image_format) in k] # Filter for only file extensions defined by 'image_format'
                        file_list = [os.path.splitext(string)[0] for string in file_list] # Get file list without extension
                        file_list = [k for k in file_list if k.isnumeric()] # Remove non-numeric image file names from list
                        file_list = [int(string) for string in file_list] # convert filename to integer value
                        file_list.sort()
                        file_list = [str(string).strip() + image_format for string in file_list]
                        time_per_image = period_duration / len(file_list) # calculate time to display each image in seconds

                new_index_number = min(int(round((now - transition_start_time).total_seconds() / time_per_image,0)), len(file_list) - 1)
                if index_number != new_index_number:
                        index_number = new_index_number
                        filepath = os.path.join(pathname, day_period, file_list[index_number])
                        iad.set_wallpaper(filepath, wallpaper_option)
                print("showing file: %s" % file_list[index_number])
                time.sleep(max(1,time_per_image))
                
        else:
                # Get file list and filter for chosen image file format only
                file_list = os.listdir(pathname) # List all files in directory defined by 'pathname'
                file_list = [string.lower() for string in file_list] # Convert filename list to lowercase
                file_list = [k for k in file_list if (image_format) in k] # Filter for only file extensions defined by 'image_format'
                file_list = [os.path.splitext(string)[0] for string in file_list] # Get file list without extension
                file_list = [k for k in file_list if k.isnumeric()] # Remove non-numeric image file names from list
                file_list = [int(string) for string in file_list] # convert filename to integer value  
                file_list = [i for i in file_list if i <= now_seconds] # return only values less than current time in seconds
                closest_time = max(file_list) # return largest matching value compared to current time in seconds

                if wallpaper_time != closest_time: # check if wallpaper is current
                        wallpaper_time = closest_time # save wallpaper update time
                        filename = str(max(file_list)).strip() + image_format # generate filename with file extension per 'image_format'
                        filepath = os.path.join(pathname,filename) # generate full file path
                        iad.set_wallpaper(filepath, wallpaper_option)
                time.sleep(5)
