import threading
import os
import time
import openai
import pygame

from pathlib import Path
from utils import Utilities
from utils import DebuggingUtilities

utils = Utilities()
debug = DebuggingUtilities()
dprint = debug.dprint

api_key = Utilities.getOpenAIKey()

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

class SpeechGenerator:
    def __init__(self, model='tts-1'):
        self.client = openai
        self.client.api_key = api_key
        self.model = model
        self.voices = ['alloy', 'echo', 'fable', 'onyx', 'nova', 'shimmer']
        self.audio_objects = []
        

    def speak(self, text, voice='alloy'):
        if voice not in self.voices:
            raise ValueError(f"Voice '{voice}' not supported. Choose from {self.voices}")
        debug.startTimer("SpeechGeneration")

        speech_file_path = Path(__file__).parent / "bin" / "MODUS_SPEECH.mp3"
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
