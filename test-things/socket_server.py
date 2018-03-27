import socket
import random


s = socket.socket()
host = socket.gethostname()
port = 12345
print(host, port)
s.bind((host, port))

s.listen(1)
c, addr = s.accept()
print('Got connection from', addr)
c.send(b'Thank you for connecting. Let\'s play!\n')

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
    if scores[0] == 3:
        c.sendall(b'I win!\n')
        c.close()

    elif scores[1] == 3:
        c.sendall(b'You win!\n')
        c.close()

    q, a = random.choice(list(responses.items()))
    c.sendall(q.encode())
    data = c.recv(1024)
    if not data:
        break

    data = data.decode().strip().lower()

    if data == a:
        scores[1] += 1
    else:
        scores[0] += 1
