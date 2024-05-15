
#############################################################################################################
# DOCUMENTATION
#############################################################################################################
# AUTHOR: Garrett Thrower
# CONTRIBUTORS: Brian Boggs, Colby McClure

# LAST UPDATED: 2024-15-04
# FUNCTION: An interactive AI assistant that serves the user's needs by executing commands. The AI starts out
# with no ability to execute commands, but can learn to do so through auto-generated code snippets and user
# feedback. The AI can also chat with the user in a conversational manner, although its primary function is to
# execute commands.
#
# PURPOSE: To provide a user-friendly AI assistant that is directed towards PC power users, tech enthusiasts,
# and basically anyone that has dreamed of having their own personal "Jarvis".
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
transcribedAudio = ""
app = None

# settings
debug.setDebugMode(True)

# TODO: add a check for the user's internet connection. If the user is offline, the program should not run and return an error message in a popup window.
# TODO: if the user hasn't set up their OpenAI API key, a popup window should appear asking them to paste their key into a text box, which is then saved to a file.
# TODO: modify the listenandrecord function to record for as long as the hotkey is pressed, then stop recording when the hotkey is released.
# the current implementation is not as user friendly as it could be, since if the audio is too short it doesn't get sent through to the AI without any feedback.

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

    if duration <= 1:
        recording = False
        return "too short"
    
    # Set the recording flag to False
    recording = False
    return audioFile

def regenerate_animation(ui):
    # spawn in a new thread
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(generate_with_codus, "Try that again with a different approach.")
        future.add_done_callback(lambda fut: ui.load_text(fut.result()))

def display_save_UI(code = None):
    app.editor_ui = NamingUI()
    app.editor_ui.show()
    app.editor_ui.add_button("Save", lambda: save_command(app.editor_ui, ml.preprocess(app.editor_ui.textEdit.toPlainText()), code), "Save the command to MODUS's internal database.") 

def save_command(app, command = None, associated_code = None):
    db.add(command, associated_code)
    # close all windows
    app.close()

def create_code_editor_ui(ui):
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
            MODUS.addContext("""If the user's current message is a computer-related command kindly ask them to rephrase their request to be longer. Otherwise, just chat with the user.""")
            
    # finally, now that contexts have been set, chat with the user in a separate thread
    chat_with_modus(userSpeech)
    
    if likely_command:
        # execute the command if found
        moderate_code(db.get(likely_command)[2])
    

#############################################################################################################
# MAIN
#############################################################################################################

# main function with optional text parameter
def main(string = None):
    global recording
    global generate_code
    global transcribedAudio

    # if currently recording or blocked, return
    # TODO: implement the button blocking feature for when any processing is happening
    if recording == True or block_button == True:
        return
    
    # if the string is None, the user has not provided any text input.
    # TODO: add text input option
    if string == None:
        
        # call the listenAndRecord function and store the result
        recordedAudio = listenAndRecord()
        
        # if the audio file was too short, print a message and return
        if recordedAudio == "too short":
            print("Audio file too short. Please try again.")
            os.remove(recordedAudio)
            return
        
        # transcribe the audio and print the result
        transcribedAudio = transcriber.transcribe(recordedAudio)
        
        # discard the audio file since it is no longer needed.
        os.remove(recordedAudio)
    
    prediction = ml.classify(transcribedAudio)
    
    # manage the context of the conversation based on the prediction and other factors
    manage_contexts(prediction, transcribedAudio)

if __name__ == "__main__":  
    # create a HotkeyHandler instance with the hotkey "alt+m" and the main function as the callback
    print("MODUS is running...")
    Handler = HotkeyHandler("alt+m", main)
    
    # aesthetic contexts
    if not db.get_all():
        # TODO: branch to some first-time user message stuff here
        MODUS.addContext("This is the first time you are meeting the user. Introduce yourself, and tell the user that they can get started by asking you to do something.") 
        pass
    else:
        MODUS.addContext("Address the user back by welcoming them back somewhere in your response with an excited tone.") 
      
    # upon starting, greet the user  
    chat_with_modus("Perform the action described above system message.")
        
    # keep the program running with a UI loop
    while True:
        # if QApplication has not been initialized, initialize it
        if not app:
            app = QApplication(sys.argv)
            app.ui = TextEditorUI()
            ui = app.ui
            create_code_editor_ui(ui)

        # if the generate_code flag is set to true, generate code
        if generate_code:
            generate_code = False
            ui.load_text("Loading...")
            QApplication.processEvents()
            
            # load text in a separate thread
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(generate_with_codus, transcribedAudio)
                future.add_done_callback(lambda fut: ui.load_text(fut.result()))
            
            # show the text box UI created above
            ui.show()
            app.exec()