import threading
import os

# hide pygame support prompt
from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

import time
import openai
import pygame

from __src__.UTILS.utils import Utilities, DebuggingUtilities, FileUtilities

utils = Utilities()
debug = DebuggingUtilities()
files = FileUtilities()
dprint = debug.dprint

api_key = Utilities.getOpenAIKey()

# a class that is linked to a temporary audio file.
# when the audio file is played, it is deleted after it finishes playing.

class TemporaryAudio:
    def __init__(self, file_path):
        self.file_path = file_path
        thread = threading.Thread(target=self._play_audio)
        thread.start()

    def _play_audio(self):
        pygame.mixer.init()
        pygame.mixer.music.load(self.file_path)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy(): 
            time.sleep(1)
        pygame.mixer.music.stop()  # Stop the audio
        pygame.mixer.music.unload()  # Unload the audio file
        os.remove(self.file_path)  # Delete file after playing


# a class that generates speech from text using the OpenAI API.
class SpeechGenerator:
    def __init__(self, model='tts-1'):
        self.client = openai
        self.client.api_key = api_key
        self.model = model
        self.voices = ['alloy', 'echo', 'fable', 'onyx', 'nova', 'shimmer']
        self.audio_objects = []
        

    def speak(self, text, voice='alloy'):
        if not text:
            text = "Something went wrong. Please try again."
        if voice not in self.voices:
            raise ValueError(f"Voice '{voice}' not supported. Choose from {self.voices}")
        debug.startTimer("SpeechGeneration")

        speech_file_path = files.getProjectDirectory() + f"\\__bin__\\{voice}_speech.mp3" # TODO: I dont think this is a cross-platform solution! change this to use os.path.join instead!
        response = self.client.audio.speech.create(
            model=self.model,
            voice=voice,
            input=text
        )
        response.stream_to_file(speech_file_path)

        debug.stopTimer("SpeechGeneration")

        temp_audio = TemporaryAudio(speech_file_path)
        self.audio_objects.append(temp_audio)
    
    def changeVoice(self, voice):
        self.voice = voice

    def stop_all_audio(self):
        pygame.mixer.music.stop()
