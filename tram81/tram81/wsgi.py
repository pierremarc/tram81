"""
WSGI config for madein project.
#!/usr/bin/env python
# -*- coding: utf-8 -*-
This module contains the WSGI application used by Django's development server
and any production WSGI deployments. It should expose a module-level variable
named ``application``. Django's ``runserver`` and ``runfcgi`` commands discover
this application via the ``WSGI_APPLICATION`` setting.

Usually you will have the standard Django WSGI application here, but it also
might make sense to replace the whole Django WSGI application with a custom one
that later delegates to the Django one. For example, you could introduce WSGI
middleware here, or combine a Django application with an application of another
framework.

"""
import os
import sys
import socket
import time
import traceback
from cherrypy import wsgiserver


from django.core.wsgi import get_wsgi_application
django_application = get_wsgi_application()

class DebugDjangoError(object):
    def __init__(self, app):
        self.application = app
        
    def __call__(self, environ, start_response):
        try:
            return self.application(environ, start_response)
        except Exception, e:
            start_response('500 Internal Server Error', [('Content-type','text/plain')])
            return '%s:\n%s\n\nsys.path\n%s'%(e, traceback.format_exc(), '\n'.join(sys.path))

class WSGIServer(wsgiserver.CherryPyWSGIServer):
    
    def start_with_socket_fd(self, sock_fd):
        """
        Re-Implement HTTPServer.start here to support 
        binding to an existing socket.
        """
        self._interrupt = None

        if self.software is None:
            self.software = "%s Server" % self.version

        # SSL backward compatibility
        if (self.ssl_adapter is None and
            getattr(self, 'ssl_certificate', None) and
            getattr(self, 'ssl_private_key', None)):
            warnings.warn(
                    "SSL attributes are deprecated in CherryPy 3.2, and will "
                    "be removed in CherryPy 3.3. Use an ssl_adapter attribute "
                    "instead.",
                    DeprecationWarning
                )
            try:
                from cherrypy.wsgiserver.ssl_pyopenssl import pyOpenSSLAdapter
            except ImportError:
                pass
            else:
                self.ssl_adapter = pyOpenSSLAdapter(
                    self.ssl_certificate, self.ssl_private_key,
                    getattr(self, 'ssl_certificate_chain', None))

        # Select the appropriate socket
        
        self.socket = socket.fromfd(sock_fd, 
                                    socket.AF_INET, 
                                    socket.SOCK_STREAM)
        msg = "No socket could be created with file descriptor '{0}'"
        if not self.socket:
            raise socket.error(msg.format(sock_fd))

        # Timeout so KeyboardInterrupt can be caught on Win32
        self.socket.settimeout(1)
        self.socket.listen(self.request_queue_size)

        # Create worker threads
        self.requests.start()

        self.ready = True
        self._start_time = time.time()
        while self.ready:
            try:
                self.tick()
            except (KeyboardInterrupt, SystemExit):
                raise
            except:
                self.error_log("Error in HTTPServer.tick", level=logging.ERROR,
                               traceback=True)

            if self.interrupt:
                while self.interrupt is True:
                    # Wait for self.stop() to complete. See _set_interrupt.
                    time.sleep(0.1)
                if self.interrupt:
                    raise self.interrupt

def main():
    
    application = DebugDjangoError(django_application)
    
    try:
        if len(sys.argv) == 2:
            sock_fd = int(sys.argv[1])
            server = WSGIServer('fd://%d'%(sock_fd,), application)
            print 'Start Server on fd://%d'%(sock_fd,)
            server.start_with_socket_fd(sock_fd)
            
        else:
            sys.path.append(sys.argv[3])
            server = WSGIServer((sys.argv[1],int(sys.argv[2])), application)
            print 'Start Server on %s:%s'%(sys.argv[1],sys.argv[2])
            server.start()
        
        
        print 'CTRL+C to interrupt'
    except KeyboardInterrupt:
        print 'Stopping server'
        server.stop()
        print 'Bye!'
    



if __name__ == "__main__":
    main()
    



