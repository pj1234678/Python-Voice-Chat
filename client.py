#!/usr/bin/python3

import ssl
import socket
import threading
import pyaudio

class Client:
    def __init__(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ssl_sock = ssl.wrap_socket(self.s, ca_certs="server.crt",cert_reqs=ssl.CERT_REQUIRED)
        
        while True:
            try:
                self.target_ip = input('Enter IP address of server --> ')
                self.target_port = int(input('Enter target port of server --> '))
                self.password = input('Enter password to server --> ')


                self.ssl_sock.connect((self.target_ip, self.target_port))
                self.ssl_sock.sendall(self.password.encode())

                break
            except:
                print("Couldn't connect to server")

        chunk_size = 1024 # 512
        audio_format = pyaudio.paFloat32
        channels = 2
        rate = 48000

        # initialise microphone recording
        self.p = pyaudio.PyAudio()
        self.playing_stream = self.p.open(format=audio_format, channels=channels, rate=rate, output=True, frames_per_buffer=chunk_size)
        self.recording_stream = self.p.open(format=audio_format, channels=channels, rate=rate, input=True, frames_per_buffer=chunk_size)
        
        print("Connected to Server")

        # start threads
        receive_thread = threading.Thread(target=self.receive_server_data).start()
        self.send_data_to_server()

    def receive_server_data(self):
        while True:
            try:
                data = self.ssl_sock.recv(1024)
                self.playing_stream.write(data)
                free = self.playing_stream.get_write_available()
                if (free > 1024) :
                	tofill = free
                	#print(tofill)
                	self.playing_stream.write(chr(0) * tofill)
            except Exception as e: print(e)


    def send_data_to_server(self):
        while True:
            try:
                data = self.recording_stream.read(1024)
                self.ssl_sock.sendall(data)
            except Exception as e: print(e)

client = Client()
