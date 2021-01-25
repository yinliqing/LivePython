# sound_microphone_base64.py

# 声音的录制、编码、解码、播放

import pyaudio
import base64
import time


CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100

RECORD_SECONDS = 5

# 录音
paudio = pyaudio.PyAudio()

stream = paudio.open(format=FORMAT,  channels=CHANNELS,  rate=RATE,  input=True, 
                                frames_per_buffer=CHUNK)

print("* recording")
frames = []
for i in range(int(RATE / CHUNK * RECORD_SECONDS)):
    data = stream.read(CHUNK)
    frames.append(data)

print("* done recording")

stream.stop_stream()
stream.close()
paudio.terminate()



# 将声音进行base64位编码
def sound_data_encode(frame):
    return base64.b64encode(frame)

# 将base64位编码的声音进行解码
def sound_data_decode(base64_code):
    return base64.b64decode(base64_code)
    
    
# 将声音进行base64位编码
sound_bytes_5s = b''.join(frames)
sound_base64_code = sound_data_encode(sound_bytes_5s)

# 将base64位编码的声音进行解码
sound_frames_data = sound_data_decode(sound_base64_code)


# 休眠3秒播放声音
print("* sleep 3 seconds")
time.sleep(3)


paudio = pyaudio.PyAudio()

stream = paudio.open(format=FORMAT,  channels=CHANNELS,  rate=RATE,  output=True)    

print("* playing")


stream.write(sound_frames_data)

print("* done playing")

stream.stop_stream()
stream.close()
paudio.terminate()

