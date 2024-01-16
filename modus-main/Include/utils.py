# Basic utility functions for the modus package.

import os
import sys
import time
import math
import random
import string
import datetime
import webbrowser
import subprocess
import platform
import json
import threading

# Define the class

class Utilities:
    def __init__(self):
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


        