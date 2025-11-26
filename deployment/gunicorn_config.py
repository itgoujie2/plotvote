"""Gunicorn configuration file"""
import multiprocessing

# Server socket
bind = "127.0.0.1:8000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'sync'
worker_connections = 1000
timeout = 30
keepalive = 2

# Logging
accesslog = '/var/log/gunicorn/access.log'
errorlog = '/var/log/gunicorn/error.log'
loglevel = 'info'

# Process naming
proc_name = 'plotvote'

# Server mechanics
daemon = False
pidfile = '/var/run/gunicorn/plotvote.pid'
user = 'ec2-user'
group = 'ec2-user'
tmp_upload_dir = None

# SSL (if terminating SSL at Gunicorn instead of Nginx)
# keyfile = '/etc/ssl/private/key.pem'
# certfile = '/etc/ssl/certs/cert.pem'
