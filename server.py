#!/usr/bin/python3

import ssl
import socket
import threading

class Server:
    def __init__(self):
            self.ip = socket.gethostbyname(socket.gethostname())
            while True:
                try:
                    self.port = int(input('Enter port number to run on --> '))
                    self.password = input('Enter password to server --> ')

                    self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    self.s.bind((self.ip, self.port))

                    break
                except:
                    print("Couldn't bind to that port")

            self.connections = []
            self.accept_connections()

    def accept_connections(self):
        self.s.listen(5)
        print('Running on IP: '+self.ip)
        print('Running on port: '+str(self.port))
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain('server.crt', 'server.key')
        
        
        while True:
            try:
                c, addr = self.s.accept()
                c.settimeout(10)
                print('New Connection From: ' + addr[0])
                connstream = context.wrap_socket(c, server_side=True)
                print('Wrapping Socket in TLS: ' + addr[0])
                self.connections.append(connstream)

                threading.Thread(target=self.handle_client,args=(connstream,addr,)).start()
            except Exception as e:
                c.close()
                #print(e)
                pass
        
    def broadcast(self, sock, data):
        for client in self.connections:
            if client != self.s and client != sock or len(self.connections) == 1:
                try:
                    client.send(data)
                except:
                    pass

    def handle_client(self,connstream,addr):
        connstream.send(str.encode('PASSWORD:'))
        try:
            password = connstream.recv(1024)
            password = password.decode()
            if password == self.password:
                while True:
                        data = connstream.recv(1024)
                        self.broadcast(connstream, data)
            else:
                connstream.close()
                self.connections.remove(connstream)
                print("Client Dropped Due to Wrong Password")
        except:
            connstream.close()
            self.connections.remove(connstream)
            print("Client Disconnected/Unknown Error")

server = Server()
