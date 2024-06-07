import pyaudio
import wave
import math
import time
import struct

from __src__.DATA.manage_files import FileManager

files = FileManager()

seconds_to_wait = 1.5 # after this many seconds of silence, the recording will stop.

# this class is used to record audio from the user's microphone while they are speaking. it will stop recording when there has been silence for a certain amount of time.

# note from past me: holy CRAP this class is messy.
# TODO: rework this class to record for as long as the user holds the hotkey down.

class VoiceRecorder:
    def __init__(self):
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 44100
        self.CHUNK = 1024
        self.SILENT_CHUNKS = int(seconds_to_wait * self.RATE / self.CHUNK)
        self.SENSITIVITY = 1 # sensitivity of the voice detection algorithm. 0 is high sensitivity, 10 is low sensitivity.

    def normalize_threshold(self, sensitivity):
        """
        Normalize the sensitivity scale from 0-100 to the RMS level scale.
        0 is extremely high sensitivity (low threshold), 100 is extremely low sensitivity (high threshold).
        """
        
        MAX_RMS = 32767  # maximum RMS level for 16-bit audio
        MIN_RMS = 0  # minimum RMS level

        # reverse the sensitivity scale (so 0 is high sensitivity and 10 is low sensitivity)
        reversed_sensitivity = sensitivity

        # normalize the reversed sensitivity to the RMS scale
        threshold = reversed_sensitivity / 100 * (MAX_RMS - MIN_RMS) + MIN_RMS
        return threshold

    def is_silent(self, data_chunk):
        "Returns 'True' if below the 'silent' threshold"
        # Unpack data, calculate RMS
        count = len(data_chunk) / 2
        format = "<%dh" % count
        shorts = struct.unpack(format, data_chunk)
        sum_squares = sum(s * s for s in shorts)
        rms = math.sqrt(sum_squares / count)
        return rms < self.normalize_threshold(self.SENSITIVITY)


    def record(self):
        self.audio = pyaudio.PyAudio()
        
        stream = self.audio.open(format=self.FORMAT, channels=self.CHANNELS,
                                 rate=self.RATE, input=True,
                                 input_device_index=0,
                                 frames_per_buffer=self.CHUNK)

        print("Recording...")
        
        audio_chunks = []
        silent_chunks = []

        # while the user is speaking, keep recording until there is silence for a certain amount of time
        try:
            i = 0
            while True:
                data_chunk = stream.read(self.CHUNK)
                audio_chunks.append(data_chunk)

                if self.is_silent(data_chunk):
                    silent_chunks.append(1)
                else:
                    i += 1
                    silent_chunks = []
                
                # if there are more than SILENT_CHUNKS of silence, stop recording.
                if len(silent_chunks) > self.SILENT_CHUNKS:
                    break
                
        finally:
            stream.stop_stream()
            stream.close()


        print("Recording stopped.")
        stream.stop_stream()
        stream.close()
        self.audio.terminate()
        
        # analyze the audio data and cut out the silence so we can analyze the length of the recording without the silence later.
        # audio_chunks = audio_chunks[:len(audio_chunks) - len(silent_chunks) - self.SILENT_CHUNKS]

        # save the recording
        filename = "recording_" + time.strftime("%Y%m%d-%H%M%S") + ".wav"
        # move the file to modus-main\Include\bin
        filename = files.createFile(files.locateDirectory("audio"), filename)

        # save the audio data to a .wav file
        wf = wave.open(filename, 'wb')
        wf.setnchannels(self.CHANNELS)
        wf.setsampwidth(self.audio.get_sample_size(self.FORMAT))
        wf.setframerate(self.RATE)
        wf.writeframes(b''.join(audio_chunks))
        wf.close()

        return filename 
    

