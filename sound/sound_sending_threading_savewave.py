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

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100

RECORD_SECONDS = 1 # 录制时长为1秒，对方听到延迟为2秒，即为n + 1
WAVE_OUTPUT_FILENAME = "sound_recording.wav"

sound_map = {}
sound_number = 0
send_number = 0

# 将声音进行base64位编码
def sound_data_encode(frame):
    return base64.b64encode(frame)
    
def sound_recording(stream,  wf,  record_seconds):
    global sound_number
    
    while True:
        # 录制声音
        print("* recording")
        frames = []
        for i in range(int(RATE / CHUNK * record_seconds)):
            data = stream.read(CHUNK)
            frames.append(data)
        sound_bytes = b''.join(frames)
        sound_base64_code = sound_data_encode(sound_bytes)
        sound_map[sound_number] = sound_base64_code
        sound_number = sound_number + 1
        wf.writeframes(sound_bytes)
        # sound_number = sound_number % 65536
        
        print("* done recording")

def microphone():
    # 录音
    paudio = pyaudio.PyAudio()

    stream = paudio.open(format=FORMAT,  channels=CHANNELS,  rate=RATE,  input=True, 
                                    frames_per_buffer=CHUNK)
                                    
    return paudio, stream

def save_wave(wavefile, format, channels, rate, sampwidth):
    wf = wave.open(wavefile,  'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(sampwidth)
    wf.setframerate(rate)
    return wf
    
def release_microphone(paudio,  stream):
    stream.stop_stream()
    stream.close()
    paudio.terminate()

class OnlineSoundTCPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        global sound_number
        global send_number
        # 视频的元数据信息发送至客户端
        sound_meta = {'CHUNK':CHUNK, 'FORMAT': 'pyaudio.paInt16',  'CHANNELS':CHANNELS, 
                             'RATE':RATE, 'RECORD_SECONDS':RECORD_SECONDS, }
                                
        smeta = str(sound_meta).encode()
        self.request.sendall(smeta)
        
        # 启动语音录制线程
        _thread.start_new_thread(sound_recording, (self.stream, self.wf, RECORD_SECONDS, ))
        
        while True:
            
            if send_number < sound_number:
                # 将声音进行base64位编码
                sound_base64_code = sound_map.pop(send_number, b'')
                
                sound_base64_code_len = str(len(sound_base64_code)).encode()
                self.request.sendall(sound_base64_code_len)
                # 接收成功消息，1秒时需要数据同步，否则两个sendall的数据会在一个缓存中，导致出错
                recv_nubmer = self.request.recv(1024)
                print('recv_nubmer',  recv_nubmer.decode())
                # TODO: 网络语音传输
                self.request.sendall(sound_base64_code)
                send_number = send_number + 1
                # send_number = send_number % 65536
                
                data = self.request.recv(1024)
                if len(data) == 0:
                    break
                
                self.data = data.decode()
                print(self.data)
            else:
                time.sleep(1)
        
        
    def setup(self):
        print('建立连接：',  self.client_address)
        
        # 录音
        self.paudio, self.stream = microphone()
        
        self.wf = save_wave(WAVE_OUTPUT_FILENAME, FORMAT, CHANNELS, RATE, self.paudio.get_sample_size(FORMAT))

    
    def finish(self):
        # 释放麦克风
        release_microphone(self.paudio,  self.stream)
        self.wf.close()

def main():
    HOST,  PORT = 'localhost',  9999
    server=socketserver.TCPServer((HOST,  PORT),  OnlineSoundTCPHandler)
    server.serve_forever()

if __name__ == '__main__':
    main()
