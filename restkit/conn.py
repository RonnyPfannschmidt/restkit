# -*- coding: utf-8 -
#
# This file is part of restkit released under the MIT license.
# See the NOTICE for more information.

from socketpool.conn import TcpSSLConnector

CHUNK_SIZE = 16 * 1024
MAX_BODY = 1024 * 112
DNS_TIMEOUT = 60


class Connection(TcpSSLConnector):

    def __init__(self, host, port, backend_mod=None, pool=None,
                 is_ssl=False, extra_headers=[],  **ssl_args):

        super(Connection, self).__init__(
            host, port, backend_mod, pool, is_ssl, **ssl_args)
        self.extra_headers = extra_headers

    def handle_exception(self, exception):
        raise

    def release(self, should_close=False):
        if self._pool is not None:
            if self._connected:
                if should_close:
                    self.invalidate()
                self._pool.release_connection(self)
            else:
                self._pool = None
        elif self._connected:
            self.invalidate()

    def close(self):
        #XXX: warn for missuse
        self.invalidate()

    def socket(self):
        return self._s

    def send_chunk(self, data):
        chunk = "".join(("%X\r\n" % len(data), data, "\r\n"))
        self._s.sendall(chunk)

    def send(self, data, chunked=False):
        if chunked:
            return self.send_chunk(data)

        return self._s.sendall(data)

    def sendlines(self, lines, chunked=False):
        for line in list(lines):
            self.send(line, chunked=chunked)

    # TODO: add support for sendfile api
    def sendfile(self, data, chunked=False):
        """ send a data from a FileObject """

        if hasattr(data, 'seek'):
            data.seek(0)

        while True:
            binarydata = data.read(CHUNK_SIZE)
            if binarydata == '':
                break
            self.send(binarydata, chunked=chunked)

