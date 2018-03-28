import socket
import random
import sys


s = socket.socket()
host = socket.gethostname()
port = 12345
print(host, port)
s.bind((host, port))

s.listen(1)
c, addr = s.accept()
print('Got connection from', addr)
c.sendall(b'Thank you for connecting. Ready to play?\n')

yn = c.recv(10)
if yn == b'n\n' or yn == b'no\n':
    c.close()
    sys.exit()

responses = {
    'You fight like a dairy farmer\n':
        'how appropriate! You fight like a cow!',
    'Every word you say to me is stupid\n':
        'i wanted to make sure you\'d feel comfortable with me.',
    'My name is feared in every dirty corner of this island!\n':
        'so you got that job as a janitor, after all.'
}
scores = [0, 0]

while True:
    c.settimeout(0.1)
    q, a = random.choice(list(responses.items()))
    c.sendall(q.encode())

    try:
        data = c.recv(1024)

    except socket.timeout:
        c.sendall(b'Time\'s up!\n')
        c.close()
        sys.exit()

    data = data.decode().strip().lower()

    if data == a:
        scores[1] += 1
    else:
        scores[0] += 1

    if scores[0] == 3:
        c.sendall(b'I win!\n')
        c.close()

    elif scores[1] == 3:
        c.sendall(b'You win!\n')
        c.close()
