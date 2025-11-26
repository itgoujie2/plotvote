# PlotVote Deployment Summary

## 📦 What Has Been Created

Your PlotVote project now has a complete production deployment setup with the following files:

### Configuration Files

1. **`requirements.txt`** - Python dependencies for production
2. **`plotvote/settings_production.py`** - Production Django settings
3. **`.env.production.example`** - Template for environment variables

### Deployment Files

#### Gunicorn Configuration
- `deployment/gunicorn_config.py` - WSGI server configuration

#### Nginx Configuration
- `deployment/nginx/plotvote.conf` - Full HTTPS configuration (use after SSL setup)
- `deployment/nginx/plotvote_http_only.conf` - HTTP-only config (use initially)

#### Systemd Services
- `deployment/systemd/plotvote.service` - Django/Gunicorn service
- `deployment/systemd/plotvote-celery.service` - Celery worker service
- `deployment/systemd/plotvote-celery-beat.service` - Celery beat scheduler

#### Deployment Scripts
- `deployment/scripts/initial_setup.sh` - First-time server setup
- `deployment/scripts/deploy.sh` - Subsequent deployment updates

### Documentation
- `DEPLOYMENT_GUIDE.md` - Complete deployment guide
- `QUICK_DEPLOY.md` - Quick reference commands

## 🏗️ Production Architecture

```
┌─────────────────────────────────────────────────────┐
│                   Internet                           │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
            ┌────────────────┐
            │  EC2 Instance  │
            │  18.191.166.7  │
            └────────┬───────┘
                     │
         ┌───────────┼───────────┐
         ▼           ▼           ▼
    ┌────────┐  ┌────────┐  ┌────────┐
    │ Nginx  │  │ Redis  │  │ MySQL  │
    │  :80   │  │ :6379  │  │ :3306  │
    │  :443  │  └────────┘  └────────┘
    └───┬────┘
        │
        ▼
   ┌──────────┐
   │ Gunicorn │
   │  :8000   │
   └────┬─────┘
        │
        ▼
   ┌──────────┐       ┌──────────┐
   │  Django  │◄─────►│  Celery  │
   │   App    │       │  Worker  │
   └──────────┘       └──────────┘
```

## 🚀 Deployment Path

### Step 1: Initial Setup on EC2
```bash
ssh -i plotvote.pem ec2-user@18.191.166.7
# Upload code via git or scp
./deployment/scripts/initial_setup.sh
```

### Step 2: Configure Environment
```bash
nano .env
# Set: SECRET_KEY, DB_PASSWORD, API keys
```

### Step 3: Verify Services
```bash
sudo systemctl status plotvote
sudo systemctl status plotvote-celery
sudo systemctl status nginx
```

### Step 4: Test Site
```bash
curl http://18.191.166.7
# Or visit in browser
```

### Step 5: Set Up SSL (Optional but Recommended)
```bash
sudo certbot --nginx -d yourdomain.com
```

### Step 6: Future Updates
```bash
./deployment/scripts/deploy.sh
```

## 🔑 Key Configuration Points

### Database
- **Development:** SQLite (current)
- **Production:** MySQL
- Migration automatic via setup script

### Static Files
- **Development:** Served by Django
- **Production:** Served by Nginx from `/home/ec2-user/plotvote/staticfiles/`

### Environment Variables
| Variable | Development | Production |
|----------|-------------|------------|
| `DEBUG` | True | False |
| `DJANGO_SETTINGS_MODULE` | plotvote.settings | plotvote.settings_production |
| `ALLOWED_HOSTS` | [] | [Your IPs/Domains] |
| `SECRET_KEY` | Shared | Unique, secure |
| `DB_*` | SQLite | MySQL |
| Stripe Keys | Test | Live |

### Services
All services managed by systemd:
- **plotvote** - Main Django application
- **plotvote-celery** - Background task worker
- **plotvote-celery-beat** - Task scheduler
- **nginx** - Web server
- **mysqld** - Database
- **redis** - Cache and message broker

## 🔐 Security Features Implemented

✅ **Application Security:**
- Debug mode disabled in production
- Secure cookies (HTTPS only)
- CSRF protection enabled
- XSS filtering enabled
- Clickjacking protection
- HSTS enabled (after SSL setup)

✅ **Server Security:**
- Environment variables in `.env` file
- Database credentials secured
- API keys not in code
- `.pem` file excluded from git

✅ **Network Security:**
- Gunicorn not exposed to internet
- Nginx reverse proxy
- SSL/TLS encryption (after cert setup)

## 📊 Monitoring & Logs

### Application Logs
- Gunicorn: `/var/log/gunicorn/`
- Celery: `/var/log/celery/`
- Django: `/home/ec2-user/plotvote/logs/`

### System Logs
```bash
sudo journalctl -u plotvote -f
sudo journalctl -u plotvote-celery -f
```

### Nginx Logs
- Access: `/var/log/nginx/plotvote_access.log`
- Error: `/var/log/nginx/plotvote_error.log`

## 🎯 Production Checklist

Before going live:

- [ ] Generate new `SECRET_KEY`
- [ ] Set `DEBUG=False`
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Set strong database password
- [ ] Switch to Stripe live keys
- [ ] Add OpenAI API key
- [ ] Run migrations
- [ ] Collect static files
- [ ] Create Django superuser
- [ ] Test all functionality
- [ ] Set up SSL certificates
- [ ] Configure EC2 security groups
- [ ] Set up database backups
- [ ] Enable error monitoring (optional)
- [ ] Set up uptime monitoring (optional)

## 🔄 Deployment Workflow

### For New Features
1. Develop locally
2. Test locally
3. Commit to Git
4. Push to repository
5. SSH to server
6. Run `./deployment/scripts/deploy.sh`
7. Test on production

### For Hotfixes
1. SSH to server
2. Edit files directly OR pull from Git
3. Restart services: `sudo systemctl restart plotvote`
4. Verify fix

### For Database Changes
1. Create migration locally
2. Test migration
3. Commit and push
4. On server: `./deployment/scripts/deploy.sh` (includes migrations)

## 📈 Scaling Considerations

### Current Capacity
- Single EC2 instance
- Handles ~100 concurrent users
- Limited by instance resources

### When to Scale
- **Vertical Scaling:** Upgrade EC2 instance type
- **Horizontal Scaling:** Add load balancer + multiple app servers
- **Database:** Move to RDS for managed MySQL
- **Static Files:** Use S3 + CloudFront CDN
- **Cache:** Use ElastiCache for Redis

### Quick Wins
1. Enable Redis caching
2. Set up CloudFront for static files
3. Optimize database queries
4. Use Celery for heavy tasks
5. Enable gzip compression in Nginx

## 🆘 Common Issues & Solutions

### 502 Bad Gateway
- **Cause:** Gunicorn not running
- **Fix:** `sudo systemctl restart plotvote`

### Static Files Not Loading
- **Cause:** Not collected or wrong permissions
- **Fix:** `python manage.py collectstatic --noinput`

### Database Connection Error
- **Cause:** Wrong credentials or MySQL not running
- **Fix:** Check `.env` and `sudo systemctl status mysqld`

### Celery Tasks Not Running
- **Cause:** Celery worker not running or Redis down
- **Fix:** `sudo systemctl restart plotvote-celery` and check Redis

### Permission Denied Errors
- **Cause:** Wrong file ownership
- **Fix:** `sudo chown -R ec2-user:ec2-user /home/ec2-user/plotvote`

## 📚 Next Steps

1. **Review DEPLOYMENT_GUIDE.md** for detailed instructions
2. **Run initial_setup.sh** on your EC2 instance
3. **Configure .env** with production values
4. **Test the deployment** thoroughly
5. **Set up SSL** with your domain
6. **Configure backups** (database and media files)
7. **Set up monitoring** (optional but recommended)

## 🎉 You're Ready to Deploy!

All configuration files are ready. Follow the steps in `DEPLOYMENT_GUIDE.md` to get your site live on EC2.

Need help? Check the troubleshooting section in the deployment guide.
