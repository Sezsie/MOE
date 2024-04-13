
#############################################################################################################
# DOCUMENTATION
#############################################################################################################
# AUTHOR: Garrett Thrower
# LAST UPDATED: 2024-09-04
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
import sys

from __src__.IO.handle_hotkeys import HotkeyHandler
from __src__.IO.record_voice import VoiceRecorder

from __src__.AI.apis.transcribe_audio import AudioTranscriber
from __src__.AI.nlp.classifier import RequestClassifier

from __src__.UTILS.utils import Utilities
from __src__.UTILS.utils import DebuggingUtilities
from __src__.IO.handle_ui import TextEditorUI, NamingUI

from time import sleep
from __src__.AI.agents.chat_to_modus import chat_with_modus
from __src__.AI.agents.generate_with_codus import generate_with_codus, save_to_database, moderate_code

import tkinter as tk
from tkinter import simpledialog

# import future
from concurrent.futures import ThreadPoolExecutor
from PySide6.QtWidgets import QApplication

api_key = Utilities.getOpenAIKey()
recorder = VoiceRecorder()
transcriber = AudioTranscriber()
utils = Utilities()
debug = DebuggingUtilities()
ml = RequestClassifier()

dprint = debug.dprint 
recording = False
block_button = False
app = None
generate_code = False
transcribedAudio = ""

# settings
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

  
#############################################################################################################
# MAIN
#############################################################################################################

# main function with optional text parameter
def main(string = None):
    global recording
    global generate_code
    global transcribedAudio

    # if currently recording or blocked, return
    if recording == True or block_button == True:
        return
    
    # if the string is None, the user has not provided any text input.
    if string == None:
        
        # call the listenAndRecord function and store the result
        recordedAudio = listenAndRecord()
        
        # if the audio file was too short, print a message and return
        if recordedAudio == "too short":
            print("Audio file too short. Please try again.")
            return
        
        # transcribe the audio and print the result
        transcribedAudio = transcriber.transcribe(recordedAudio)
        
        # discard the audio file since it is no longer needed.
        os.remove(recordedAudio)
        
    # otherwise, the user has provided text input.
    else:
        transcribedAudio = string
    
    prediction = ml.classify(transcribedAudio)
    
    # chat with MODUS in a separate thread while CODUS processes the user's requests.
    # CODUS is branched through the generate_with_codus function, which is called in the chat_with_modus function.
    thread = threading.Thread(target=chat_with_modus, args=[transcribedAudio])
    thread.start()
    
    # if the prediction is command or user's message contains "I want you to", generate code with CODUS
    if prediction == "command" or transcribedAudio.lower().find("i want you to") != -1:
        generate_code = True

print("MODUS is running...")
Handler = HotkeyHandler("alt+m", main)

def regenerate_animation(ui):
    new_text = generate_with_codus("Try that again in a completely different way.")
    ui.load_text(new_text)
    
def display_command_name():
    app.editor_ui = NamingUI()
    app.editor_ui.show()
    app.editor_ui.add_button("Save", lambda: save_command(app), "Save the command to MODUS's internal database.")
    
def save_command(app):
    # save the text in a variable
    command = app.editor_ui.textEdit.toPlainText()
    # close all open windows
    app.editor_ui.close()
    app.ui.close()
    print(f"Saved command: {command}")
    

if __name__ == "__main__":
    
    # keep the program running with a UI loop
    while True:
        # if QApplication has not been initialized, initialize it
        if not app:
            app = QApplication(sys.argv)
            app.ui = TextEditorUI()
            ui = app.ui
            # set window title
            ui.change_window_title("Generated Code (Click to Edit)")
            # set size of window
            ui.set_size(800, 600)
            # button that regens code in a different way
            ui.add_button("Regenerate", lambda: regenerate_animation(ui), "Regenerate the code in a different way (WARNING: MAY FREEZE THE UI FOR A FEW SECONDS).")
            # execute code currently in editor
            ui.add_button("Execute", lambda: moderate_code(ui.textEdit.toPlainText()), "Execute the code currently in the editor.")
            # save the code in the editor to MODUS's internal database and execute it
            ui.add_button("Save and Execute", lambda: display_command_name(), "Save the code to MODUS's internal database and execute it.")

        if generate_code:
            generate_code = False
            ui.load_text("Loading...")
            QApplication.processEvents()
            ui = app.ui
            print(f"Current Text: {ui.textEdit.toPlainText()}")
            # load text into separate thread
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(generate_with_codus, transcribedAudio)
                future.add_done_callback(lambda fut: ui.load_text(fut.result()))  
            ui.show()
            app.exec()