# sound_sending.py

# 声音发送端

import socketserver
import base64
import pyaudio
# import _thread

# _thread.start_new_thread(func, (arg1,arg2,))

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100

RECORD_SECONDS = 5
    
# 将声音进行base64位编码
def sound_data_encode(frame):
    return base64.b64encode(frame)

class OnlineSoundTCPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        
        # 视频的元数据信息发送至客户端
        sound_meta = {'CHUNK':CHUNK, 'FORMAT': 'pyaudio.paInt16',  'CHANNELS':CHANNELS, 
                             'RATE':RATE, 'RECORD_SECONDS':RECORD_SECONDS, }
                                
        smeta = str(sound_meta).encode()
        self.request.sendall(smeta)
        
        while True:
            # 录制声音
            print("* recording")
            frames = []
            for i in range(int(RATE / CHUNK * RECORD_SECONDS)):
                data = self.stream.read(CHUNK)
                frames.append(data)

            print("* done recording")
            # 将声音进行base64位编码
            sound_bytes_5s = b''.join(frames)
            sound_base64_code = sound_data_encode(sound_bytes_5s)
            sound_base64_code_len = str(len(sound_base64_code)).encode()
            self.request.sendall(sound_base64_code_len)
            # TODO: 网络语音传输
            self.request.sendall(sound_base64_code)
            
            data = self.request.recv(1024)
            if len(data) == 0:
                break
            
            self.data = data.decode()
            print(self.data)
            # time.sleep(1)
        
        
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
