# sound_receiving_threading_interactive.py

# 声音接收端
# 经测试语音发送效果很好
# 边录音边播放录音质量不好，在单机上声卡的去噪功能会导致声音变小
# 在直播客户端不放语音
# 作者：尹立庆
# 微信：13521526165

import socket
import base64
import pyaudio
import _thread
import time
import wave

local = {'CHUNK': 1024, 'FORMAT': pyaudio.paInt16, 'CHANNELS': 2, 'RATE': 44100, }

RECORD_SECONDS = 1 # 录制时长为1秒，对方听到延迟为2秒，即为n + 1
RECEIVE_WAVE_OUTPUT_FILENAME_RECORDING = "receive_sound_recording.wav"
RECEIVE_WAVE_OUTPUT_FILENAME_PLAYING = "receive_sound_playing.wav"

# 录音缓存
record_sound_map = {}
record_sound_number = 0
send_number = 0
# 接收播放缓存
play_sound_map = {}
receive_number = 0
play_number = 0

# 将base64位编码的声音进行解码
def sound_data_decode(base64_code):
    return base64.b64decode(base64_code)

# 将声音进行base64位编码
def sound_data_encode(frame):
    return base64.b64encode(frame)

def sound_playing(play_stream,  play_wf):
    global play_number
    # 保存录音

    while True:
        if play_number <= receive_number and play_sound_map.__contains__(play_number):
            print("* playing")
            sound_base64_code = play_sound_map.pop(play_number,  b'')
            sound_frames_data = sound_data_decode(sound_base64_code)
            play_stream.write(sound_frames_data)
            play_wf.writeframes(sound_frames_data)
            play_number = play_number + 1
            print("* done playing")
        else:
            time.sleep(1)

def speaker(format, channels, rate, frames_per_buffer):
    # 录音
    play_audio = pyaudio.PyAudio()

    play_stream = play_audio.open(format=format,  channels=channels,  rate=rate,  output=True, 
                                    frames_per_buffer=frames_per_buffer)
                                    
    return play_audio, play_stream

def save_wave(wavefile, format, channels, rate, sampwidth):
    play_wf = wave.open(wavefile,  'wb')
    play_wf.setnchannels(channels)
    play_wf.setsampwidth(sampwidth)
    play_wf.setframerate(rate)
    return play_wf

def release_speaker(play_audio,  play_stream):
    play_stream.stop_stream()
    play_stream.close()
    play_audio.terminate()

def sound_recording(record_stream,  record_wf,  record_seconds):
    global record_sound_number
    
    times = int(local['RATE'] / local['CHUNK'] * record_seconds)
    
    while True:
        # 录制声音
        print("* recording")
        frames = []
        for i in range(times):
            data = record_stream.read(local['CHUNK'])
            frames.append(data)
        sound_bytes = b''.join(frames)
        sound_base64_code = sound_data_encode(sound_bytes)
        record_sound_map[record_sound_number] = sound_base64_code
        record_sound_number = record_sound_number + 1
        record_wf.writeframes(sound_bytes)
        # record_sound_number = record_sound_number % 65536
        
        print("* done recording")

def microphone():
    # 录音
    record_audio = pyaudio.PyAudio()

    record_stream = record_audio.open(format=local['FORMAT'],  channels=local['CHANNELS'],  rate=local['RATE'],  input=True, 
                                    frames_per_buffer=local['CHUNK'])
                                    
    return record_audio, record_stream

def release_microphone(record_audio,  record_stream):
    record_stream.stop_stream()
    record_stream.close()
    record_audio.terminate()

def main():
    # HOST, PORT = 'localhost',  9999
    HOST, PORT = '192.168.2.102',  9999
    client = socket.socket()
    client.connect((HOST, PORT))
    
    remote = {'CHUNK': 1024, 'FORMAT': pyaudio.paInt16, 'CHANNELS': 2, 'RATE': 44100, }
    
    msg = "Connect succussfully"
    print(msg)
    smeta = client.recv(1024)
    remote = eval(smeta.decode())
    print(remote)
    
    # 播放
    play_audio, play_stream = speaker(remote['FORMAT'], remote['CHANNELS'], remote['RATE'], remote['CHUNK'])
    
    play_wf = save_wave(RECEIVE_WAVE_OUTPUT_FILENAME_PLAYING, remote['FORMAT'], remote['CHANNELS'], remote['RATE'], play_audio.get_sample_size(remote['FORMAT']))
    
    # 录音
    record_audio, record_stream = microphone()
    
    record_wf = save_wave(RECEIVE_WAVE_OUTPUT_FILENAME_RECORDING, local['FORMAT'], local['CHANNELS'], local['RATE'], record_audio.get_sample_size(local['FORMAT']))

    
    # 启动录音线程
    _thread.start_new_thread(sound_recording, (record_stream, record_wf, RECORD_SECONDS, ))
    # 启动语音播放功能
    _thread.start_new_thread(sound_playing, (play_stream, play_wf, ))
    
    global receive_number
    global send_number
    
    while True:
        
        # 接收声音数据的长度
        receive_sound_base64_code_len = client.recv(1024)
        receive_sound_base64_code_len = int(receive_sound_base64_code_len.decode())
        print('receive_sound_base64_code_len',  receive_sound_base64_code_len)
        # 回复接收成功
        # 将声音进行base64位编码
        
        send_sound_base64_code = record_sound_map.pop(send_number, b'')
        send_sound_base64_code_len = str(len(send_sound_base64_code)).encode()
        client.send(send_sound_base64_code_len)
        #  接收声音数据
        receive_sound_base64_code = client.recv(receive_sound_base64_code_len)
        
        play_sound_map[receive_number] = receive_sound_base64_code
        receive_number = receive_number + 1
        
        client.send(send_sound_base64_code)
        if len(send_sound_base64_code) > 0:
            send_number = send_number + 1
        # print(msg)
        # time.sleep(1)
    
    # 释放麦克风
    release_microphone(record_audio,  record_stream)
    record_wf.close()
    release_speaker(play_audio,  play_stream)
    play_wf.close()
    client.close()
    # 关闭窗口
    print('断开连接')

if __name__ == '__main__':
    main()
