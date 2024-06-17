# HotkeyHandler.py

# Description: A class that handles hotkeys for the MOE AI assistant. This class is designed to be
# used in conjunction with the keyboard module.

import keyboard

class HotkeyHandler:
    def __init__(self, hotkey, function):
        self.hotkey = hotkey
        self.function = function
        keyboard.add_hotkey(self.hotkey, self.function)

    def disconnect(self):
        keyboard.unhook_all()
        
    def add(self):
        keyboard.add_hotkey(self.hotkey, self.function)
        
    def remove(self):
        keyboard.remove_hotkey(self.hotkey)
        
    def waitForKey(self):
        keyboard.wait(self.hotkey)