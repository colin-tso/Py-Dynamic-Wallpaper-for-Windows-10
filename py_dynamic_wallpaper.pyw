import configparser
import datetime
import time
import os
import ctypes
from typing import List

import pythoncom
import pywintypes
import win32gui
from win32com.shell import shell, shellcon

# Load Config File
config = configparser.ConfigParser()
config.read_file(open("config.ini"))

# Get folder path for images
pathname = config.get("GENERAL", "path", fallback = os.getcwd())
pathname.encode("unicode_escape")
print(pathname)

# Set image format
image_format = config.get("GENERAL", "image_format", fallback = r".jpg")
image_format.lower()
image_format.encode("unicode_escape")
print(image_format)

# Set wallpaper option
wallpaper_option = config.get("GENERAL", "wallpaper_option", fallback = r"fill")
wallpaper_option.lower()
wallpaper_option.encode("unicode_escape")
print(wallpaper_option)
wp_options_dict = {"center": 0x0, "tile": 0x1, "stretch": 0x2, "fit": 0x3, "fill": 0x4, "span": 0x5}
wallpaper_option = wp_options_dict.get(wallpaper_option)
print(wallpaper_option)

#wait = input("PRESS ENTER TO CONTINUE.")

# Initialise variables
wallpaper_time = -1

# Active Desktop Functions #
user32 = ctypes.windll.user32

def _make_filter(class_name: str, title: str):
	"""https://docs.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-enumwindows"""

	def enum_windows(handle: int, h_list: list):
		if not (class_name or title):
			h_list.append(handle)
		if class_name and class_name not in win32gui.GetClassName(handle):
			return True  # continue enumeration
		if title and title not in win32gui.GetWindowText(handle):
			return True  # continue enumeration
		h_list.append(handle)

	return enum_windows


def find_window_handles(parent: int = None, window_class: str = None, title: str = None) -> List[int]:
	cb = _make_filter(window_class, title)
	try:
		handle_list = []
		if parent:
			win32gui.EnumChildWindows(parent, cb, handle_list)
		else:
			win32gui.EnumWindows(cb, handle_list)
		return handle_list
	except pywintypes.error:
		return []


def force_refresh():
	user32.UpdatePerUserSystemParameters(1)


def enable_activedesktop():
	"""https://stackoverflow.com/a/16351170"""
	try:
		progman = find_window_handles(window_class='Progman')[0]
		cryptic_params = (0x52c, 0, 0, 0, 500, None)
		user32.SendMessageTimeoutW(progman, *cryptic_params)
	except IndexError as e:
		raise WindowsError('Cannot enable Active Desktop') from e


def set_wallpaper(image_path: str, use_activedesktop: bool = True):
	if use_activedesktop:
		enable_activedesktop()
	pythoncom.CoInitialize()
	iad = pythoncom.CoCreateInstance(shell.CLSID_ActiveDesktop, None, pythoncom.CLSCTX_INPROC_SERVER, shell.IID_IActiveDesktop)
	iad.SetWallpaper(str(image_path), 0)
	iad.SetWallpaperOptions(wallpaper_option, 0)
	iad.ApplyChanges(shellcon.AD_APPLY_ALL)
	force_refresh()

# Start Loop #

while(True):

        now = datetime.datetime.now() # get current time
        now_seconds = now.hour * 3600 + now.minute * 60 + now.second # calculate current time in seconds

        # Get file list and filter for chosen image file format only
        file_list = os.listdir(pathname) # List all files in directory defined by 'pathname'
        file_list = [string.lower() for string in file_list] # Convert filename list to lowercase
        file_list = [k for k in file_list if (image_format) in k] # Filter for only file extensions defined by 'image_format'
        file_list = [os.path.splitext(string)[0] for string in file_list] # Get file list without extension
        file_list = [k for k in file_list if k.isnumeric()] # Remove non-numeric image file names from list
        file_list = [int(string) for string in file_list] # convert to filename to integer value  
        file_list = [i for i in file_list if i <= now_seconds] # return only values less than current time in seconds
        closest_time = max(file_list) # return largest matching value compared to current time in seconds

        if wallpaper_time != closest_time: # check if wallpaper is current 
                wallpaper_time = closest_time
                filename = str(max(file_list)).strip() + image_format
                filepath = os.path.join(pathname,filename)
                # Update wallpaper
                if __name__ == '__main__':
                        set_wallpaper(filepath)
        time.sleep(5)
