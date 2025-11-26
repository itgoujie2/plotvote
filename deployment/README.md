# Deployment Configuration Files

This directory contains all configuration files needed for production deployment.

## 📂 Directory Structure

```
deployment/
├── gunicorn_config.py              # Gunicorn WSGI server configuration
├── nginx/
│   ├── plotvote.conf              # Nginx config with HTTPS (use after SSL setup)
│   └── plotvote_http_only.conf    # Nginx config without HTTPS (use initially)
├── systemd/
│   ├── plotvote.service           # Main Django application service
│   ├── plotvote-celery.service    # Celery worker service
│   └── plotvote-celery-beat.service # Celery beat scheduler service
└── scripts/
    ├── initial_setup.sh           # First-time server setup script
    └── deploy.sh                  # Deployment script for updates

```

## 📋 File Descriptions

### gunicorn_config.py
Configuration for Gunicorn WSGI server that runs Django:
- **Workers:** Auto-calculated based on CPU cores
- **Bind:** localhost:8000 (not exposed to internet)
- **Logging:** `/var/log/gunicorn/`
- **User:** ec2-user

### nginx/plotvote.conf
Full production Nginx configuration with HTTPS:
- SSL certificate configuration
- HTTPS redirect from HTTP
- Static and media file serving
- Reverse proxy to Gunicorn
- Security headers
- **Use this AFTER setting up SSL certificates**

### nginx/plotvote_http_only.conf
Initial Nginx configuration without HTTPS:
- HTTP only (port 80)
- Static and media file serving
- Reverse proxy to Gunicorn
- **Use this for initial setup before SSL**

### systemd/plotvote.service
Systemd service for Django application:
- Runs Gunicorn with your Django app
- Auto-restart on failure
- Reads environment from `.env` file
- Managed by systemd

### systemd/plotvote-celery.service
Systemd service for Celery worker:
- Processes background tasks (AI generation, emails, etc.)
- Connects to Redis as message broker
- Auto-restart on failure
- Logs to `/var/log/celery/`

### systemd/plotvote-celery-beat.service
Systemd service for Celery beat scheduler:
- Schedules periodic tasks
- Works with Celery worker
- Required for scheduled operations

### scripts/initial_setup.sh
One-time server setup script that:
- Installs Python, PostgreSQL, Redis, Nginx
- Creates database and user
- Sets up Python virtual environment
- Installs dependencies
- Runs migrations
- Configures and starts services
- **Run once on fresh EC2 instance**

### scripts/deploy.sh
Deployment script for updates that:
- Pulls latest code from Git
- Updates dependencies
- Runs database migrations
- Collects static files
- Restarts services
- **Run for every deployment**

## 🚀 Usage

### First Time Setup

1. Upload your code to EC2
2. Run the initial setup script:
```bash
chmod +x deployment/scripts/initial_setup.sh
./deployment/scripts/initial_setup.sh
```

3. Configure environment variables:
```bash
nano .env
```

4. Restart services:
```bash
sudo systemctl restart plotvote
sudo systemctl restart plotvote-celery
```

### Subsequent Deployments

```bash
./deployment/scripts/deploy.sh
```

## 🔧 Service Management

```bash
# View status
sudo systemctl status plotvote
sudo systemctl status plotvote-celery
sudo systemctl status plotvote-celery-beat

# Start services
sudo systemctl start plotvote
sudo systemctl start plotvote-celery

# Stop services
sudo systemctl stop plotvote
sudo systemctl stop plotvote-celery

# Restart services
sudo systemctl restart plotvote
sudo systemctl restart plotvote-celery

# Enable auto-start on boot
sudo systemctl enable plotvote
sudo systemctl enable plotvote-celery

# View logs
sudo journalctl -u plotvote -f
sudo journalctl -u plotvote-celery -f
```

## 📝 Customization

### Change Gunicorn Workers

Edit `deployment/gunicorn_config.py`:
```python
workers = 4  # Set to specific number instead of auto-calculate
```

### Change Ports

Edit `deployment/gunicorn_config.py`:
```python
bind = "127.0.0.1:9000"  # Change port
```

Then update `deployment/nginx/plotvote.conf`:
```nginx
upstream plotvote_app {
    server 127.0.0.1:9000;  # Match Gunicorn port
}
```

### Add Static Gzip Compression

Edit Nginx config and add:
```nginx
gzip on;
gzip_types text/css application/javascript image/svg+xml;
```

### Change Log Levels

Edit `deployment/gunicorn_config.py`:
```python
loglevel = 'debug'  # or 'warning', 'error'
```

## 🔍 Troubleshooting

### Check Configuration Syntax

```bash
# Test Gunicorn config
/home/ec2-user/plotvote/venv/bin/gunicorn --check-config --config deployment/gunicorn_config.py plotvote.wsgi:application

# Test Nginx config
sudo nginx -t
```

### View Detailed Service Status

```bash
sudo systemctl status plotvote -l --no-pager
sudo journalctl -u plotvote -n 100 --no-pager
```

### Reload Configuration Without Restart

```bash
# Reload Gunicorn (for code changes)
sudo systemctl reload plotvote

# Reload Nginx (for config changes)
sudo systemctl reload nginx
```

## 📚 References

- [Gunicorn Documentation](https://docs.gunicorn.org/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [Systemd Service Documentation](https://www.freedesktop.org/software/systemd/man/systemd.service.html)
- [Celery Documentation](https://docs.celeryproject.org/)

