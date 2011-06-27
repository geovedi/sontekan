#!/usr/bin/env python
"""
Mark Nottingham's push-based asynchronous TCP library (with Dugsong's pyevent)

*** Create Server
    server = push_tcp.create_server(host, port, conn_handler)


*** Create Client
    host = 'www.example.com'
    port = '80'
    push_tcp.create_client(host, port, conn_handler, error_handler)


*** Handler
    def conn_handler(tcp_conn):
        print "connected to %s:%s" % tcp_conn.host, tcp_conn.port
        return read_cb, close_cb, pause_cb

    def error_handler(host, port, reason):
        print "can't connect to %s:%s: %s" % (host, port, reason)

"""

import sys
import socket
import errno
import event


class _TCPConnection(object):
	"""
	Base class for a TCP connection
	"""
	write_bufsize = 8
	read_bufsize = 1024 * 8
	def __init__(self, sock, host, port, connect_error_handler=None):
	    self.socket = sock
	    self.host = host
	    self.port = port
	    self.connect_error_handler = connect_error_handler
	    self.read_cb = None
	    self.close_cb = None
	    self._close_cb_called = False
	    self.pause_cb = None
	    self.tcp_connected = True
	    self._paused = False
	    self._closing = False
	    self.write_buffer = []
	    self._revent = event.read(sock, self.handle_read)
	    self._wevent = event.write(sock, self.handle_write)
	
	def handle_read(self):
	    """
	    The connection has data read for reading;
	    call read_cb if appropriate
	    """
	    try:
	        data = self.socket.recv(self.read_bufsize)
	    except socket.error, why:
	        if why[0] in [errno.EBADF, errno.ECONNRESET, errno.EPIPE, errno.TIMEOUT]:
	            self.conn_closed()
	            return
	        elif why[0] in [errno.ECONNREFUSED, errno.ENETUNREACH] and self.connect_error_handler:
	            self.tcp_connected = False
	            self.connect_error_handler(why[0])
	            return
	        else:
	            raise
	    if data == "":
	        self.conn_closed()
	    else:
	        self.read_cb(data)
        if self.read_cb and self.tcp_connected and not self._paused:
            return self._revent
	
	def handle_write(self):
	    """
	    The connection is ready for writing;
	    write any buffered data
	    """
	    if len(self._write_buffer) > 0:
	        data = "".join(self._write_buffer)
	        try:
	            sent = self.socket.send(data)
	        except socket.error, why:
	            if why[0] in [errno.EBADF, errno.ECONNRESET, errno.EPIPE, errno.ETIMEOUT]:
	                self.conn_closed()
	                return
	            elif why[0] in [errno.ECONNREFUSED, errno.ENETUNREACH] and self.connect_error_handler:
	                self.tcp_connected = False
	                self.connect_error_handler(why[0])
	                return
	            else:
	                raise
	        if sent < len(data):
	            self._write_buffer = [data[sent:]]
	        else:
	            self._write_buffer = []
	    if self.pause_cb and len(self._write_buffer) < self.write_bufsize:
	        self.pause_cb(False)
	    if self._closing:
	        self.close()
        if self.tcp_connected and (len(self._write_buffer) > 0 or self._closing):
            return self._wevent
    
    def conn_closed(self):
        """
        The connection has been closed by the other side.
        Do local cleanup and then call close_cb
        """
        self.tcp_connected = False
        if self._close_cb_called:
            return
        elif self.close_cb:
            self._close_cb_called = True
            self.close_cb()
        else:
            schedule(1, self.conn_closed)
    
    def write(self, data):
        """
        Write data to the connection
        """
        self._write_buffer.append(data)
        if self.pause_cb and len(self._write_buffer) > self.write_bufsize:
            self.pause_cb(True)
        if not self._wevent.pending():
            self._wevent.add()
    
    def pause(self, paused):
        """
        Temporarily stop/start reading from the connection
        and pushing it to the app
        """
        if paused:
            if self._revent.pending():
                self._revent.delete()
            else:
                if not self._revent.pending():
                    self._revent.add()
        self._paused = paused
    
    def close(self):
        """
        Flush buffered data (if any) and close the connection
        """
        self.pause(True)
        if len(self._write_buffer) > 0:
            self._closing = True
        else:
            self.socket.close()
            self.tcp_connected = False
    

class create_server(object):
    """
    An asynchronous TCP server
    """
    def __init__(self, host, port, conn_handler):
        self.host = host
        self.port = port
        self.conn_handler = conn_handler
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setblocking(0)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADD, 1)
        sock.bind((host, port))
        sock.listen(socket.SOMAXCONN)
        event.event(self.handle_accept, handle=sock, evtype=event.EV_READ|event.EV_PERSIST).add()
    
    def handle_accept(self, *args):
        conn, addr = args[1].accept()
        tcp_conn = _TCPConnection(conn, self.host, self.port, self.handle_error)
        tcp_conn.read_cb, tcp_conn.close_cb, tcp_conn.pause_cb = self.conn_handler(tcp_conn)
    
    def handle_error(self, err=None):
        raise AssertionError, "this (%s) should never happen for a server" % err
    

class create_client(object):
    """
    An asynchronous TCP client
    """
    def __init__(self, host, port, conn_handler, connect_error_handler, timeout=None):
        self.host = host
        self.port = port
        self.conn_handler = conn_handler
        self.connect_error_handler = connect_error_handler
        self._timeout_ev = None
        self._conn_handled = False
        self._error_sent = False
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setblocking(0)
        event.write(sock, self.handle_connect, sock).add()
        try:
            err = sock.connect_ex((host, port))
        except socket.error, why:
            self.handle_error(why)
            return
        if err != errno.EINPROGRESS:
            self.handle_error(err)
        if timeout:
            to_err = errno.ETIMEDOUT
            self._timeout_ev = schedule(timeout, self.handle_error, to_err)
    
    def handle_connect(self, sock=None):
        if self._timeout_ev:
            self._timeout_ev.delete()
        tcp_conn = _TCPConnection(sock, self.host, self.port, self.handle_error)
        tcp_conn.read_cb, tcp_conn.close_cb, tcp_conn.pause_cb = self.conn_handler(tcp_conn)
    
    def handle_write(self):
        pass
    
    def handle_error(self, err=None):
        if self._timeout_ev:
            self._timeout_ev.delete()
        if not self._error_sent:
            self._error_sent = True
            if err == None:
                t, err, tb = sys.exc_info()
            self.connect_error_handler(self.host, self.port, err)
    

schedule = event.timeout
run = event.dispatch
stop = event.abort
	