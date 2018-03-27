import socket


s = socket.socket()
host = socket.gethostname()
port = 12345
print(host, port)
s.bind((host, port))

s.listen(5)
c, addr = s.accept()
print('Got connection from', addr)
c.send(b'Thank you for connecting\n')
while True:

    data = c.recv(1024)
    if not data:
        break

    resp = b'Echo: ' + data + b'\n'
    c.sendall(resp)
