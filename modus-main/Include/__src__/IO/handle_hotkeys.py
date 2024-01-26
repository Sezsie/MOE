# HotkeyHandler.py

# Description: A class that handles hotkeys for the modus AI assistant. This class is designed to be
# used in conjunction with the keyboard module, which can be installed using pip. The keyboard module
# is a cross-platform module that allows for the detection of keyboard events, such as key presses.

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





