# Py Dynamic Wallpaper for Windows-10
A python-based dynamic wallpaper utility for Windows 10

# How to Use
1. Download and extracct the zip archive containing 2 files into the same folder:
  a. py_dynamic_wallpaper.exe
  b. config.ini

2. Set up a folder containing all the images you would like to use for the dynamic wallpaper, with numbered filenames according to the time of day in seconds. The app will find the largest matching value/filename according to the time of day.  
You may use the example directory containing numbered images captured from [Lakeside Animation by Louis Coyle](https://dribbble.com/shots/1941754-Lakeside-Animation)
  
  For example, `2:34:05 pm` is `14 * 60 * 60 + 34 * 60 + 5 = 52445`  
  filename `52445.jpg` will be displayed at 2:35 pm if there are no other image files that satisfy the criteria.
