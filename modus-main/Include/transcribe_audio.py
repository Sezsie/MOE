import requests

class AudioTranscriber:
    def __init__(self, key):
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
                return response.json()['text']
            else:
                print(response.status_code)
                return "Error in transcription"
