import pyaudio
import wave
import math
import time
import struct

class VoiceRecorder:
    def __init__(self):
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 44100
        self.CHUNK = 1024
        
        
        self.SILENT_CHUNKS = int(2 * self.RATE / self.CHUNK)
        self.THRESHOLD = 200  # Threshold for silence, on a scale of 0-32767 where 32767 is loudest. basically, if the audio is below this threshold, it is considered silent.
        self.audio = pyaudio.PyAudio()

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
        stream = self.audio.open(format=self.FORMAT, channels=self.CHANNELS,
                                 rate=self.RATE, input=True,
                                 frames_per_buffer=self.CHUNK)

        print("Please start talking.")
        audio_chunks = []
        silent_chunks = []

        while True:
            data_chunk = stream.read(self.CHUNK)
            audio_chunks.append(data_chunk)

            if self.is_silent(data_chunk):
                silent_chunks.append(1)
            else:
                silent_chunks = []

            if len(silent_chunks) > self.SILENT_CHUNKS:
                break

        print("Recording stopped.")
        stream.stop_stream()
        stream.close()
        self.audio.terminate()

        # Save the recording
        filename = "recording_" + time.strftime("%Y%m%d-%H%M%S") + ".wav"
        wf = wave.open(filename, 'wb')
        wf.setnchannels(self.CHANNELS)
        wf.setsampwidth(self.audio.get_sample_size(self.FORMAT))
        wf.setframerate(self.RATE)
        wf.writeframes(b''.join(audio_chunks))
        wf.close()

        return filename 
