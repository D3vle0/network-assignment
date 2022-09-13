from datetime import datetime
import socket
import pickle, base64, json

FLAG = open('./FLAG', 'r').read()

port = 8081
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("0.0.0.0", port))

while True:
    data, addr = sock.recvfrom(1024)
    dec = pickle.loads(base64.b64decode(data.decode()))
    sock.sendto(json.dumps(dec).encode(), addr)
    print(dec)