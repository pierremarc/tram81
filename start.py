#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Copyright (C) 2013  Pierre Marchand <pierremarc07@gmail.com>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as
    published by the Free Software Foundation, either version 3 of the
    License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

## END OF CONF

import os
import sys
from circus.watcher import Watcher
from circus.arbiter import Arbiter
from circus.util import (DEFAULT_ENDPOINT_DEALER, DEFAULT_ENDPOINT_SUB,
                                 DEFAULT_ENDPOINT_MULTICAST,
                                 DEFAULT_ENDPOINT_STATS)
from circus.sockets import CircusSocket, CircusSockets
from circus import logger
from circus.util import configure_logger
from importlib import  import_module





HAS_WEB = False
try:
    import circusweb
    HAS_WEB = True
except ImportError:
    pass

SERVER_NAME = 'name'
SERVER_PROGRAM = 'program'
SERVER_ARGS = 'args'
SERVER_ENV = 'env'
SERVER_HOST = 'host'
SERVER_PORT = 'port'
SERVER_WORKING_DIR = 'working_dir'
SERVER_WORKERS = 'workers'


def gc(s, a, d=None):
    try:
        return s[a]
    except Exception:
        return d

def main():
    #configure_logger(logger, 'DEBUG')
    config_mod = 'circus_settings'
    if len(sys.argv) > 1:
        config_mod = sys.argv[1]
    
    config = import_module(config_mod)
    
    
    for p in config.PATHS:
        ap = os.path.abspath(p)
        if ap not in os.sys.path:
            os.sys.path.append(ap)

    watchers = []
    sockets = []

    for s in config.SERVERS:
        
        w = Watcher(gc(s, SERVER_NAME), 
                    gc(s, SERVER_PROGRAM), 
                    gc(s, SERVER_ARGS),
                    numprocesses=gc(s, SERVER_WORKERS, 1), 
                    working_dir=gc(s, SERVER_WORKING_DIR, './'),
                    env=gc(s, SERVER_ENV, dict()),
                    copy_env=True, 
                    copy_path=True,
                    use_sockets=True)
        
        watchers.append(w)
        
        sock_port = gc(s, SERVER_PORT)
        if sock_port is not None:
            sock_name = gc(s, SERVER_NAME)
            sock_host = gc(s, SERVER_HOST, '127.0.0.1')
            sock = CircusSocket(sock_name, host=sock_host, port=sock_port)
            sockets.append(sock)
        
    for sock in sockets:
        print '>> %s'%(sock,)

    try:
        WANT_WEB = getattr(config, 'WANT_WEB')
    except Exception:
        WANT_WEB = True

    if HAS_WEB and WANT_WEB:
        arbiter = Arbiter(watchers, DEFAULT_ENDPOINT_DEALER, DEFAULT_ENDPOINT_SUB, 
                          sockets=sockets,
                        stats_endpoint=DEFAULT_ENDPOINT_STATS, 
                        multicast_endpoint=DEFAULT_ENDPOINT_MULTICAST, 
                        statsd=True, 
                        httpd=True,
                        httpd_port=9999)
    else:
        arbiter = Arbiter(watchers, DEFAULT_ENDPOINT_DEALER, DEFAULT_ENDPOINT_SUB,
                          sockets=sockets,
                        stats_endpoint=DEFAULT_ENDPOINT_STATS, 
                        multicast_endpoint=DEFAULT_ENDPOINT_MULTICAST)

    arbiter.start()


if __name__ == "__main__":
    main()



