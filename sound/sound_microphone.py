# sound_microphone.py

# 声音的录制、编码、解码、播放
# 作者：尹立庆
# 微信：13521526165

import pyaudio
import wave
import time

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100

RECORD_SECONDS = 5
WAVE_OUTPUT_FILENAME = "output_audio.wav"

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

# 保存录音

wf = wave.open(WAVE_OUTPUT_FILENAME,  'wb')
wf.setnchannels(CHANNELS)
wf.setsampwidth(paudio.get_sample_size(FORMAT))
wf.setframerate(RATE)
wf.writeframes(b''.join(frames))
wf.close()

# 休眠3秒播放声音
print("* sleep 3 seconds")
time.sleep(3)
# 播放声音文件
wf = wave.open(WAVE_OUTPUT_FILENAME,  'rb')
paudio = pyaudio.PyAudio()

stream = paudio.open(format=FORMAT,  channels=CHANNELS,  rate=RATE,  output=True)    

print("* playing")

# TODO: 播放完成自动停止
data = wf.readframes(CHUNK)
while data != '':
    stream.write(data)
    data = wf.readframes(CHUNK)

print("* done playing")

stream.stop_stream()
stream.close()
paudio.terminate()
wf.close()

