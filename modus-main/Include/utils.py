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
    def __init__(self):
        self.timers = {}
        
        self.os = platform.system()
        self.osVersion = platform.release()
        
    def getOS(self):
        return self.os
    
    def getOSVersion(self):
        return self.osVersion
    
    def getOSVersionName(self):
        return self.osVersionName
    

    
    def clearScreen(self):
        if self.os == "Windows":
            os.system("cls")
        else:
            os.system("clear")
            
           
            
    # starts a thread that will delete a file when either given its path or the file object itself after a specified amount of time (in seconds).
    def scheduleRemoval(self, file, time):
        
        if isinstance(file, str):
            threading.Timer(time, os.remove, args=[file]).start()
        else:
            threading.Timer(time, os.remove, args=[file.name]).start()
          
            
    def openFile(self, file):
        if isinstance(file, str):
            os.startfile(file)
        else:
            os.startfile(file.name)
            
            
    def openFolder(self, folder):
        if isinstance(folder, str):
            os.startfile(folder)
        else:
            os.startfile(folder.name)
        
        
        
    def openWebsite(self, url):
        webbrowser.open(url)


    def openWebsiteInBrowser(self, url):
        webbrowser.open(url, new=2)
        
    # returns the length of an audio file in seconds   
    def checkAudioLength(self, audioFile):
        with contextlib.closing(wave.open(audioFile, 'r')) as f:
            frames = f.getnframes()
            rate = f.getframerate()
            duration = frames / float(rate)
            return duration
        
        
        
    # starts a timer with the given name
    def startTimer(self, timer_name):
        self.timers[timer_name] = time.time()

    # returns the elapsed time since the named timer was started
    def stopTimer(self, timer_name):
        if timer_name in self.timers:
            elapsed_time = time.time() - self.timers[timer_name]
            return round(elapsed_time, 3)
        else:
            print(f"Timer with name '{timer_name}' not found.")
            return None

        
        
        