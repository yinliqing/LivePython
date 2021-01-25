# sound_microphone_more.py

# 声音的录制、编码、解码、播放

import pyaudio
import wave
import time
import base64

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100

RECORD_SECONDS = 1
WAVE_OUTPUT_FILENAME = "output_audio.wav"

# 将声音进行base64位编码
def sound_data_encode(frame):
    return base64.b64encode(frame)

# 将base64位编码的声音进行解码
def sound_data_decode(base64_code):
    return base64.b64decode(base64_code)
    

# 录音
paudio = pyaudio.PyAudio()

stream = paudio.open(format=FORMAT,  channels=CHANNELS,  rate=RATE,  input=True, 
                                frames_per_buffer=CHUNK)


# 保存录音

wf = wave.open(WAVE_OUTPUT_FILENAME,  'wb')
wf.setnchannels(CHANNELS)
wf.setsampwidth(paudio.get_sample_size(FORMAT))
wf.setframerate(RATE)

for i in range(10):
    print("* recording")
    frames = []
    for i in range(int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    print("* done recording")

    # 将声音进行base64位编码
    sound_bytes_5s = b''.join(frames)
    sound_base64_code = sound_data_encode(sound_bytes_5s)

    # 将base64位编码的声音进行解码
    sound_frames_data = sound_data_decode(sound_base64_code)
    wf.writeframes(sound_frames_data)
    
stream.stop_stream()
stream.close()
paudio.terminate()


wf.close()

"""
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
"""
