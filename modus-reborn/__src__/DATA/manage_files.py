# File Manager class
# Purpose: The purpose of this class is to provide a structured way to create, destroy, and manage files in the system across platforms.
# Each file in the MODUS system is managed by this class, and the appropriate files will be initialized in the user's directory on windows, and in the user's home directory on linux.

# import ui classes
from __src__.IO.handle_ui import NamingUI

import platform
import os
import shutil

desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')

class FileManager:
    _shared_state = {}
    
    def __init__(self):
        self.__dict__ = self._shared_state
        # on initialization, save the user's operating system and create the necessary directories.
        # topLevel is the directory that holds all the other directories in the project. gets initialized in the firstTimeSetup method.
        # gets set to C:\Users\(whatever the user's name is)\MODUS on windows, and ~/MODUS on linux.
        if not self._shared_state:
            self.OS = FileManager.getOS()
            self.topLevel = os.path.join(os.path.expanduser("~"), "MODUS")
            self.firstTimeSetup()
        
    # create the necessary directories based on the user's operating system.
    def firstTimeSetup(self):
        # if the MODUS directory already exists, return.
        if os.path.exists(self.topLevel):
            print("MODUS directory already exists.")
            return
        
        # a list of what directories/files to create in the topLevel directory upon first time setup.
        desiredDirectories = ["bin", "data", "temp", "logs", "models", "temp/audio", "temp/scripts", "data/auth", "data/databases", "data/auth/api-key.txt"]
        
        print("Setting up directories...")
        os.makedirs(self.topLevel, exist_ok=True)
        
        # for every directory in the list, create it in the topLevel directory.
        for directory in desiredDirectories:
            full_path = os.path.join(self.topLevel, directory)
            if '.' in directory:  # if the directory has an extension, it's a file
                os.makedirs(os.path.dirname(full_path), exist_ok=True)  # create the parent directory
                open(full_path, 'a').close()  # create the file
            else:
                os.makedirs(full_path, exist_ok=True)  # create the directory
        
        # if the openai api key file doesn't contain a key, prompt the user to enter one.
        if not self.getOpenAIKey():
            self.AIKeyPrompt()
        
    def AIKeyPrompt(self):
        # locate the api-key.txt file in the data/auth directory
        keyfile = self.locateFile("api-key.txt")
        
        # create a naming UI object
        namingUI = NamingUI()
        # set the window title
        namingUI.setWindowTitle("Welcome!")
        # change the label text
        namingUI.change_label("To use MODUS, please enter your OpenAI API key below.")
        # set the window size
        namingUI.set_size(500, 300)
        # write the text in the text box to the keyfile
        namingUI.add_button("Submit", lambda: [self.writeToFile(keyfile, namingUI.textEdit.toPlainText()), namingUI.close()], "Get started with MODUS!")
        # load the UI
        namingUI.show()
        namingUI.app.exec()

    # get API key from the api-key.txt file
    def getOpenAIKey(self):
        file = self.locateFile("api-key.txt")
        if file:
            with open(file, "r") as f:
                return f.read().strip()
        
    # move a file from one location to another    
    def copyTo(self, file, destination):
        # copy the file to the destination
        shutil.copy(file, destination)
        return destination 
            
    # create a file with a specified name and location, and optional content. supports writing to file with binary data, so that's nifty!
    def createFile(self, location, name, optionalContent=None):
        print(f"Creating file: {name} @ {location}")
        # create the directory if it doesn't exist
        os.makedirs(location, exist_ok=True)
        
        # create a file in the specified location and add optional content if specified.
        with open(os.path.join(location, name), "w") as f:
            if optionalContent:
                # if the content is a string, write it to the file
                if isinstance(optionalContent, str):
                    f.write(optionalContent)
                # else, if its raw binary data, write it in binary mode.
                else:
                    with open(os.path.join(location, name), "wb") as f:
                        f.write(optionalContent)
                        
        return os.path.join(location, name)
      
         
    # recursively search through the top level directory and all of its subdirectories to find a file with a specified name.
    def locateFile(self, name):
        for root, dirs, files in os.walk(self.topLevel):
            if name in files:
                return os.path.join(root, name)
        return None
    
    def locateDirectory(self, name):
        for root, dirs, files in os.walk(self.topLevel):
            if name in dirs:
                return os.path.join(root, name)
        return None
                    
    def deleteFile(self, name):
        # use the locateFile func to find the file, and delete it if it exists.
        file = self.locateFile(name)
        if file:
            os.remove(file)
            print(f"Deleted file: {name}")
        else:
            print(f"File {name} not found.")
        
    def doesFileExist(self, name):
        # check if the file exists by using the locateFile func
        file = self.locateFile(name)
        if file:
            return True
        return False
    
    def createDirectory(self, location, name):
        print(f"Creating directory: {name} @ {location}")
        # create a directory in the specified location
        os.makedirs(os.path.join(location, name))
    
    def writeToFile(self, file, content):
        with open(file, "w") as f:
            f.write(content)
    
    @staticmethod
    def getOS():
        return platform.system()
        

if __name__ == "__main__":
    # create a file manager object
    fm = FileManager()
    print(fm.OS)
    print(fm.topLevel)