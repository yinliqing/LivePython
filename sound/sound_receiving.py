# sound_receiving.py

# 声音接收端

import socket
import base64
import pyaudio

# 将base64位编码的声音进行解码
def sound_data_decode(base64_code):
    return base64.b64decode(base64_code)

def main():
    HOST, PORT = 'localhost',  9999
    client = socket.socket()
    client.connect((HOST, PORT))
    
    msg = "Connect succussfully"
    print(msg)
    smeta = client.recv(1024)
    sound_meta = eval(smeta.decode())
    print(sound_meta)
    CHUNK = int(sound_meta['CHUNK'])
    FORMAT = eval(sound_meta['FORMAT'])
    CHANNELS = int(sound_meta['CHANNELS'])
    RATE = int(sound_meta['RATE'])
    
    paudio = pyaudio.PyAudio()
        
    stream = paudio.open(format=FORMAT,  channels=CHANNELS,  rate=RATE,  output=True)    
    
    while True:
        
        # 接收声音数据的长度
        sound_base64_code_len = client.recv(1024)
        sound_base64_code_len = int(sound_base64_code_len.decode())
        #  接收声音数据
        sound_base64_code = client.recv(sound_base64_code_len)
        sound_frames_data = sound_data_decode(sound_base64_code)
        


        print("* playing")

        stream.write(sound_frames_data)

        print("* done playing")

        
        
        msg = "Data Receive succussfully"
        client.send(msg.encode())
        print(msg)
        # time.sleep(1)
    
    stream.stop_stream()
    stream.close()
    paudio.terminate()
    client.close()
    # 关闭窗口
    print('断开连接')

if __name__ == '__main__':
    main()
