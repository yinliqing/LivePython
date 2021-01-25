# sound_sending_threading_interactive.py

# 声音发送端
# 经测试语音发送效果很好
# 边录音边播放录音质量不好，在单机上声卡的去噪功能会导致声音变小
# 在直播客户端不放语音
# 作者：尹立庆
# 微信：13521526165

import socketserver
import base64
import pyaudio
import _thread
import time
import wave

# _thread.start_new_thread(func, (arg1,arg2,))
local = {'CHUNK': 1024, 'FORMAT': pyaudio.paInt16, 'CHANNELS': 2, 'RATE': 44100, }

remote = {'CHUNK': 1024, 'FORMAT': pyaudio.paInt16, 'CHANNELS': 2, 'RATE': 44100, }


RECORD_SECONDS = 1 # 录制时长为1秒，对方听到延迟为2秒，即为n + 1
SEND_WAVE_OUTPUT_FILENAME_RECORDING = "send_sound_recording.wav"
SEND_WAVE_OUTPUT_FILENAME_PLAYING = "send_sound_playing.wav"

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
    global play_sound_map
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

def save_wave(wavefile, format, channels, rate, sampwidth):
    record_wf = wave.open(wavefile,  'wb')
    record_wf.setnchannels(channels)
    record_wf.setsampwidth(sampwidth)
    record_wf.setframerate(rate)
    return record_wf
    
def release_microphone(record_audio,  record_stream):
    record_stream.stop_stream()
    record_stream.close()
    record_audio.terminate()

class OnlineSoundTCPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        global record_sound_number
        global send_number
        global receive_number
        global play_sound_map
        global local
        # 视频的元数据信息发送至客户端
        
        # print('local:', local)
        smeta = str(local).encode()
        self.request.sendall(smeta)
        
        # 启动录音线程
        _thread.start_new_thread(sound_recording, (self.record_stream, self.record_wf, RECORD_SECONDS, ))
        # 启动语音播放功能
        _thread.start_new_thread(sound_playing, (self.play_stream, self.play_wf, ))
    
        while True:
            
            if send_number < record_sound_number:
                # 将声音进行base64位编码
                send_sound_base64_code = record_sound_map.pop(send_number, b'')
                
                send_sound_base64_code_len = str(len(send_sound_base64_code)).encode()
                self.request.sendall(send_sound_base64_code_len)
                # 接收成功消息，1秒时需要数据同步，否则两个sendall的数据会在一个缓存中，导致出错
                receive_sound_base64_code_len = self.request.recv(1024)
                receive_sound_base64_code_len = int(receive_sound_base64_code_len.decode())
                print('receive_sound_base64_code_len',  receive_sound_base64_code_len)
                # TODO: 网络语音传输
                self.request.sendall(send_sound_base64_code)
                send_number = send_number + 1
                # send_number = send_number % 65536
                
                # 接收语音数据
                receive_sound_base64_code = self.request.recv(receive_sound_base64_code_len)
                play_sound_map[receive_number] = receive_sound_base64_code
                receive_number = receive_number + 1
                
            else:
                time.sleep(1)
        
        
    def setup(self):
        global local
        print('建立连接：',  self.client_address)
        # 播放
        self.play_audio, self.play_stream = speaker(remote['FORMAT'], remote['CHANNELS'], remote['RATE'], remote['CHUNK'])
    
        self.play_wf = save_wave(SEND_WAVE_OUTPUT_FILENAME_PLAYING, remote['FORMAT'], remote['CHANNELS'], remote['RATE'], self.play_audio.get_sample_size(remote['FORMAT']))
    
        # 录音
        self.record_audio, self.record_stream = microphone()
        
        self.record_wf = save_wave(SEND_WAVE_OUTPUT_FILENAME_RECORDING, local['FORMAT'], local['CHANNELS'], local['RATE'], self.record_audio.get_sample_size(local['FORMAT']))

    
    def finish(self):
        # 释放麦克风
        release_microphone(self.record_audio,  self.record_stream)
        self.record_wf.close()

def main():
    # HOST, PORT = 'localhost',  9999
    HOST, PORT = '192.168.2.102',  9999
    server=socketserver.TCPServer((HOST,  PORT),  OnlineSoundTCPHandler)
    server.serve_forever()

if __name__ == '__main__':
    main()
