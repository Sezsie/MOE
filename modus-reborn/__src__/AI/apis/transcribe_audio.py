import requests

from __src__.UTILS.utils import Utilities, DebuggingUtilities
from __src__.DATA.manage_files import FileManager

files = FileManager()
api_key = files.getOpenAIKey()
debug = DebuggingUtilities()
dprint = debug.dprint

# this is the class that is responsible for transcribing audio files using the OpenAI API.
class AudioTranscriber:
    def __init__(self):
        key = api_key
        self.api_url = 'https://api.openai.com/v1/audio/transcriptions'
        self.headers = {'Authorization': f"Bearer {key}"}

    def transcribe(self, audio_file_path, prompt=None):
        with open(audio_file_path, 'rb') as audio_file:
            files = {'file': audio_file}
            data = {'model': 'whisper-1'}
            if prompt:
                data['prompt'] = prompt
            response = requests.post(self.api_url, headers=self.headers, data=data, files=files)
            if response.status_code == 200:
                dprint(f"Transcribed text: " + response.json()['text'])
                return self.correctTranscription(response.json()['text'])
            else:
                print(response.status_code)
                return "Error in transcription"
    
    # a method to replace the text "motus" with "MODUS" in the transcription.
    # during testing, the AI would often mishear "MODUS" as "motus", so this method is used to correct that.
    # otherwise, the AI would respond with something to the effect of "I am not Motus, I am MODUS. blah blah blah". it was so annoying.
    # you can probably tell that I am a bit salty about this.
    def correctTranscription(self, transcription):
        # while we're here, we might as well make the transcription lowercase for easier processing.
        transcription = transcription.lower()
        # replace "motus" with "MODUS"
        transcription = transcription.replace("motus", "MODUS")
        return transcription
