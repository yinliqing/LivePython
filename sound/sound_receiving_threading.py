# sound_receiving.py

# 声音接收端
# 经测试语音发送效果很好
# 在单机上声卡的去噪功能会导致声音变小
# 作者：尹立庆
# 微信：13521526165

import socket
import base64
import pyaudio
import _thread
import time
import wave

RECORD_SECONDS = 1 # 录制时长为1秒，对方听到延迟为2秒，即为n + 1
WAVE_OUTPUT_FILENAME = "sound_network.wav"

# 将base64位编码的声音进行解码
def sound_data_decode(base64_code):
    return base64.b64decode(base64_code)

sound_map = {}
receive_number = 0
play_number = 0

def sound_playing(stream,  wf):
    global play_number
    # 保存录音

    while True:
        if play_number <= receive_number and sound_map.__contains__(play_number):
            print("* playing")
            sound_base64_code = sound_map.pop(play_number,  b'')
            sound_frames_data = sound_data_decode(sound_base64_code)
            stream.write(sound_frames_data)
            wf.writeframes(sound_frames_data)
            play_number = play_number + 1
            print("* done playing")
        else:
            time.sleep(1)


def main():
    HOST, PORT = 'localhost',  9999
    # HOST, PORT = '192.168.2.102',  9999
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
        
    stream = paudio.open(format=FORMAT,  channels=CHANNELS,  rate=RATE,  output=True, 
                                        frames_per_buffer=CHUNK)
    
    wf = wave.open(WAVE_OUTPUT_FILENAME,  'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(paudio.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    
    _thread.start_new_thread(sound_playing, (stream, wf, ))
    
    global receive_number
    
    while True:
        
        # 接收声音数据的长度
        sound_base64_code_len = client.recv(1024)
        sound_base64_code_len = int(sound_base64_code_len.decode())
        # 回复接收成功
        client.send(str(receive_number).encode())
        #  接收声音数据
        sound_base64_code = client.recv(sound_base64_code_len)
        
        sound_map[receive_number] = sound_base64_code
        receive_number = receive_number + 1
        
        msg = "Data Receive succussfully"
        client.send(msg.encode())
        print(msg)
        # time.sleep(1)
    
    stream.stop_stream()
    stream.close()
    paudio.terminate()
    wf.close()
    client.close()
    # 关闭窗口
    print('断开连接')

if __name__ == '__main__':
    main()
