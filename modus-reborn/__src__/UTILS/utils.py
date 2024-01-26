# Basic utility functions for the modus package.

import os
import wave
import contextlib
import webbrowser
import platform
import threading
import time
import re


# Define the class

class Utilities:
            @staticmethod
            def getOS():
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
                api_key_file_path = FileUtilities.getProjectDirectory() + "\\__auth__\\api-key.txt"
                
                # Open the file and read the key
                with open(api_key_file_path, "r") as apiKeyFile:
                    api_key = apiKeyFile.read().strip()

                return api_key

            
            @staticmethod
            def extract_text_by_header(markdown_text, header):
                """
                Extracts and returns the text under a specified Markdown header until an empty line is encountered.
                
                :param markdown_text: String containing the entire Markdown content.
                :param header: The Markdown header to find (e.g., 'my_response' for '## my_response').
                :return: Extracted text as a string or None if the header is not found.
                """
                # Make the header safe for inclusion in a regex pattern
                header_pattern = re.escape(header)
                # Craft the regex pattern to find the header and capture all text that follows
                # until the next empty line
                pattern = fr"##\s*{header_pattern}\s*\n+((?:[^\n]+\n)*(?:[^\n]+))(?=\n\s*\n|$)"
                matches = re.findall(pattern, markdown_text, re.DOTALL)
                return matches[0].strip() if matches else None


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
  
            
class FileUtilities:
    # simply returns the topmost directory of the project (Include)
    @staticmethod
    def getProjectDirectory():
        return os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
        