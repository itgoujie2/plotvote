# Quick Deployment Reference

## 🚀 First Time Setup (Run Once)

```bash
# 1. Connect to EC2
ssh -i plotvote.pem ec2-user@18.191.166.7

# 2. Upload code (choose one method):

## Method A: Git
git clone https://github.com/yourusername/plotvote.git
cd plotvote

## Method B: SCP from local machine
# On local:
tar --exclude='venv' --exclude='db.sqlite3' --exclude='.git' -czf plotvote.tar.gz plotvote/
scp -i plotvote/plotvote.pem plotvote.tar.gz ec2-user@18.191.166.7:~
# On server:
tar -xzf plotvote.tar.gz && cd plotvote

# 3. Run setup script
chmod +x deployment/scripts/initial_setup.sh
./deployment/scripts/initial_setup.sh

# 4. Configure environment
nano .env
# Update: SECRET_KEY, DB_PASSWORD, STRIPE keys, OPENAI_API_KEY

# 5. Restart services
sudo systemctl restart plotvote
sudo systemctl restart plotvote-celery
```

## 🔄 Regular Updates

```bash
# Quick deploy (if using Git)
ssh -i plotvote.pem ec2-user@18.191.166.7
cd /home/ec2-user/plotvote
./deployment/scripts/deploy.sh
```

## 📊 Useful Commands

```bash
# Check status
sudo systemctl status plotvote
sudo systemctl status plotvote-celery
sudo systemctl status nginx

# View logs
sudo journalctl -u plotvote -f
tail -f /var/log/gunicorn/error.log

# Restart services
sudo systemctl restart plotvote
sudo systemctl restart plotvote-celery
sudo systemctl reload nginx

# Database backup
mysqldump -u plotvote -p plotvote > backup_$(date +%Y%m%d).sql

# Run Django commands
cd /home/ec2-user/plotvote
source venv/bin/activate
python manage.py shell
python manage.py createsuperuser
```

## 🔧 Troubleshooting

```bash
# Service won't start
sudo journalctl -u plotvote -n 100

# Check Gunicorn
sudo netstat -tlnp | grep 8000

# Test Nginx config
sudo nginx -t

# Check Redis
redis-cli ping

# MySQL connection
mysql -u plotvote -p plotvote
```

## 🔒 SSL Setup

```bash
# Install certbot
sudo yum install certbot python3-certbot-nginx -y

# Get certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Update Nginx config to HTTPS version
sudo cp deployment/nginx/plotvote.conf /etc/nginx/conf.d/plotvote.conf
sudo nginx -t && sudo systemctl reload nginx
```

## 📝 Before Going Live Checklist

- [ ] Update `.env` with production values
- [ ] Generate new `SECRET_KEY`
- [ ] Set `DEBUG=False`
- [ ] Update `ALLOWED_HOSTS` with your domain
- [ ] Switch Stripe to live keys
- [ ] Set up SSL certificates
- [ ] Run database migrations
- [ ] Collect static files
- [ ] Test all functionality
- [ ] Set up database backups
- [ ] Configure EC2 security groups (ports 80, 443, 22)

## 🆘 Emergency Commands

```bash
# Stop everything
sudo systemctl stop plotvote plotvote-celery plotvote-celery-beat nginx

# Start everything
sudo systemctl start plotvote plotvote-celery plotvote-celery-beat nginx

# View all service logs
sudo journalctl -u plotvote -u plotvote-celery -u nginx -f

# Rollback to previous version (if using Git)
git log  # Find commit hash
git reset --hard <commit-hash>
./deployment/scripts/deploy.sh
```

## 📞 Important Paths

```
Application: /home/ec2-user/plotvote
Virtual Env: /home/ec2-user/plotvote/venv
Static Files: /home/ec2-user/plotvote/staticfiles
Media Files: /home/ec2-user/plotvote/media
Logs: /var/log/gunicorn/, /var/log/nginx/
Services: /etc/systemd/system/plotvote*.service
Nginx Config: /etc/nginx/conf.d/plotvote.conf
```
