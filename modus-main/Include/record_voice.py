import pyaudio
import wave
import math
import time
import struct
import os

from utils import Utilities
utils = Utilities()

# This class is used to record audio from the user's microphone while they are speaking. It will stop recording when there has been silence for a certain amount of time.

class VoiceRecorder:
    def __init__(self):
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 44100
        self.CHUNK = 1024
        self.SILENT_CHUNKS = int(1 * self.RATE / self.CHUNK)
        self.THRESHOLD = 500  # Threshold for silence, on a scale of 0-32767. The higher the number, the more sensitive the mic.


    def is_silent(self, data_chunk):
        "Returns 'True' if below the 'silent' threshold"
        # Unpack data, calculate RMS
        count = len(data_chunk) / 2
        format = "<%dh" % count
        shorts = struct.unpack(format, data_chunk)
        sum_squares = sum(s * s for s in shorts)
        rms = math.sqrt(sum_squares / count)
        return rms < self.THRESHOLD


    def record(self):
        self.audio = pyaudio.PyAudio()
        
        stream = self.audio.open(format=self.FORMAT, channels=self.CHANNELS,
                                 rate=self.RATE, input=True,
                                 input_device_index=0,
                                 frames_per_buffer=self.CHUNK)

        print("Please start talking.")
        audio_chunks = []
        silent_chunks = []


        # while the user is speaking, keep recording until there is silence for a certain amount of time
        try:
            while True:
                data_chunk = stream.read(self.CHUNK)
                audio_chunks.append(data_chunk)

                if self.is_silent(data_chunk):
                    silent_chunks.append(1)
                else:
                    silent_chunks = []
                    
                if len(silent_chunks) > self.SILENT_CHUNKS:
                    break
                
        finally:
            stream.stop_stream()
            stream.close()


        print("Recording stopped.")
        stream.stop_stream()
        stream.close()
        self.audio.terminate()

        # Save the recording
        filename = "recording_" + time.strftime("%Y%m%d-%H%M%S") + ".wav"
        # move theto modus-main\Include\bin
        filename = "modus-main/Include/bin/" + filename
        
        wf = wave.open(filename, 'wb')
        wf.setnchannels(self.CHANNELS)
        wf.setsampwidth(self.audio.get_sample_size(self.FORMAT))
        wf.setframerate(self.RATE)
        wf.writeframes(b''.join(audio_chunks))
        wf.close()
        
        # remove recording after three seconds.
        utils.scheduleRemoval(filename, 3)

        return filename 
    
    def list_devices(self):
        info = self.audio.get_host_api_info_by_index(0)
        numdevices = info.get('deviceCount')
        for i in range(0, numdevices):
            if (self.audio.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
                print("Input Device id ", i, " - ", self.audio.get_device_info_by_host_api_device_index(0, i).get('name'))


    
if __name__ == "__main__":
    recorder = VoiceRecorder()
    recorder.list_devices()
    
    audio = recorder.record()
    
    # use pydub to play the audio file
    from pydub import AudioSegment
    from pydub.playback import play
    
    sound = AudioSegment.from_wav(audio)
    play(sound)
    
    # delete the audio file after playing it
    os.remove(audio)

