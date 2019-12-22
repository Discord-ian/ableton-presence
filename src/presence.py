from pypresence import Presence, Activity 
import time
import win32gui
import requests
import ctypes
import os
import webbrowser
onLaunch = True
EnumWindows = ctypes.windll.user32.EnumWindows
EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int))
GetWindowText = ctypes.windll.user32.GetWindowTextW
GetWindowTextLength = ctypes.windll.user32.GetWindowTextLengthW
IsWindowVisible = ctypes.windll.user32.IsWindowVisible
titles = []
storedTitle = ""

# from 
def foreach_window(hwnd, lParam):
	if IsWindowVisible(hwnd):
		length = GetWindowTextLength(hwnd)
		buff = ctypes.create_unicode_buffer(length + 1)
		GetWindowText(hwnd, buff, length + 1)
		titles.append(buff.value)
	return True


def checkForUpdate():
	global rpcActive
	global storedTitle
	global titles
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
		forCheck = forCheck.strip()
	if forCheck is "" and rpcActive:
		RPC.clear()  # kills the RPC when there is no Ableton found to be running and it is stated as currently active
		rpcActive = False # inform everything else that the RPC is closed
		storedTitle = ""
		print("closed connection")
	details = "Project: {}".format(forCheck)
	print("'" + forCheck + "'")
	if rpcActive and forCheck != storedTitle:
		storedTitle = forCheck
		RPC.update(large_image = "main", state=phrase,details=details, start=time.time())
		print("updated")
	elif forCheck is not "" and not rpcActive:
		RPC.update(large_image = "main", state=phrase,details=details, start=time.time())
		storedTitle = forCheck
		rpcActive = True
	print("StoredTitle = {} // rpcActive = {}".format(storedTitle, rpcActive))


def checkIfLatest():
	currentVersion = "1.1v.3"
	check = requests.get(url="https://im-stuck-in.space/dev/latestversion")
	if check.json()[0] != currentVersion:
		print("wrong version!")
		box = ctypes.windll.user32.MessageBoxW(0, "There is an update available", "Version Checker", 1)
		if box == 1:
			webbrowser.open('https://github.com/Discord-ian/ableton-presence/releases')
			os._exit(0)
		print(box)


while True:
	if onLaunch:
		# with open('config.json') as userCfg:
		#	data = json.load(userCfg) might add back at a later date
		RPC = Presence("609115046051840050") # discord application ID
		try:
			RPC.connect()
		except Exception as e:
			onLaunch = True
			print("trying again.")
		else:
			onLaunch = False
			checkIfLatest()
			phrase = "Making Music"
			print("check")
		rpcActive = False
	checkForUpdate()
	time.sleep(15)