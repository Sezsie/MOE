
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

print("MODUS is starting...")

#############################################################################################################
# IMPORTS AND GLOBALS
#############################################################################################################
import os
import sys

from __src__.IO.handle_hotkeys import HotkeyHandler
from __src__.IO.record_voice import VoiceRecorder

from __src__.AI.apis.transcribe_audio import AudioTranscriber
from __src__.AI.nlp.classifier import RequestClassifier

from __src__.UTILS.utils import Utilities
from __src__.UTILS.utils import DebuggingUtilities
from __src__.IO.handle_ui import TextEditorUI, NamingUI
from __src__.DATA.manage_database import Database
from __src__.AI.apis.contact_openai import AIHandler

from __src__.AI.agents.chat_to_modus import chat_with_modus
from __src__.AI.agents.generate_with_codus import generate_with_codus, moderate_code

# import future
from concurrent.futures import ThreadPoolExecutor
from PySide6.QtWidgets import QApplication

api_key = Utilities.getOpenAIKey()
recorder = VoiceRecorder()
transcriber = AudioTranscriber()
utils = Utilities()
debug = DebuggingUtilities()
ml = RequestClassifier()
db = Database()
ai = AIHandler.getInstance()
MODUS = ai.getAgent("MODUS")

dprint = debug.dprint 
recording = False
block_button = False
generate_code = False
ran_once = False
transcribedAudio = ""
app = None

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

def regenerate_animation(ui):
    new_text = generate_with_codus("Try that again in a completely different way.")
    ui.load_text(new_text)

def display_save_UI(code = None):
    app.editor_ui = NamingUI()
    app.editor_ui.show()
    app.editor_ui.add_button("Save", lambda: save_command(app.editor_ui, ml.preprocess(app.editor_ui.textEdit.toPlainText()), code), "Save the command to MODUS's internal database.") 

def save_command(app, command = None, associated_code = None):
    db.add(command, associated_code)
    # close all windows
    app.close()


def manage_contexts(prediction, userSpeech, likely_command = None):
    global generate_code
    global ran_once
    
    ran_once = True
    cleantext = ml.preprocess(userSpeech)
    likely_command = db.semantic_search(cleantext)
    
    # functional contexts
    # if a command is found, no need to generate code, just perform the command
    if likely_command:
        MODUS.addContext(f"Excitedly tell the user that you're on it.")
        # if no command is found, generate code
    else:
        if prediction == "command" or userSpeech.lower().find("i want you to") != -1:
            generate_code = True
            MODUS.addContext("Inform the user that you'll try to do that. Ask them to double check the code on the screen.")
        elif prediction == "conversational":
            MODUS.addContext("""If the user's message is a computer-related command, please ask the user to rephrase their request. Give them hints, such as including the phrase 'I want you to'. Otherwise, just chat with the user.""")
            
    # finally, now that contexts have been set, chat with the user in a separate thread
    chat_with_modus(userSpeech)
    
    if likely_command:
        # execute the command if found
        moderate_code(db.get(likely_command)[2])
        
    # wipe the system messages so that the AI will not get its responses confused
    MODUS.wipeSystemMessages()
    

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
    
    prediction = ml.classify(transcribedAudio)
    
    # manage the context of the conversation based on the prediction and other factors
    manage_contexts(prediction, transcribedAudio)

if __name__ == "__main__":  
    # aesthetic contexts
    # if the database has no commands, add context to MODUS to let them know that they are meeting the user for the first time
    if not db.get_all() and not ran_once:
        MODUS.addContext("This is the first time you are meeting the user. Tell them that right now, you don't know very much, but that can change with their help.")
    else:
        MODUS.addContext("Excitedly welcome the user back somewhere in your response.") 
    
    # create a HotkeyHandler instance with the hotkey "alt+m" and the main function as the callback
    print("MODUS is running...")
    Handler = HotkeyHandler("alt+m", main)
        
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
            # button that regenerates different code to satisfy the user's request
            ui.add_button("Regenerate", lambda: regenerate_animation(ui), "Regenerate the code in a different way (WARNING: MAY FREEZE THE UI FOR A FEW SECONDS).")
            # execute code currently in editor
            ui.add_button("Execute", lambda: moderate_code(ui.textEdit.toPlainText()), "Execute the code currently in the editor.")
            # save the code in the editor to MODUS's internal database and execute it
            ui.add_button("Save", lambda: display_save_UI(ui.textEdit.toPlainText()), "Save the code so MODUS can remember it for later.")

        if generate_code:
            generate_code = False
            ui.load_text("Loading...")
            QApplication.processEvents()
            
            # load text in a separate thread
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(generate_with_codus, transcribedAudio)
                future.add_done_callback(lambda fut: ui.load_text(fut.result()))
                
            ui.show()
            app.exec()