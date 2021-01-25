# sound_sending.py

# 声音发送端
# 经测试语音发送效果很好
# 在单机上声卡的去噪功能会导致声音变小

import socketserver
import base64
import pyaudio
import _thread
import time

# _thread.start_new_thread(func, (arg1,arg2,))

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100

RECORD_SECONDS = 1 # 录制时长为1秒，对方听到延迟为2秒，即为n + 1

sound_map = {}
sound_number = 0
send_number = 0

# 将声音进行base64位编码
def sound_data_encode(frame):
    return base64.b64encode(frame)
    
def sound_recording(stream,  record_seconds):
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
        # sound_number = sound_number % 65536
        
        print("* done recording")

class OnlineSoundTCPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        global sound_number
        global send_number
        # 视频的元数据信息发送至客户端
        sound_meta = {'CHUNK':CHUNK, 'FORMAT': 'pyaudio.paInt16',  'CHANNELS':CHANNELS, 
                             'RATE':RATE, 'RECORD_SECONDS':RECORD_SECONDS, }
                                
        smeta = str(sound_meta).encode()
        self.request.sendall(smeta)
        
        _thread.start_new_thread(sound_recording, (self.stream, RECORD_SECONDS, ))
        
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
        self.paudio = pyaudio.PyAudio()

        self.stream = self.paudio.open(format=FORMAT,  channels=CHANNELS,  rate=RATE,  input=True, 
                                        frames_per_buffer=CHUNK)

    
    def finish(self):
        # 
        self.stream.stop_stream()
        self.stream.close()
        self.paudio.terminate()

def main():
    HOST,  PORT = 'localhost',  9999
    server=socketserver.TCPServer((HOST,  PORT),  OnlineSoundTCPHandler)
    server.serve_forever()

if __name__ == '__main__':
    main()
