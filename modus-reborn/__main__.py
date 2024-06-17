
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

#############################################################################################################
# IMPORTS AND GLOBALS
#############################################################################################################

print("Initializing...")

import os

from __src__.IO.handle_hotkeys import HotkeyHandler
from __src__.IO.record_voice import VoiceRecorder

from __src__.AI.apis.transcribe_audio import AudioTranscriber
from __src__.AI.nlp.classifier import RequestClassifier

from __src__.UTILS.utils import Utilities, DebuggingUtilities
from __src__.IO.handle_ui import TextEditorUI, NamingUI
from __src__.DATA.manage_database import Database
from __src__.DATA.manage_files import FileManager
from __src__.AI.apis.contact_openai import AIHandler
from __src__.IO.code_executor import CodeExecutor

# import the chat_with_MOE and generate_with_codus functions from the agents modules
from __src__.AI.agents.chat_to_moe import chat_with_MOE
from __src__.AI.agents.generate_with_codus import generate_with_codus

# import future
from concurrent.futures import ThreadPoolExecutor
from PySide6.QtWidgets import QApplication

import pygame

print("Starting...")

# class instances
files = FileManager()
utils = Utilities()
debug = DebuggingUtilities()
recorder = VoiceRecorder()
transcriber = AudioTranscriber()
ml = RequestClassifier()
db = Database()
code_executor = CodeExecutor()

# neccessary global variables
transcribedAudio = ""
sfx_directory = os.path.join("modus-reborn", "__resources__", "sfx")

# state variables
recording = False
block_button = False
generate_code = False

# set debug mode to True to print debug messages
debug.setDebugMode(True)
# wipe the database on startup for testing purposes
# db.wipe_database()

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
    pygame.mixer.init()
    
    # set the recording flag to True
    recording = True
    
    # play a sound to indicate that recording has started
    pygame.mixer.music.load(os.path.join(sfx_directory, "MOE_active.mp3"))
    pygame.mixer.music.play()
    
    # call the record method of the Recorder instance
    audioFile = recorder.record()
    
    # play a sound to indicate that recording has stopped
    pygame.mixer.music.load(os.path.join(sfx_directory, "MOE_inactive.mp3"))
    pygame.mixer.music.play()
    
    # set the recording flag to False
    recording = False
    return audioFile


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
    ui.add_button("Execute", lambda: code_executor.moderate_code(ui.textEdit.toPlainText()), "Execute the code currently in the editor.")
    # save the code in the editor to MOE's internal database and execute it
    ui.add_button("Save", lambda: display_save_UI(ui.textEdit.toPlainText()), "Save the code so MOE can remember it for later.")
    
def regenerate_animation(ui):
    # spawn in a new thread
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(generate_with_codus, "Try that again with a different approach.")
        future.add_done_callback(lambda fut: ui.load_text(fut.result()))

def display_save_UI(code = None):
    editor_ui = NamingUI()
    editor_ui.show()
    editor_ui.add_button("Save", lambda: save_command(editor_ui, ml.preprocess(editor_ui.textEdit.toPlainText()), code), "Save the command to MOE's internal database.") 
    
def AIKeyPrompt():
    # locate the api-key.txt file in the data/auth directory
    keyfile = files.locateFile("api-key.txt")
    
    # create a naming UI object
    namingUI = NamingUI()
    
    # set the window title
    namingUI.setWindowTitle("MOE")
    
    # change the label text
    namingUI.change_label("Welcome! Please enter your OpenAI API key below, and we can get started!")
    
    # set the window size
    namingUI.set_size(500, 300)
    
    # write the text in the text box to the keyfile
    namingUI.add_button("Submit", lambda: [files.writeToFile(keyfile, namingUI.textEdit.toPlainText()), namingUI.close()], "Get started with MOE!")
    
    # load the UI
    namingUI.show()
    namingUI.app.exec()


def manage_contexts(prediction, userSpeech, likely_command = None):
    global generate_code
    global ran_once
    
    ran_once = True
    cleantext = ml.preprocess(userSpeech)
    likely_command = db.semantic_search(cleantext)
    
    # functional contexts
    # if a command is found, no need to generate code, just perform the command
    if likely_command:
        MOE.addContext(f"Excitedly tell the user that you're on it. Do not ask questions.")
        # if no command is found, generate code
    else:
        # TODO: fix the prediction classifier. I feel its a problem with not enough data, but I'm not sure.
        if userSpeech.lower().find("i want you to") != -1:
            generate_code = True
            MOE.addContext("Tell the user that you're on it then as for feedback on the code that will shortly appear on their screen. Do not say anything that contains code or is unrelated to the previous sentence.")
        else:
            MOE.addContext("""If the user is making a computer-related request, inform them in one sentence that they can use the phrase "I want you to" to get you to do something. Otherwise, just chat with the user.""")
            
    # finally, now that contexts have been set, chat with the user in a separate thread
    chat_with_MOE(userSpeech)
    
    if likely_command:
        # execute the command if found
        code_executor.execute_code((db.get(likely_command)[2]))
    

#############################################################################################################
# MAIN
############################################################################################################# 

# instantiate the AIHandler class and get the MOE agent after the user has entered their OpenAI key
ai = AIHandler.getInstance()
MOE = ai.getAgent("MOE")

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
        
        # check the length of the audio file. if it's too short, delete it and return "too short". Otherwise, return the audio file
        duration = utils.checkAudioLength(recordedAudio)
        
        # round off duration to 1 decimal place.
        duration = round(duration, 1)
        
        # if the audio file was too short, print a message and return
        if duration <= 1:
            print("Audio file too short. Please try again.")
            os.remove(recordedAudio)
            return
        
        # transcribe the audio and print the result
        transcribedAudio = transcriber.transcribe(recordedAudio)
        
        # discard the audio file since it is no longer needed.
        os.remove(recordedAudio)
    
    # predict the class of the user's input speech, returns either "command" or "conversational"
    prediction = ml.classify(transcribedAudio)
    
    # manage the context of the conversation based on the prediction and other factors
    manage_contexts(prediction, transcribedAudio)



if __name__ == "__main__":  
    # create a HotkeyHandler instance with the hotkey "alt+m" and the main function as the callback
    print("MOE is running...")
    Handler = HotkeyHandler("alt+m", main)
    
    # aesthetic contexts
    # if the settings file does not have any data, the user is new and should be greeted as such
    if not files.locateFile("settings.json"):
        # for now create a settings file with no data. there will be a user settings class that will handle this in the future, so the only purpose this serves is to check if the user is new.
        files.createFile(files.locateDirectory("data"), "settings.json", "{}")
        MOE.addContext("""This is the first time you are meeting the user. Introduce yourself with a clever paragraph, describing what you can do, how you learn, and your limitations.
                         Let the user know that they can press the buttons alt and m at the same time to talk to you.""")
        pass
    else:
        # otherwise, the user is returning and should be welcomed back
        MOE.addContext("Succinctly welcome the user back, then optimistically tell them that you're ready to assist them with their needs. Do not ask questions.") 
      
    # upon starting, greet the user  
    chat_with_MOE("Perform the action described above system message.")
        
    # keep the program running with a UI loop
    while True:
        # if the generate_code flag is set to true, generate code
        if generate_code:
            ui = TextEditorUI()
            create_code_editor_ui(ui)
            generate_code = False
            QApplication.processEvents()
            
            # load text in a separate thread
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(generate_with_codus, transcribedAudio)
                future.add_done_callback(lambda fut: ui.load_text(fut.result()))
            
            # show the text box UI created above
            ui.show()
            ui.app.exec()