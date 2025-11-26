# Redis Installation Guide for Amazon Linux 2023

Redis package names vary in Amazon Linux 2023. Here are multiple methods to install Redis.

## Method 1: Try Available Packages (Recommended)

```bash
# Try redis6 first
sudo yum install redis6 -y

# If redis6 doesn't work, try generic redis
sudo yum install redis -y
```

## Method 2: Use the Auto-Install Script

We've provided a script that tries multiple methods:

```bash
cd /home/ec2-user/plotvote
chmod +x deployment/scripts/install_redis_manual.sh
./deployment/scripts/install_redis_manual.sh
```

## Method 3: Install from EPEL Repository

If the above don't work, install from EPEL:

```bash
# Add EPEL repository
sudo yum install https://dl.fedoraproject.org/pub/epel/epel-release-latest-9.noarch.rpm -y

# Install Redis
sudo yum install redis -y

# Start and enable
sudo systemctl start redis
sudo systemctl enable redis
```

## Method 4: Install Specific Version

Search for available Redis packages:

```bash
# Search for Redis packages
sudo yum search redis

# Install specific version (e.g., redis6.2)
sudo yum install redis6.2 -y
```

## Verify Installation

After installation, verify Redis is working:

```bash
# Check service status
sudo systemctl status redis    # or redis6

# Test connection
redis-cli ping
# Should return: PONG

# Check version
redis-cli --version
```

## Determine Service Name

After installation, find out what service name was created:

```bash
# List Redis-related services
systemctl list-units | grep redis

# Common service names:
# - redis.service
# - redis6.service
# - redis-server.service
```

## Update Celery Services

Once you know the Redis service name, update your systemd files if needed:

```bash
# Edit Celery service files
sudo nano /etc/systemd/system/plotvote-celery.service
sudo nano /etc/systemd/system/plotvote-celery-beat.service

# Change "After=network.target redis7.service" to:
# After=network.target redis.service
# or
# After=network.target redis6.service

# Reload systemd
sudo systemctl daemon-reload
```

## Common Issues & Solutions

### Issue: "No package redis available"

**Solution:** Install from EPEL repository (Method 3)

### Issue: Service won't start

```bash
# Check logs
sudo journalctl -u redis -n 50

# Check if port 6379 is already in use
sudo netstat -tlnp | grep 6379

# Try restarting
sudo systemctl restart redis
```

### Issue: Permission denied

```bash
# Fix Redis directory permissions
sudo chown -R redis:redis /var/lib/redis
sudo chown -R redis:redis /var/log/redis

# Restart
sudo systemctl restart redis
```

## Alternative: Use Docker (Advanced)

If all else fails, you can run Redis in Docker:

```bash
# Install Docker
sudo yum install docker -y
sudo systemctl start docker
sudo systemctl enable docker

# Run Redis container
sudo docker run -d --name redis -p 6379:6379 redis:7-alpine

# Auto-start on boot
sudo docker update --restart unless-stopped redis
```

## For Production: Use Amazon ElastiCache

For production deployments, consider using Amazon ElastiCache for Redis:
- Fully managed Redis service
- Automatic failover and backups
- Better performance and reliability

Update `.env`:
```bash
CELERY_BROKER_URL=redis://your-elasticache-endpoint:6379/0
```

## Quick Test

After installation, test Redis with Python:

```bash
source /home/ec2-user/plotvote/venv/bin/activate
python << EOF
import redis
r = redis.Redis(host='localhost', port=6379, db=0)
print(r.ping())  # Should print True
EOF
```

## Service Names Summary

Depending on what gets installed, your Redis service might be named:
- `redis.service` (most common)
- `redis6.service`
- `redis-server.service`

Use `systemctl list-units | grep redis` to find the exact name on your system.
