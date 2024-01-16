
#############################################################################################################
# DOCUMENTATION
#############################################################################################################

# AUTHOR: Sezzie
# LAST UPDATED: 2024-16-01
# FUNCTION: An interactive AI assistant that serves the user's needs by executing commands. The AI
# will interpret and remember the user's commands and preferences, and will learn to adapt to the user's own
# unique style of communication. Should the AI be unable to perform a command, the user will be able to modify
# the AI's memory so the mistake is not repeated in the future.
#
# PURPOSE: To make the user's life easier by automating tasks in a convenient and intelligent way.

#############################################################################################################
# IMPORTS
#############################################################################################################

# TO DO: Disallow the user from triggering the same hotkey until MODUS has stopped listening.
from handle_hotkeys import HotkeyHandler
from record_voice import VoiceRecorder
from utils import Utilities
from time import sleep

utils = Utilities()

recording = False

def listenAndRecord():
    global recording
    if recording:
        return
    
    recording = True
    
    recorder = VoiceRecorder()
    
    print("Listening...")
    
    # create an instance of Recorder and call the record method
    audioFile = recorder.record()

    print(f"Recording saved as: {audioFile}")
    utils.scheduleRemoval(audioFile, 1)
    
    recording = False
    return audioFile


def main():
    global recording
    
    # output: .wav file
    recordedAudio = listenAndRecord()
    
    # TO DO: Add code to transcribe the audio file
    

    






if __name__ == "__main__":
    Handler = HotkeyHandler("alt+m", main)
    
    # the loop is here to prevent the program from exiting. This is because the keyboard module uses a separate thread to detect key presses.
    while True:
        sleep(1)
        pass