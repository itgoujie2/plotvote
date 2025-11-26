# PlotVote Production Deployment Guide

This guide will walk you through deploying PlotVote to your EC2 instance in a production-ready configuration.

## 📋 Prerequisites

- EC2 instance running Amazon Linux 2023 or similar
- SSH access to the instance (you have the .pem file)
- Domain name (optional but recommended for SSL)
- Your server IP: `18.191.166.7`

## 🏗️ Architecture Overview

**Production Stack:**
- **Web Server:** Nginx (reverse proxy, SSL termination, static files)
- **Application Server:** Gunicorn (WSGI server for Django)
- **Database:** MySQL (replacing SQLite)
- **Cache/Queue:** Redis (for Celery and caching)
- **Task Queue:** Celery (background tasks for AI generation)
- **Process Management:** systemd (service management)

## 🚀 Initial Deployment (First Time)

### Step 1: Connect to Your EC2 Instance

```bash
ssh -i plotvote.pem ec2-user@18.191.166.7
```

### Step 2: Upload Your Code to Server

**Option A: Using Git (Recommended)**

1. Push your code to a Git repository (GitHub, GitLab, etc.)
2. On the server, clone the repository:

```bash
cd /home/ec2-user
git clone https://github.com/yourusername/plotvote.git
cd plotvote
```

**Option B: Using SCP (Direct Upload)**

From your local machine:

```bash
# Upload project files (excluding venv and db.sqlite3)
cd /Users/jiegou/Downloads
tar --exclude='plotvote/venv' --exclude='plotvote/db.sqlite3' --exclude='plotvote/.git' -czf plotvote.tar.gz plotvote/
scp -i plotvote/plotvote.pem plotvote.tar.gz ec2-user@18.191.166.7:~

# On the server
ssh -i plotvote.pem ec2-user@18.191.166.7
tar -xzf plotvote.tar.gz
cd plotvote
```

### Step 3: Run Initial Setup Script

The setup script will install all dependencies and configure services:

```bash
cd /home/ec2-user/plotvote
chmod +x deployment/scripts/initial_setup.sh
./deployment/scripts/initial_setup.sh
```

This script will:
- Install Python 3.11, MySQL, Redis, Nginx
- Create MySQL database and user
- Set up Python virtual environment
- Install Python dependencies
- Run database migrations
- Configure systemd services
- Configure Nginx
- Start all services

**⚠️ IMPORTANT:** During the script, you'll be prompted to:
1. The script creates a MySQL user with default password 'change_this_password' (CHANGE THIS!)
2. Create a Django superuser account

### Step 4: Configure Environment Variables

Edit the `.env` file with production values:

```bash
nano /home/ec2-user/plotvote/.env
```

**Required Changes:**

```bash
# Generate a new SECRET_KEY
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'

# Update .env with:
SECRET_KEY=<your-new-secret-key>
DEBUG=False
DJANGO_SETTINGS_MODULE=plotvote.settings_production

# Database
DB_PASSWORD=<change-from-default-password>

# OpenAI (keep your existing key)
OPENAI_API_KEY=<your-openai-key>

# Stripe - USE LIVE KEYS FOR PRODUCTION!
STRIPE_PUBLISHABLE_KEY=pk_live_...
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

### Step 5: Update Production Settings

Edit production settings if needed:

```bash
nano /home/ec2-user/plotvote/plotvote/settings_production.py
```

Update `ALLOWED_HOSTS` with your domain:

```python
ALLOWED_HOSTS = [
    '18.191.166.7',
    'yourdomain.com',
    'www.yourdomain.com',
]
```

### Step 6: Restart Services

```bash
sudo systemctl restart plotvote
sudo systemctl restart plotvote-celery
sudo systemctl restart plotvote-celery-beat
```

### Step 7: Verify Deployment

Check service status:

```bash
# Check Django/Gunicorn
sudo systemctl status plotvote

# Check Celery worker
sudo systemctl status plotvote-celery

# Check Nginx
sudo systemctl status nginx

# View logs if there are issues
sudo journalctl -u plotvote -n 50
tail -f /var/log/gunicorn/error.log
```

Test the site:

```bash
curl http://18.191.166.7
```

Visit in browser: `http://18.191.166.7`

## 🔄 Subsequent Deployments (Updates)

For code updates after initial setup:

### Option 1: Using Git (Recommended)

```bash
ssh -i plotvote.pem ec2-user@18.191.166.7
cd /home/ec2-user/plotvote
./deployment/scripts/deploy.sh
```

The deploy script will:
- Pull latest code from Git
- Install/update dependencies
- Run migrations
- Collect static files
- Restart services

### Option 2: Manual Deployment

```bash
ssh -i plotvote.pem ec2-user@18.191.166.7
cd /home/ec2-user/plotvote
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart plotvote
sudo systemctl restart plotvote-celery
```

## 🔒 SSL/HTTPS Setup with Let's Encrypt

### Prerequisites
- Domain name pointing to your EC2 IP address
- Port 80 and 443 open in EC2 security group

### Install Certbot

```bash
sudo yum install certbot python3-certbot-nginx -y
```

### Obtain SSL Certificate

```bash
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

Follow the prompts. Certbot will:
- Obtain certificates from Let's Encrypt
- Automatically configure Nginx
- Set up auto-renewal

### Update Nginx Configuration

After SSL setup, update to the HTTPS configuration:

```bash
sudo cp /home/ec2-user/plotvote/deployment/nginx/plotvote.conf /etc/nginx/conf.d/plotvote.conf
sudo nginx -t
sudo systemctl reload nginx
```

### Auto-Renewal

Certbot automatically sets up renewal. Test it:

```bash
sudo certbot renew --dry-run
```

## 📊 Monitoring and Maintenance

### View Logs

```bash
# Application logs
sudo journalctl -u plotvote -f

# Celery logs
sudo journalctl -u plotvote-celery -f

# Nginx access logs
sudo tail -f /var/log/nginx/plotvote_access.log

# Nginx error logs
sudo tail -f /var/log/nginx/plotvote_error.log

# Gunicorn logs
tail -f /var/log/gunicorn/error.log
```

### Service Management

```bash
# Start services
sudo systemctl start plotvote
sudo systemctl start plotvote-celery
sudo systemctl start plotvote-celery-beat

# Stop services
sudo systemctl stop plotvote
sudo systemctl stop plotvote-celery

# Restart services
sudo systemctl restart plotvote
sudo systemctl restart plotvote-celery

# Check status
sudo systemctl status plotvote
sudo systemctl status nginx
sudo systemctl status redis
sudo systemctl status mysqld
```

### Database Backup

```bash
# Create backup
mysqldump -u plotvote -p plotvote > plotvote_backup_$(date +%Y%m%d).sql

# Restore backup
mysql -u plotvote -p plotvote < plotvote_backup_20241126.sql
```

### Update Dependencies

```bash
cd /home/ec2-user/plotvote
source venv/bin/activate
pip install -r requirements.txt --upgrade
sudo systemctl restart plotvote
```

## 🔧 Troubleshooting

### Service Won't Start

```bash
# Check logs
sudo journalctl -u plotvote -n 100
sudo journalctl -u plotvote-celery -n 100

# Check file permissions
ls -la /home/ec2-user/plotvote

# Check environment variables
sudo systemctl show plotvote --property=Environment
```

### Database Connection Issues

```bash
# Test MySQL connection
mysql -u plotvote -p plotvote

# Check MySQL status
sudo systemctl status mysqld

# View MySQL logs
sudo tail -f /var/log/mysqld.log
```

### Static Files Not Loading

```bash
# Recollect static files
cd /home/ec2-user/plotvote
source venv/bin/activate
python manage.py collectstatic --noinput

# Check Nginx configuration
sudo nginx -t

# Check file permissions
ls -la /home/ec2-user/plotvote/staticfiles/
```

### 502 Bad Gateway

This usually means Gunicorn isn't running:

```bash
# Check if Gunicorn is running
sudo systemctl status plotvote

# Check if it's listening on port 8000
sudo netstat -tlnp | grep 8000

# Restart the service
sudo systemctl restart plotvote
```

## 📈 Performance Optimization

### Enable Gzip Compression in Nginx

Add to Nginx config:

```nginx
gzip on;
gzip_vary on;
gzip_types text/plain text/css text/xml text/javascript application/json application/javascript application/xml+rss;
```

### Set Up Caching

Redis is already configured for caching. To verify:

```bash
redis-cli ping  # Should return PONG
```

### Monitor Resource Usage

```bash
# Check CPU and memory
htop

# Check disk space
df -h

# Check database size
mysql -u plotvote -p -e "SELECT table_schema AS 'Database', ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) AS 'Size (MB)' FROM information_schema.tables WHERE table_schema = 'plotvote' GROUP BY table_schema;"
```

## 🔐 Security Checklist

- [ ] `DEBUG=False` in production
- [ ] Strong `SECRET_KEY` generated
- [ ] MySQL password changed from default 'change_this_password'
- [ ] SSL certificates installed and auto-renewal working
- [ ] Security groups configured (ports 80, 443, 22 only)
- [ ] Regular backups scheduled
- [ ] Stripe live keys configured (not test keys)
- [ ] OpenAI API key secured
- [ ] Django admin only accessible to superusers
- [ ] Strong MySQL root password set

## 📞 Getting Help

If you encounter issues:

1. Check logs first (see Monitoring section)
2. Verify all services are running
3. Check environment variables are set correctly
4. Ensure database migrations have run
5. Verify file permissions

## 🎉 Post-Deployment

After successful deployment:

1. **Test all functionality:**
   - User registration/login
   - Story creation
   - AI generation (Celery tasks)
   - Payment processing (use Stripe test mode first)
   - File uploads

2. **Set up monitoring:**
   - Consider services like Sentry for error tracking
   - Set up uptime monitoring (e.g., UptimeRobot)

3. **Configure backups:**
   - Schedule daily database backups
   - Backup media files regularly

4. **Update DNS:**
   - Point your domain to the EC2 IP
   - Set up SSL certificates

5. **Switch Stripe to live mode:**
   - Update environment variables with live keys
   - Test payment flow thoroughly

---

## 📚 Additional Resources

- [Django Deployment Checklist](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/)
- [Gunicorn Documentation](https://docs.gunicorn.org/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [Let's Encrypt](https://letsencrypt.org/)

