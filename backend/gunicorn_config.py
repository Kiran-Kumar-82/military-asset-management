# Gunicorn configuration file
import multiprocessing
import os

# Render provides PORT environment variable
port = os.environ.get('PORT', '10000')
bind = f"0.0.0.0:{port}"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
timeout = 120
keepalive = 5
max_requests = 1000
max_requests_jitter = 50


