# Basic utility functions for the modus package.

import os
import wave
import contextlib
import webbrowser
import platform
import threading
import time

# Define the class

class Utilities:
            @staticmethod
            def getOS():
                return os

            @staticmethod
            def getOSVersion():
                return platform.platform()

            @staticmethod
            def getOSVersionName():
                return platform.system()

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
                apiKeyFile = open("D:\\Documents\\GitHub\\ModusREBORN\\.gitignore\\sensitive\\api-key.txt", "r")
                api_key = ""

                with apiKeyFile as f:  
                    api_key = f.read().replace("\n", "")
                    
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
        
    def clearScreen(self):
        if Utilities.getOS == "Windows":
            os.system("cls")
        else:
            os.system("clear")