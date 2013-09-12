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


## CONF

servers = [
    ('tram81', 'python', 'manage.py runserver 8000'),
    ('tram81', 'python', 'manage.py runserver 8001'),
    ('tram81', 'python', 'manage.py runserver 8002'),
    ('tram81', 'python', 'manage.py runserver 8003'),
    ]

paths = ['tram81']

## END OF CONF

import os
from circus.watcher import Watcher
from circus.arbiter import Arbiter
from circus.util import (DEFAULT_ENDPOINT_DEALER, DEFAULT_ENDPOINT_SUB,
                                 DEFAULT_ENDPOINT_MULTICAST,
                                 DEFAULT_ENDPOINT_STATS)

HAS_WEB = False
try:
    import circusweb
    HAS_WEB = True
except ImportError:
    pass

SERVER_NAME = 0
SERVER_PROGRAM = 1
SERVER_ARGS = 2
SERVER_ENV = 3

def main():
    for p in paths:
        ap = os.path.abspath(p)
        if ap not in os.sys.path:
            os.sys.path.append(ap)

    def gc(s, a, d=None):
        try:
            return s[a]
        except Exception:
            return d

    watchers = []

    for s in servers:
        w = Watcher(gc(s, SERVER_NAME), 
                    gc(s, SERVER_PROGRAM), 
                    gc(s, SERVER_ARGS), 
                    working_dir=gc(s, SERVER_NAME),
                    env=gc(s, SERVER_ENV, dict()),
                    copy_env=True, 
                    copy_path=True)
        watchers.append(w)
        
    if HAS_WEB:
        arbiter = Arbiter(watchers, DEFAULT_ENDPOINT_DEALER, DEFAULT_ENDPOINT_SUB, 
                        stats_endpoint=DEFAULT_ENDPOINT_STATS, 
                        multicast_endpoint=DEFAULT_ENDPOINT_MULTICAST, 
                        statsd=True, 
                        httpd=True,
                        httpd_port=9999)
    else:
        arbiter = Arbiter(watchers, DEFAULT_ENDPOINT_DEALER, DEFAULT_ENDPOINT_SUB,
                        stats_endpoint=DEFAULT_ENDPOINT_STATS, 
                        multicast_endpoint=DEFAULT_ENDPOINT_MULTICAST)

    arbiter.start()


if __name__ == "__main__":
    main()



