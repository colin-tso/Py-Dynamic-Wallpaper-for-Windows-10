# Py Dynamic Wallpaper for Windows-10
**A python-based program for Windows 10 that dynamically changes and fades your desktop wallpaper based on the time of day.**  
Unlike most implementations, this utility allows for:
1. **Fading** between wallpaper images by hooking onto the Windows API and enabling Active Desktop via `pywin32`
2. **Dynamic** sunrise/sunset times based on your location and time of year
3. Requires no internet connection

## How to Use
1. Download the 2 files under [releases](https://github.com/GrandTheftGelato/Py-Dynamic-Wallpaper-for-Windows-10/releases) into the same folder:  
   * `py_dynamic_wallpaper.exe`  
   * `config.ini`
  
  
2. Fill in the required parameters in `config.ini`
   * `path`- the folder that contains all of your images. Defaults to the same directory as the app if not defined.
   * `image_format` - image file extension of your images. Defaults to `.jpg` if not defined.
   * `wallpaper_option` - shall be either : `center`, `tile`, `stretch`, `fit`, `fill` or `span`. Defaults to `fill`if not defined.
   * `seasonal` - shall be either `True` or `False` - setting this to true allows the program take into account actual sunrise and sunset times depending on location and time of year.  Defaults to `False` if not defined.
   * `latitude`, `longitude` and `elevation` - the corresponding information of your location. Defaults to Melbourne, Australia if not defined.
  
   For example:  
```ini
[GENERAL]
path = D:\firewatch
image_format = .jpg
wallpaper_option = fill
seasonal = True

[LOCATION]
latitude = -37.840935
longitude = 144.946457
elevation = 31
```
  
  
3. If you are using the static sunrise and sunset time option, following Step 3A, otherwise follow Step 3B.  
    - 3A. Set up a folder containing all the images you would like to use for the dynamic wallpaper with numbered filenames according to the time of day in seconds.  The app is currently hard-set to check whether your wallpaper requires refreshing every 5 seconds - the CPU load is very low, so don't worry!  
	**Note: You do not need to have an image for every second of the day — the app will find the largest matching value/filename according to the time of day.**  
    You may use the example `firewatch` directory in this respository containing numbered images (@ 1920 x 1080 resolution) captured from the [Lakeside Animation by Louis Coyle](https://dribbble.com/shots/1941754-Lakeside-Animation)  
  
      For example, `2:34:05 pm` is `14 * 60 * 60 + 34 * 60 + 5 = 52445 seconds`  
      File `52445.jpg` will be displayed at `2:35:00 pm` if the next largest image number is `52561.jpg --> 2:36:01 pm`.  
	
   - 3B. Set up a root folder containing folders named `day`, `night`, `sunrise` and `sunset`. Place corresponding images into the folders, sequenced in the order you would like them to be diplayed for each time of day. It does not matter what numbers you give the images as the app will just play them in sequence. Each image will be displayed for a fixed time based on the the duration of the time period.  
   For example, if I have 20 images for a `day` period of 9 hours, then each image in the day folder will be displayed for 2.22 seconds.  
   **Note: The maximum refresh rate is limited to 1 second in order not to overload the Windows API with wallpaper changes.**  
   You may use the example `firewatch2` directory in this respository containing numbered images (@ 1920 x 1080 resolution) captured from the [Lakeside Animation by Louis Coyle](https://dribbble.com/shots/1941754-Lakeside-Animation)  

4. Run `py_dynamic_wallpaper.exe`. You may wish to add the app to your startup programs or configure it to run when you logon via the **Task Scheduler** in Windows 10.

## Running the Source Code
To run the source code, you will require the following Python libraries:  
* `configparser`
* `pywin32`
* `ephem`
  
You can install the libraries via `pip`:  
```bash
pip install configparser pywin32 ephem
```
  
If you run into any issues with loading `pywin32` modules, you may need to manually copy `pythoncom37.dll` and `pywintypes37.dll` to the correct directory. The exact locations will vary depending on your Python installation, however they will similar to the paths below:  
  
Copy from:  
`C:\Users\[USERNAME]\AppData\Local\Programs\Python\Python37\Lib\site-packages\pywin32_system32`  
to  
`C:\Users\[USERNAME]\AppData\Local\Programs\Python\Python37\Lib\site-packages\win32`

## To Do List
- [x] Add option to take into account local sunrise and sunset times depending on location and time of year
