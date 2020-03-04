from pypresence import Presence, Activity
import time
import win32gui
import requests
#from infi.systray import SysTrayIcon py2exe fails to run
import ctypes
import os
import webbrowser
import logging

dev_level = logging.INFO
onLaunch = True
EnumWindows = ctypes.windll.user32.EnumWindows
EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int))
GetWindowText = ctypes.windll.user32.GetWindowTextW
GetWindowTextLength = ctypes.windll.user32.GetWindowTextLengthW
IsWindowVisible = ctypes.windll.user32.IsWindowVisible
titles = []
storedTitle = ""

logging.basicConfig(level=dev_level)


def blacklist(systray):
    addtoblacklist(storedTitle)


def call_quit(systray):
    os._exit(0)


def checkupdate(systray):
    checkIfLatest()


def disable_blacklist(systray):
    print("the blacklist has been disabled")


#menu_options = (("Check for Updates", None, checkupdate),)
#systray = SysTrayIcon("icon.ico", "Ableton Presence", menu_options, on_quit=call_quit)
#systray.start()


def addtoblacklist(title):
    checkifblacklisted(title)


def checkifblacklisted(title):
    print("OK")


def foreach_window(hwnd, lParam): # https://sjohannes.wordpress.com/2012/03/23/win32-python-getting-all-window-titles/
    if IsWindowVisible(hwnd):
        length = GetWindowTextLength(hwnd)
        buff = ctypes.create_unicode_buffer(length + 1)
        GetWindowText(hwnd, buff, length + 1)
        titles.append(buff.value)
    return True


def outputDebug():
    logging.info("StoredTitle = {} // rpcActive = {}".format(storedTitle, rpcActive))


def checkForUpdate():
    global rpcActive
    global storedTitle
    global titles
    EnumWindows(EnumWindowsProc(foreach_window), 0)
    aa = [string for string in titles if "Ableton Live" in string]
    searchstring = ''.join(aa)
    titles = []
    checkForUntitled = [string for string in aa if "Untitled" in string]
    if checkForUntitled != []:
        forCheck = searchstring.split("-")[0]
        forCheck = forCheck.strip()
    else:
        forCheck = searchstring.split("[")[0]
        forCheck = forCheck.split("*")[0]
        forCheck = forCheck.strip()
    if forCheck is "" and rpcActive:
        RPC.clear()  # kills the RPC when there is no Ableton found to be running and it is stated as currently active
        rpcActive = False  # inform everything else that the RPC is closed
        storedTitle = ""
        outputDebug()
    details = "Project: {}".format(forCheck)
    if rpcActive and forCheck != storedTitle:
        storedTitle = forCheck
        RPC.update(large_image="main", state=phrase, details=details, start=time.time())
        outputDebug()
    elif forCheck is not "" and not rpcActive:
        RPC.update(large_image="main", state=phrase, details=details, start=time.time())
        storedTitle = forCheck
        rpcActive = True
        outputDebug()


def checkIfLatest():
    currentVersion = "1.2.1"
    logging.info("Checking for update @ https://im-stuck-in.space/dev/latestversion")
    try:
        check = requests.get(url="https://im-stuck-in.space/dev/latestversion")
        if check.json()[0] != currentVersion:
            box = ctypes.windll.user32.MessageBoxW(0,
                                                   "There is an update available. You are on version {}, and the latest release version is {}.".format(
                                                       currentVersion, check.json()[0]), "Version Checker", 1)
            if box == 1:
                logging.debug("Opening webbrowser to https://github.com/Discord-ian/ableton-presence/releases")
                webbrowser.open('https://github.com/Discord-ian/ableton-presence/releases')
                os._exit(0)
            else:
                logging.info("Skipping update. . .")
        else:
            logging.info("No update found.")
    except Exception as e:
        logging.error("Ran into " + e)


while True:
    if onLaunch:
        # with open('config.json') as userCfg:
        #	data = json.load(userCfg) might add back at a later date
        RPC = Presence("609115046051840050")  # discord application ID
        logging.info("If you get an error stating that the RPC handshake failed, Discord is probably not open")
        try:
            RPC.connect()
        except Exception as e:
            onLaunch = True
            logging.warning("RPC handshake failed... trying again in 15 seconds")
        else:
            onLaunch = False
            checkIfLatest()
            phrase = "Making Music"
        rpcActive = False
    checkForUpdate()
    time.sleep(15)
