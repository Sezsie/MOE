import os
import wave
import contextlib
import webbrowser
import platform
import threading
import time
import re

# a collection of utility functions that are commonly used throughout the project
# some of these arent used at the moment, but I have other plans for them in the future.

class Utilities:
    @staticmethod
    def getOS():
        return platform.system()

    @staticmethod
    def openWebsite(url):
        webbrowser.open(url)

    @staticmethod
    def openWebsiteInBrowser(url):
        webbrowser.open(url, new=2)

    @staticmethod
    def checkAudioLength(audioFile):
        with contextlib.closing(wave.open(audioFile, 'r')) as f:
            frames = f.getnframes()
            rate = f.getframerate()
            duration = frames / float(rate)
            return duration

    @staticmethod
    def getOpenAIKey():
        # use getprojectdirectory to get the project directory
        print(FileUtilities.getProjectDirectory())
        api_key_file_path = os.path.join(FileUtilities.getProjectDirectory(), "__auth__", "api-key.txt")
        
        # check if the file exists
        if not os.path.exists(api_key_file_path):
            return None # return None if the file doesn't exist, this can be used to prompt the user to enter their key (when thats actually implemented)

        # open the file and read the key
        with open(api_key_file_path, "r") as apiKeyFile:
            api_key = apiKeyFile.read().strip()

        return api_key


class DebuggingUtilities:
    debugMode = False
    
    def __init__(self):
        self.timers = {}
    
    @classmethod
    # set the debug mode to True or False, or toggle it if no argument is given
    def setDebugMode(self, mode):
        if mode == True:
            self.debugMode = True
        elif mode == False:
            self.debugMode = False
        else:
            self.debugMode = not self.debugMode
    
    # prints a message with the [DEBUG] tag. only used in this debug class. 
    def dprint(self, message):
        if DebuggingUtilities.debugMode:
            print("[DEBUG] " + message)
    
    # starts a timer with the given name
    def startTimer(self, timer_name):
        self.timers[timer_name] = time.time()
        self.dprint(f"Timer '{timer_name}' started.")

    # returns and prints the elapsed time since the named timer was started
    def stopTimer(self, timer_name):
        if timer_name in self.timers:
            elapsed_time = time.time() - self.timers[timer_name]
            self.dprint(f"Timer '{timer_name}' elapsed time: {elapsed_time} seconds.")
            return round(elapsed_time, 3)
        else:
            self.dprint(f"Timer with name '{timer_name}' not found.")
            return None
    
    # check a currently running timer if it exists
    def checkTimer(self, timer_name):
        if timer_name in self.timers:
            elapsed_time = time.time() - self.timers[timer_name]
            return round(elapsed_time, 3)
        else:
            return None
        
    # removes a timer by name
    def removeTimer(self, timer_name):
        if timer_name in self.timers:
            del self.timers[timer_name]
        else:
            self.dprint(f"Timer with name '{timer_name}' not found.")
  
            
class FileUtilities:
    @staticmethod
    # starting at this file, get the project directory with a certain name
    def getProjectDirectory(name="modus-reborn"):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        while os.path.basename(current_dir) != name:
            current_dir = os.path.dirname(current_dir)
        return current_dir
        
    
    @staticmethod
    def scheduleRemoval(file, time):
        if isinstance(file, str):
            threading.Timer(time, os.remove, args=[file]).start()
        else:
            threading.Timer(time, os.remove, args=[file.name]).start()

    @staticmethod
    def openFile(file):
        if isinstance(file, str):
            os.startfile(file)
        else:
            os.startfile(file.name)

    @staticmethod
    def openFolder(folder):
        if isinstance(folder, str):
            os.startfile(folder)
        else:
            os.startfile(folder.name)
        