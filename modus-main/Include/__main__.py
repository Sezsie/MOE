
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


#############################################################################################################
# IMPORTS
#############################################################################################################

from handle_hotkeys import HotkeyHandler
from record_voice import VoiceRecorder
from transcribe_audio import AudioTranscriber

from utils import Utilities
from time import sleep

import os

#############################################################################################################
# GLOBAL VARIABLES
#############################################################################################################


# TO DO: Figure out how to store the API key in a more secure way.
# For now, check in modus-main\.gitignore and grab the API key from there.
apiKeyFile = open("modus-main/.gitignore/api-key.txt", "r")
recording = False
api_key = ""

# Read the API key from the file and store it as a string
with apiKeyFile as f:  
    api_key = f.read().replace("\n", "")
    f.close()

# Create instances of the Recorder, Transcriber, and Utilities classes
recorder = VoiceRecorder()
transcriber = AudioTranscriber(api_key)
utils = Utilities()

#############################################################################################################
# FUNCTIONS
#############################################################################################################

# Function to start recording audio
def listenAndRecord():
    global recording
    
    # Set the recording flag to True
    recording = True
    
    print("Listening...")
    
    # Call the record method of the Recorder instance
    audioFile = recorder.record()

    print(f"Recording saved as: {audioFile}")
    
    # Check the length of the audio file. If it's too short, delete it and return "too short". Otherwise, return the audio file
    if utils.checkAudioLength(audioFile) <= 1:
        os.remove(audioFile)
        recording = False
        return "too short"
    
    # Set the recording flag to False
    recording = False
    return audioFile


# Main function
def main():
    global recording
    global api_key
    
    # If currently recording, return
    if recording:
        return
    
    # Call the listenAndRecord function and store the result
    recordedAudio = listenAndRecord()
    
    # If the audio file was too short, print a message and return
    if recordedAudio == "too short":
        print("Audio file too short. Please try again.")
        return
    
    # Start a timer
    utils.startTimer("MODUSResponseTime")
    
    print("Transcribing...")
    
    # Transcribe the audio and print the result
    transcribedAudio = transcriber.transcribe(recordedAudio)
    print(transcribedAudio)
    
    # Stop the timer and print the execution time
    executionTime = utils.stopTimer("MODUSResponseTime")
    print(f"Total API response time: {executionTime} seconds")
  
#############################################################################################################
# MAIN
#############################################################################################################

# If this script is the main module, execute the main function when the hotkey is pressed
if __name__ == "__main__":
    Handler = HotkeyHandler("alt+m", main)
    
    print("MODUS is running...")
    
    # Keep the program running with a loop that sleeps for 1 second at a time
    while True:
        sleep(1)
        pass