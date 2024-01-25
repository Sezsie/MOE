
#############################################################################################################
# DOCUMENTATION
#############################################################################################################
# AUTHOR: Sezzie
# LAST UPDATED: 2024-19-01
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

from handle_hotkeys import HotkeyHandler
from record_voice import VoiceRecorder
from transcribe_audio import AudioTranscriber

from utils import Utilities
from utils import DebuggingUtilities

from time import sleep
from chat_to_modus import chat_with_modus
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

# Function to start recording audio
def listenAndRecord():
    global recording
    
    # Set the recording flag to True
    recording = True
    
    # Call the record method of the Recorder instance
    audioFile = recorder.record()
    # Check the length of the audio file. If it's too short, delete it and return "too short". Otherwise, return the audio file
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

def get_text_w_UI():
    root = tk.Tk()
    root.withdraw()  # Hide the main window (we just need the dialog)
    
    # This line pops up the dialog box, waits for input, then destroys the root window
    user_input = simpledialog.askstring(title="Text Input", prompt="Type something here:")
    
    return user_input


# Main function with optional text parameter
def main(string = None):
    global recording
    
    transcribedAudio = None

    # If currently recording, return
    if recording:
        return
    
    if string == None:
        # Call the listenAndRecord function and store the result
        recordedAudio = listenAndRecord()
        
        # If the audio file was too short, print a message and return
        if recordedAudio == "too short":
            print("Audio file too short. Please try again.")
            return
        
        print("Transcribing...")
        
        # Transcribe the audio and print the result
        transcribedAudio = transcriber.transcribe(recordedAudio)
        
        # discard the audio file since it is no longer needed.
        os.remove(recordedAudio)
        
    # chat with MODUS in a separate thread while CODUS (not yet implemented) processes the user's requests.
    thread = threading.Thread(target=chat_with_modus, args=[transcribedAudio or string])
    thread.start()
       
       
    # TO DO: use machine learning to check if the user's request is similar to a previous command, and if so, use the code from the relevant command.
    # thread = threading.Thread(target=check_request_similarity, args=[transcribedAudio])
    # thread.start()
    
# TO DO: try tor educe the delay between the user's request and the AI's response.
  
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
        if text == None:
            break
        else:
            main(text)
        sleep(1)
        pass