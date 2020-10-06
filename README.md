# Py Dynamic Wallpaper for Windows-10
**A python-based dynamic wallpaper utility for Windows 10 that changes based on your system clock**.  
Unlike most implementations, this utility allows for **fading** between wallpaper images by hooking onto the Windows API and enabling Active Desktop via `pywin32`.

## How to Use
1. Download the 2 files under [releases](https://github.com/GrandTheftGelato/Py-Dynamic-Wallpaper-for-Windows-10/releases) into the same folder:  
   * `py_dynamic_wallpaper.exe`  
   * `config.ini`
  
2. Set up a folder containing all the images you would like to use for the dynamic wallpaper, with numbered filenames according to the time of day in seconds. **Note: You do not need to have an image for every second of the day — the app will find the largest matching value/filename according to the time of day.**  
You may use the example `firewatch` directory in this respository containing numbered images (@ 1920 x 1080 resolution) captured from the [Lakeside Animation by Louis Coyle](https://dribbble.com/shots/1941754-Lakeside-Animation)  
  
   For example, `2:34:05 pm` is `14 * 60 * 60 + 34 * 60 + 5 = 52445 seconds`  
   File `52445.jpg` will be displayed at `2:35:00 pm` if the next largest image number is `52561.jpg --> 2:36:01 pm`.  
  
3. Fill in the required parameters in `config.ini`
   * `path`- the folder that contains all of your images. Defaults to the same directory as the app if not defined.
   * `image_format` - image file extension of your images. Defaults to `.jpg` if not defined.
   * `wallpaper_option` - shall be either : `center`, `tile`, `stretch`, `fit`, `fill` or `span`. Defaults to `fill`if not defined.  
  
   For example:  
```ini
[GENERAL]
path = D:\firewatch
image_format = .jpg
wallpaper_option = fill
```
  
4. Run `py_dynamic_wallpaper.exe`. The app is currently hard-set to check whether your wallpaper requires refreshing every 5 seconds - the CPU load is very low, so don't worry!  You may wish to add the app to your startup programs or configure it to run when you logon via the **Task Scheduler** in Windows 10.

## Running the Source Code
You will require the following Python libraries:  
* `configparser`
* `pywin32`
  
You can install the libraries via `pip`:  
```bash
pip install configparser pywin32
```
  
If you run into any issues with loading `pywin32` modules, you may need to manually copy `pythoncom37.dll` and `pywintypes37.dll` to the correct directory. The exact locations will vary depending on your Python installation, however they will similar to the paths below:  
  
Copy from:  
`C:\Users\[USERNAME]\AppData\Local\Programs\Python\Python37\Lib\site-packages\pywin32_system32`  
to  
`C:\Users\[USERNAME]\AppData\Local\Programs\Python\Python37\Lib\site-packages\win32`
