import os


bind = f"0.0.0.0:{os.getenv('PORT', '8000')}"
workers = int(os.getenv("WEB_CONCURRENCY", "1"))
threads = int(os.getenv("GUNICORN_THREADS", "2"))
worker_class = "gthread"
timeout = int(os.getenv("GUNICORN_TIMEOUT", "60"))
graceful_timeout = 30
keepalive = 5

accesslog = "-"
errorlog = "-"
capture_output = True
control_socket_disable = True

# Render terminates TLS before forwarding traffic to the container. Trusting its
# forwarding headers keeps Flask-generated Toss success/fail URLs on HTTPS.
forwarded_allow_ips = os.getenv("FORWARDED_ALLOW_IPS", "*")
