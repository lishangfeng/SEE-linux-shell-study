# -*- coding: utf-8 -*-

import paramiko
from paramiko.common import DEBUG, INFO
from paramiko.ssh_exception import (SSHException, ProxyCommandFailure)


class Transport(paramiko.Transport):
    def __init__(self, *args, **kwargs):
        super(Transport, self).__init__(*args, **kwargs)

    def _check_banner(self):
        # this is slow, but we only have to do it once
        for i in range(100):
            # give them 15 seconds for the first line, then just 2 seconds
            # each additional line.  (some sites have very high latency.)
            if i == 0:
                timeout = self.banner_timeout
            else:
                timeout = 2
            try:
                buf = self.packetizer.readline(timeout)
            except ProxyCommandFailure:
                raise
            # except Exception as e:
            #     raise SSHException('Error reading SSH protocol banner' + str(e))
            if buf[:4] == 'SSH-':
                break
            self._log(DEBUG, 'Banner: ' + buf)
        if buf[:4] != 'SSH-':
            raise SSHException('Indecipherable protocol version "' + buf + '"')
        # save this server version string for later
        self.remote_version = buf
        self._log(DEBUG, 'Remote version/idstring: %s' % buf)
        # pull off any attached comment
        comment = ''
        i = buf.find(' ')
        if i >= 0:
            comment = buf[i+1:]
            buf = buf[:i]
        # parse out version string and make sure it matches
        segs = buf.split('-', 2)
        if len(segs) < 3:
            raise SSHException('Invalid SSH banner')
        version = segs[1]
        client = segs[2]
        if version != '1.99' and version != '2.0':
            raise SSHException('Incompatible version (%s instead of 2.0)' % (version,))
        self._log(INFO, 'Connected (version %s, client %s)' % (version, client))
