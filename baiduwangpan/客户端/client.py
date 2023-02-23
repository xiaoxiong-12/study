#!/usr/bin/python
# author Yu
# 2023年02月17日
from socket import *
import struct


class Client:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.client: socket = None

    def tcp_connect(self):
        self.client = socket(AF_INET, SOCK_STREAM)
        self.client.connect((self.ip, self.port))

    # 制作火车头 接收数据
    def recv_train(self):
        train_head_len = struct.unpack('I', self.client.recv(4))
        data = self.client.recv(train_head_len[0])
        return data.decode('utf8')

    # 制作火车头 发送数据
    def send_train(self, send_data: str):
        data_bytes = send_data.encode('utf8')
        data_len = struct.pack('I', len(data_bytes))  # 计算发送数据的大小
        self.client.send(data_len + data_bytes)

    def send_command(self):

        while True:
            command = input()
            self.send_train(command)
            if command[:2] == 'ls':
                self.do_ls()
            elif command[:2] == 'cd':
                self.do_cd()
            elif command[:3] == 'pwd':
                self.do_pwd()
            elif command[:2] == 'rm':
                self.do_rm(command)
            elif command[:4] == 'gets':
                self.do_gets(command)
            elif command[:4] == 'puts':
                self.do_puts(command)
            else:
                print("wrong command")

    def do_gets(self,command):
        filename = command.split()[1]
        f = open(filename, 'wb')
        train_head_len = struct.unpack('I', self.client.recv(4))
        file_content = self.client.recv(train_head_len[0])
        f.write(file_content)
        f.close()
        print(self.recv_train())

    def do_puts(self,command):
        filename=command.split()[1]
        f=open(filename,'rb')
        file_content=f.read()
        f.close()
        train_head=struct.pack('I',len(file_content))
        self.client.send(train_head+file_content)
        print(self.recv_train())


    def do_rm(self):
        pass

    def do_cd(self):
        print(self.recv_train())

    def do_ls(self):
        print(self.recv_train())

    def do_pwd(self):
        print(self.recv_train())



if __name__ == '__main__':
    client = Client('192.168.15.1', 2000)
    client.tcp_connect()
    client.send_command()
