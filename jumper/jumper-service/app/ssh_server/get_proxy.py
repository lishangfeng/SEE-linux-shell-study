# -*- coding:utf-8 -*-

import logging
import socket

from app.ssh_server.poll import simple_poll
from app.ssh_server.proxy_server import ProxyServer


class GetProxy:
    def __init__(self, client):
        self.client_ip = client.get('client_ip')
        self.client_port = client.get('client_port')
        self.client_socket = client.get('client_socket')

    def process(self):
        try:
            if simple_poll([self.client_socket], timeout=0.05):
                if self.client_socket.recv(4, socket.MSG_PEEK) != "SSH-":
                    self.client_socket.close()
                    return False

            proxy_server = ProxyServer(self.client_socket, self.client_ip, self.client_port)
            if proxy_server.start():
                return proxy_server
            else:
                self.client_socket.close()
        except Exception as e:
            logging.debug(u'客户端关闭连接: {0} - {1}'.format(self.client_ip, str(e)))
            return False
