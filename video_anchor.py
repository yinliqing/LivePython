# video anchor

# 捕捉视频与音频与客户端实现在线视频，P2P视频

import socketserver
import cv2
import base64

class LiveTCPHandler(socketserver.BaseRequestHandler):
    
    def handle(self):
        try:
            while True:
                # 逐帧发送视频与播放
                ret, frame = self.cap.read()
                print(frame[1, 1],  frame[-1, -1])
                print(ret,  type(frame[0, 0, 0]),  type(frame),  frame.shape)
                cv2.imshow("Live", frame)
                if cv2.waitKey(100) & 0xff == ord('q'):
                    break
                frame_code = base64.b64encode(frame)
                print(len(frame_code))
                
                self.request.sendall(frame_code)
                # 接收客户端反馈
                self.data=self.request.recv(1024)
                print("{} send:".format(self.client_address),self.data)
                if not self.data:
                    print("connection lost")
                    break
                
        except Exception as e:
            print(self.client_address, e, "连接断开")
        finally:
            self.request.close()
            cv2.destroyAllWindows()

            
    def setup(self):
        print("before handle,连接建立：",self.client_address)
        # self.cap = cv2.VideoCapture(0)       # 调用笔记本内置摄像头
        self.cap=cv2.VideoCapture("BattleForge.mp4")        #参数为视频文件目录
        
    def finish(self):
        # 释放摄像头对象和窗口
        self.cap.release()
        cv2.destroyAllWindows()
        print("finish run after handle")

if __name__=="__main__":
    
    HOST,PORT = "localhost",9999
    server=socketserver.TCPServer((HOST,PORT), LiveTCPHandler)

    server.serve_forever()
    
    
