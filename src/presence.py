from pypresence import Presence, Activity 
import time
import win32gui
import ctypes
import json
onLaunch = True
EnumWindows = ctypes.windll.user32.EnumWindows
EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int))
GetWindowText = ctypes.windll.user32.GetWindowTextW
GetWindowTextLength = ctypes.windll.user32.GetWindowTextLengthW
IsWindowVisible = ctypes.windll.user32.IsWindowVisible
titles = []
storedTitle = ""
def foreach_window(hwnd, lParam):
    if IsWindowVisible(hwnd):
        length = GetWindowTextLength(hwnd)
        buff = ctypes.create_unicode_buffer(length + 1)
        GetWindowText(hwnd, buff, length + 1)
        titles.append(buff.value)
    return True
	
def checkforupdate():
	global rpcActive
	global storedTitle
	global titles
	print("checking..")
	EnumWindows(EnumWindowsProc(foreach_window), 0)
	aa = [ string for string in titles if  "Ableton Live" in string ]
	searchstring = ''.join(aa)
	titles = []
	checkForUntitled = [ string for string in aa if  "Untitled" in string ]
	if checkForUntitled != []:
		forCheck = searchstring.split("-")[0]
	else:
		forCheck = searchstring.split("[")[0]
		forCheck = forCheck.split("*")[0]
	if forCheck is "" and rpcActive:
		RPC.clear()
		print("cleared")
		rpcActive = False
	details = "Project: {}".format(forCheck)
	if rpcActive and storedTitle != forCheck:
		storedTitle = forCheck
		RPC.update(large_image = "main", state=data["phrase"],details=details, start=time.time())
		print("updated")
	elif forCheck is not "":
		RPC.connect()
		RPC.update(large_image = "main", state=data["phrase"],details=details, start=time.time())
		storedTitle = forCheck
		rpcActive = True
	print("StoredTitle = {} // rpcActive = {}".format(storedTitle, rpcActive))

while True:
	if onLaunch:
		with open('config.json') as userCfg:
			data = json.load(userCfg)
		onLaunch = False
		print(data)
		RPC = Presence(data["client_id"])
		rpcActive = False
	checkforupdate()
	time.sleep(15)