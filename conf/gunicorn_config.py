command = '/home/josh/dailydose/venv/bin/gunicorn'
pythonpath = '/home/josh/dailydose/dailytriviadose'
bind = '0.0.0.0:8000'
workers = 3

max_requests = 1000
max_request_jitter = 50

timeout = 30
gracefultimeout = 30

accesslog = '/home/josh/dailydose/logs/gunicorn_access.log'
errorlog = '/home/josh/dailydose/logs/gunicorn_error.log'
