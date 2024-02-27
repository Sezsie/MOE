
#############################################################################################################
# DOCUMENTATION
#############################################################################################################
# AUTHOR: Sezzie
# LAST UPDATED: 2024-25-01
# FUNCTION: An interactive AI assistant that serves the user's needs by executing commands. The AI
# will interpret and remember the user's commands and preferences, and will learn to adapt to the user's own
# unique style of communication. Should the AI be unable to perform a command, the user will be able to modify
# the AI's memory directly so the mistake is not repeated in the future.
#
# PURPOSE: To make the user's life easier by automating tasks using natural language.
#############################################################################################################



#############################################################################################################
# IMPORTS AND GLOBALS
#############################################################################################################
import threading
import os

from __src__.IO.handle_hotkeys import HotkeyHandler
from __src__.IO.record_voice import VoiceRecorder
from __src__.AI.apis.transcribe_audio import AudioTranscriber

from __src__.UTILS.utils import Utilities
from __src__.UTILS.utils import DebuggingUtilities

from time import sleep
from __src__.AI.agents.chat_to_modus import chat_with_modus
from __src__.AI.agents.generate_with_codus import generate_with_codus

import tkinter as tk
from tkinter import simpledialog

api_key = Utilities.getOpenAIKey()
recorder = VoiceRecorder()
transcriber = AudioTranscriber()
utils = Utilities()
debug = DebuggingUtilities()
dprint = debug.dprint 
recording = False

# Settings
debug.setDebugMode(True)

#############################################################################################################
# FUNCTIONS
#############################################################################################################

# start recording audio
def listenAndRecord():
    global recording
    
    # set the recording flag to True
    recording = True
    
    # call the record method of the Recorder instance
    audioFile = recorder.record()
    # check the length of the audio file. if it's too short, delete it and return "too short". Otherwise, return the audio file
    duration = utils.checkAudioLength(audioFile)
    # round off duration to 1 decimal place.
    duration = round(duration, 1)
    
    dprint(f"Recording saved as: {audioFile}")
    dprint(f"Recording duration: {duration} seconds")

    if duration <= 1.5:
        recording = False
        return "too short"
    
    # Set the recording flag to False
    recording = False
    return audioFile

# this is just a testing function that makes a simple dialog box to get text input from the user.
# this is never used by the user, as the main form of interaction with MODUS is through voice commands.
def get_text_w_UI():
    root = tk.Tk()
    root.withdraw()  # hide the main window (we just need the dialog)
    
    # this line pops up the dialog box, waits for input, then destroys the root window
    user_input = simpledialog.askstring(title="Text Input", prompt="Type something here:")
    
    return user_input


# main function with optional text parameter
def main(string = None):
    global recording
    
    transcribedAudio = None

    # if currently recording, return
    if recording:
        return
    
    if string == None:
        
        # call the listenAndRecord function and store the result
        recordedAudio = listenAndRecord()
        
        # if the audio file was too short, print a message and return
        if recordedAudio == "too short":
            print("Audio file too short. Please try again.")
            return
        
        print("Transcribing...")
        
        # transcribe the audio and print the result
        transcribedAudio = transcriber.transcribe(recordedAudio)
        
        # discard the audio file since it is no longer needed.
        os.remove(recordedAudio)
        
    # chat with MODUS in a separate thread while CODUS processes the user's requests.
    thread = threading.Thread(target=chat_with_modus, args=[transcribedAudio or string])
    thread.start()
    
    # TO DO: use machine learning to check if the user's request is similar to a previous command, and if so, use the code from the relevant command. otherwise, use CODUS to generate code.
    # thread = threading.Thread(target=check_request_similarity, args=[transcribedAudio])
    # thread.start()
    
    # generate code with CODUS in a separate thread. not ready for use, so I return here.
    return
    thread = threading.Thread(target=generate_with_codus, args=[transcribedAudio or string])
    thread.start()
    
# TO DO: try to reduce the delay between the user's request and the AI's response.
  
#############################################################################################################
# MAIN
#############################################################################################################

Handler = HotkeyHandler("alt+m", main)

# If this script is the main module, execute the main function when the hotkey is pressed
if __name__ == "__main__":
    
    print("MODUS is running...")
    
    # Keep the program running with a loop that sleeps for 1 second at a time
    while True:
        text = get_text_w_UI()
        main(text)
        sleep(1)