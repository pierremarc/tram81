www = {
    'name':'mons.atelier-cartographique.be',
    'program':'python',
    'args':'/home/pierre/System/src/tram81/tram81/tram81/wsgi.py $(circus.sockets.mons.atelier-cartographique.be)',
    'host':'127.0.0.1',
    'port':8000,
    'working_dir':'/home/pierre/System/src/tram81/tram81/tram81',
    'workers': 2,
    'env':dict(DJANGO_SETTINGS_MODULE='tram81.settings'),

    }



SERVERS = (www,)

PATHS = (
    '/home/pierre/System/src/tram81/tram81',
    )

WANT_WEB = False

