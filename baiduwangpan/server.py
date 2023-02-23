#!/usr/bin/python
# author Yu
# 2023年02月17日
import select
# import socket
import struct
from multiprocessing import Pool
from os import listdir
from socket import *
import os


class server:
    def __init__(self, ip, port):
        self.s_listen: socket = None
        # self.epoll = None
        self.ip = ip
        self.port = port

    def tcp_client(self):
        # （）中的两个参数 使用ipv4 和tcp协议
        self.s_listen = socket(AF_INET, SOCK_STREAM)
        # 绑定ip and port
        self.s_listen.bind((self.ip, self.port))
        # 最大允许12个客户端同时连接
        self.s_listen.listen(12)
        # self.epoll = select.epoll()
        # epoll监控listen写缓冲 实现允许多个客户端连接
        # self.epoll.register(self.s_listen.fileno(), select.EPOLLIN)


class User:
    def __init__(self, new_client):
        self.new_client: socket = new_client
        self.path = None

    def deal_command(self):
        while True:
            self.path = os.getcwd()
            command = self.recv_train()
            if command[:2] == 'ls':
                self.do_ls()
            elif command[:2] == 'cd':
                self.do_cd(command)
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

    def do_gets(self, command):
        filename = command.split()[1]
        f = open(filename, 'rb')
        file_content = f.read()
        f.close()
        train_head = struct.pack('I', len(file_content))
        self.new_client.send(train_head + file_content)
        self.send_train('下载成功')

    def do_puts(self, command):
        filename = command.split()[1]
        f = open(filename, 'wb')
        train_head_len = struct.unpack('I', self.new_client.recv(4))
        file_content = self.new_client.recv(train_head_len[0])
        f.write(file_content)
        f.close()
        self.send_train('上传成功')

    def do_rm(self):
        pass

    def do_cd(self, command):
        path = command.split()[1]
        os.chdir(path)
        self.path = os.getcwd()
        self.send_train(self.path)

    def do_ls(self):
        data = ''
        for file in listdir(self.path):
            data += file + '' * 5 + str(os.stat(file).st_size) + '\n'
        self.send_train(data)

    def do_pwd(self):
        self.send_train(self.path)

    # 制作火车头 接收数据
    def recv_train(self):
        train_head_len = struct.unpack('I', self.new_client.recv(4))
        data = self.new_client.recv(train_head_len[0])
        return data.decode('utf8')

    # 制作火车头 发送数据
    def send_train(self, send_data: str):
        data_bytes = send_data.encode('utf8')
        data_len = struct.pack('I', len(data_bytes))  # 计算发送数据的大小
        self.new_client.send(data_len + data_bytes)


def pool_task(user):
    user.deal_command()  # 用户做什么


if __name__ == '__main__':
    server1 = server('', 2000)
    server1.tcp_client()
    po = Pool(5)
    while True:
      new_client, addr = server1.s_listen.accept() # 注意
      user = User(new_client)
      po.apply_async(pool_task, (user,))
