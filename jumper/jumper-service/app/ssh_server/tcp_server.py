# -*- coding: utf-8 -*-

from SocketServer import ForkingTCPServer
from SocketServer import ThreadingTCPServer

from app.ssh_server.init import config

if config['server_type'] == 'process':
    TCPServer = ForkingTCPServer
else:
    TCPServer = ThreadingTCPServer


class Server(TCPServer):
    max_children = 2000
    daemon_threads = True
    allow_reuse_address = True

    def finish_request(self, request, client_address):
        self.socket.close()
        self.RequestHandlerClass(request, client_address)
