# video viewer

# 捕捉视频与音频与客户端实现在线视频，P2P视频

import socket
import base64
import cv2
import numpy as np

client=socket.socket()

client.connect(('localhost',9999))
frame_count = 0

while True:
    
    frame_code=client.recv(8294400) # 1228800
    
    frame_bytes = base64.b64decode(frame_code)
    print(type(frame_bytes))
    uint8_array = np.frombuffer(frame_bytes, dtype=np.uint8)
    print(type(uint8_array),  type(uint8_array),  uint8_array.shape)
    
    # segment_data = cv2.imdecode(uint8_array, cv2.IMREAD_COLOR)
    # frame = segment_data
    # frame2=np.array(frame1)
    frame=uint8_array.reshape((1920, 1080, 3))  # (480,640, 3)
    frame = frame.astype(np.uint8)
    # frame = cv2.cvtColor(frame, cv2.COLOR_BAYER_GB2RGB)
    print(frame[1, 1],  frame[-1, -1])
    print(type(frame[0, 0, 0]),  type(frame),  frame.shape)
    
    frame_count = frame_count+1
    print(frame_count)
    cmd= str(frame_count)
    if len(cmd)==0:
        continue
    if cmd=="quit":
        break
    client.send(cmd.encode())
    
    # ret, frame = cap.read()
    # image = Image.fromarray(frame)
    cv2.imshow("Live Viewer", frame)
    if cv2.waitKey(100) & 0xff == ord('q'):
        break
    
    # time.sleep(1)
    
client.close()
cv2.destroyAllWindows()

