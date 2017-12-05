# -*- coding:utf-8 -*-

import select
import logging
from multiprocessing import Pipe


def simple_poll(fds, timeout=60):
    k = None
    if hasattr(select, 'epoll'):
        poll = select.epoll()
        [poll.register(fd, getattr(select, 'EPOLLIN')) for fd in fds]
        for event, event_type in poll.poll(timeout=timeout):
            k = [fd for fd in fds if fd.fileno() == event]
        else:
            [poll.unregister(fd.fileno()) for fd in fds]
    else:
        k, _, _ = select.select(fds, [], [], timeout)
    return k[0] if k else None


class Poll:
    def __init__(self, transport=None):
        self.fd_list = list()
        self.fd_map = dict()
        self.transport = transport
        self.reload_send, self.reload_receive = Pipe()
        logging.debug(u'\t使用select io网络模型')

    def register(self, fd):
        self.reload_send.send('message')
        self.fd_list.append(fd)

    def unregister(self, fd):
        self.reload_send.send('message')
        try:
            self.fd_list.pop(self.fd_list.index(fd))
        except ValueError:
            pass

    def get_fd(self):
        while True:
            fds, _, _ = select.select(self.fd_list + [self.reload_receive], [], [], 1)
            if not fds:
                if not self.transport.active:
                    return False
            elif fds[0] == self.reload_receive:
                self.reload_receive.recv()
            else:
                return fds[0]


class PollBakcup:
    def __init__(self, transport=None):
        self.fd_list = list()
        self.fd_map = dict()
        self.transport = transport
        self.reload_send, self.reload_receive = Pipe()
        if hasattr(select, 'epoll'):
            self.poll = select.epoll()
            self.select = False
            logging.debug(u'\t使用epoll io网络模型')
        else:
            self.poll = None
            self.select = True
            logging.debug(u'\t使用select io网络模型')

    def register(self, fd):
        self.reload_send.send('message')
        self.fd_list.append(fd)
        if self.poll:
            self.fd_map[fd.fileno()] = fd
            self.poll.register(fd.fileno(), getattr(select, 'EPOLLIN'))

    def unregister(self, fd):
        self.reload_send.send('message')
        try:
            self.fd_list.pop(self.fd_list.index(fd))
            if self.poll:
                self.fd_map.pop(fd.fileno())
                self.poll.unregister(fd.fileno())
        except ValueError:
            pass

    def get_fd(self):
        while True:
            if self.poll:
                for fd, event in self.poll.poll(timeout=5):
                    return self.fd_map[fd]
                if not self.transport.active:
                    return False
            else:
                fds, _, _ = select.select(self.fd_list + [self.reload_receive], [], [], 5)
                if not fds:
                    if not self.transport.active:
                        return False
                elif fds[0] == self.reload_receive:
                    self.reload_receive.recv()
                else:
                    return fds[0]
