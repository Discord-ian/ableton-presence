from pypresence import Presence, exceptions
import time
import json
import requests
import ctypes
import os
import webbrowser
import logging
import platform
import random
import string
#  TODO: port entire project over to C# and figure out a solution for Linux/OSX
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


def foreach_window(hwnd, lParam):  # https://sjohannes.wordpress.com/2012/03/23/win32-python-getting-all-window-titles/
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
    aa = [string for string in titles if "Ableton Live" in string]  # checks to see if any process with the window name
    # ableton live exists
    searchstring = ''.join(aa)
    titles = []
    checkForUntitled = [string for string in aa if "Untitled" in string]  # special case for untitled project
    if checkForUntitled:
        forCheck = searchstring.split("-")[0]
        forCheck = forCheck.strip()
    else:
        forCheck = searchstring.split("[")[0]
        forCheck = forCheck.split("*")[0]
        forCheck = forCheck.strip()
    # RPC section
    try: 
        if forCheck == "" and rpcActive:
            RPC.clear()  # kills the RPC when there is no Ableton found to be running and it is stated as currently active
            rpcActive = False  # inform everything else that the RPC is closed
            storedTitle = ""
        details = "Project: {}".format(forCheck)
        if rpcActive and forCheck != storedTitle:
            storedTitle = forCheck
            RPC.update(large_image="main", state=phrase, details=details, start=time.time())
        elif forCheck != "" and not rpcActive:
            RPC.update(large_image="main", state=phrase, details=details, start=time.time())
            storedTitle = forCheck
            rpcActive = True
    except Exception as e:
        print(e)
    outputDebug()


def checkIfLatest():
    currentVersion = "1.9.1"
    logging.info("Checking for update @ https://discordian.dev/dev/latestversion")
    try:
        check = requests.get(url="https://discordian.dev/dev/latestversion")
        if check.json()["version"] != currentVersion:
            box = ctypes.windll.user32.MessageBoxW(0,
                                                   "There is an update available. You are on version {}, and the "
                                                   "latest release version is {}.".format(
                                                       currentVersion, check.json()["version"]), "Version Checker", 1)
            if box == 1:
                logging.debug("Opening webbrowser to https://github.com/Discord-ian/ableton-presence/releases")
                webbrowser.open('https://github.com/Discord-ian/ableton-presence/releases')
                os._exit(0)
            else:
                logging.info("Skipping update. . .")
        else:
            logging.info("No update found.")
    except Exception as e:
        logging.error(e)


def data_collect():
    appdata_path = os.getenv("appdata")
    path = os.getenv("APPDATA") + "/AbletonPresence"
    os.chdir(os.getenv("APPDATA"))
    if os.path.isdir("AbletonPresence"):
        try:
            with open("AbletonPresence/main_config.json", "r") as tosave:
                user_prefs = json.load(tosave)
        except Exception as e:
            logging.error("Warning: {}".format(e)) 
    else:
        os.mkdir(appdata_path+"/AbletonPresence")
        os.chdir(path)
        try:
            about = requests.get("https://discordian.dev/ableton/about.txt")
            version = requests.get("https://discordian.dev/ableton/version.json")
            main_config = requests.get("https://discordian.dev/ableton/main_config.json")
            with open("about.txt", "w+") as out:
                out.write(about.text)
            with open("version.json", "w+") as out:
                json.dump(version.json(), out)
            with open("main_config.json", "w+") as out:
                json.dump(main_config.json(), out)
        except Exception as e:
            logging.error("Warning: {}".format(e))
        box = ctypes.windll.user32.MessageBoxW(0,
                                               "Would you like to send data (OS version, Ableton Presence version) to "
                                               "improve the program? This is the only time you will be asked",
                                               "Analytics Collection", 1)
        if box == 1:
            with open("main_config.json", "r") as tosave:
                user_prefs = json.load(tosave)
            user_prefs["collect_data"] = True
            user_prefs["has_asked"] = True
        else:
            with open("main_config.json", "r") as tosave:
                user_prefs = json.load(tosave)
            user_prefs["collect_data"] = False
            user_prefs["has_asked"] = True
        with open("main_config.json", "w") as out:
            json.dump(user_prefs, out)
    if user_prefs["collect_data"]:
        if user_prefs.get("id") is None:
            os.chdir(path)
            user_prefs["id"] = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(16))
            # thank you stack overflow
            # note: this isnt meant to be cryptographically secure or what not.
            # just a way to hopefully avoid me counting 1 computer as multiple ppl
            with open("main_config.json", "w") as out:
                json.dump(user_prefs, out)
        os_v = "{} {} {}".format(platform.system(), platform.release(), platform.version())
        version = "1.9.1"  # TODO: make this a real version number please
        logging.info("Sent analytical data to https://api.discordian.dev/analytics, read more @ "
                     "https://github.com/Discord-ian/ableton-presence/blob/master/src/AbletonPresence/about.txt")
        requests.post(url="https://api.discordian.dev/analytics", data={'os': os_v, 'v': version, "id": user_prefs["id"]})


logging.info("If you get an error stating that the RPC handshake failed, Discord is probably not open")
while True:
    if onLaunch:
        RPC = Presence("609115046051840050")  # discord application ID
        try:
            RPC.connect()
        except exceptions.InvalidPipe:  # TODO: fix generic exception
            onLaunch = True
            logging.warning("RPC handshake failed... trying again in 15 seconds")
        else:
            onLaunch = False
            checkIfLatest()
            try:
                #data_collect()  # not mission critical, can fail and still have app work
                logging.info("Skipping data collection as it is not important.")
            except Exception as e:  # TODO: fix generic exception
                logging.error(e)
            phrase = "Making Music"
        rpcActive = False
    else:
        checkForUpdate()
    time.sleep(15)  # blocking statement is ok in this case
