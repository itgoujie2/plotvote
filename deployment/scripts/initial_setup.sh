#!/bin/bash

# PlotVote Initial Server Setup Script
# Run this script on your EC2 instance for first-time setup

set -e  # Exit on error

echo "🚀 Starting PlotVote initial server setup..."

# Configuration
PROJECT_DIR="/home/ec2-user/plotvote"
REPO_URL="https://github.com/yourusername/plotvote.git"  # Update this

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}📦 Updating system packages...${NC}"
sudo yum update -y

echo -e "${YELLOW}🐍 Installing Python 3.11 and development tools...${NC}"
sudo yum install python3.11 python3.11-pip python3.11-devel -y
sudo yum install git gcc nginx -y

echo -e "${YELLOW}🗄️  Installing and configuring MySQL (MariaDB)...${NC}"
# Install MariaDB (MySQL-compatible) and development libraries
sudo yum install mariadb105-server mariadb105-devel -y
sudo systemctl start mariadb
sudo systemctl enable mariadb

echo -e "${YELLOW}📦 Installing Redis...${NC}"
# Try different Redis package names for AL2023
if sudo yum install redis6 -y 2>/dev/null; then
    REDIS_SERVICE="redis6"
    echo "Installed Redis 6"
elif sudo yum install redis -y 2>/dev/null; then
    REDIS_SERVICE="redis"
    echo "Installed Redis"
else
    echo "Installing Redis from EPEL repository..."
    sudo yum install https://dl.fedoraproject.org/pub/epel/epel-release-latest-9.noarch.rpm -y
    sudo yum install redis -y
    REDIS_SERVICE="redis"
fi

sudo systemctl start $REDIS_SERVICE
sudo systemctl enable $REDIS_SERVICE
echo "Redis service: $REDIS_SERVICE"

echo -e "${YELLOW}📁 Creating project directory...${NC}"
cd /home/ec2-user
if [ ! -d "$PROJECT_DIR" ]; then
    git clone $REPO_URL plotvote
else
    echo "Project directory already exists"
fi

cd $PROJECT_DIR

echo -e "${YELLOW}🐍 Creating Python virtual environment...${NC}"
python3.11 -m venv venv
source venv/bin/activate

echo -e "${YELLOW}📦 Installing Python dependencies...${NC}"
pip install --upgrade pip
pip install -r requirements.txt

echo -e "${YELLOW}🗄️  Setting up MySQL database...${NC}"
# Create database and user (MariaDB doesn't require root password by default for sudo)
sudo mysql << EOF
CREATE DATABASE IF NOT EXISTS plotvote CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS 'plotvote'@'localhost' IDENTIFIED BY 'change_this_password';
GRANT ALL PRIVILEGES ON plotvote.* TO 'plotvote'@'localhost';
FLUSH PRIVILEGES;
EOF

echo "MySQL database 'plotvote' created with user 'plotvote'"
echo "⚠️  Default password is 'change_this_password' - CHANGE THIS in production!"

echo -e "${YELLOW}📝 Creating environment file...${NC}"
if [ ! -f ".env" ]; then
    cp .env.production.example .env
    echo "⚠️  IMPORTANT: Edit .env file with your production values!"
else
    echo "Environment file already exists"
fi

echo -e "${YELLOW}📊 Running initial database migrations...${NC}"
python manage.py migrate

echo -e "${YELLOW}👤 Creating Django superuser...${NC}"
echo "You'll need to create a superuser account:"
python manage.py createsuperuser

echo -e "${YELLOW}📁 Collecting static files...${NC}"
python manage.py collectstatic --noinput

echo -e "${YELLOW}📂 Creating log directories...${NC}"
sudo mkdir -p /var/log/gunicorn /var/log/celery /var/log/nginx
sudo mkdir -p /var/run/gunicorn /var/run/celery
sudo chown -R ec2-user:ec2-user /var/log/gunicorn /var/log/celery
sudo chown -R ec2-user:ec2-user /var/run/gunicorn /var/run/celery
mkdir -p $PROJECT_DIR/logs

echo -e "${YELLOW}🔧 Installing systemd service files...${NC}"
sudo cp deployment/systemd/plotvote.service /etc/systemd/system/
sudo cp deployment/systemd/plotvote-celery.service /etc/systemd/system/
sudo cp deployment/systemd/plotvote-celery-beat.service /etc/systemd/system/

echo -e "${YELLOW}🌐 Configuring Nginx...${NC}"
sudo cp deployment/nginx/plotvote_http_only.conf /etc/nginx/conf.d/plotvote.conf
sudo nginx -t
sudo systemctl restart nginx
sudo systemctl enable nginx

echo -e "${YELLOW}🔄 Reloading systemd and starting services...${NC}"
sudo systemctl daemon-reload
sudo systemctl start plotvote
sudo systemctl enable plotvote
sudo systemctl start plotvote-celery
sudo systemctl enable plotvote-celery
sudo systemctl start plotvote-celery-beat
sudo systemctl enable plotvote-celery-beat

echo -e "${YELLOW}✅ Checking service status...${NC}"
sudo systemctl status plotvote --no-pager
sudo systemctl status plotvote-celery --no-pager
sudo systemctl status nginx --no-pager

echo -e "${GREEN}✅ Initial setup completed successfully!${NC}"
echo ""
echo -e "${YELLOW}⚠️  IMPORTANT NEXT STEPS:${NC}"
echo "1. Edit /home/ec2-user/plotvote/.env with your production values"
echo "2. Generate a new SECRET_KEY: python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'"
echo "3. Update database password in .env (change from 'change_this_password')"
echo "4. Configure your domain DNS to point to this server"
echo "5. Set up SSL certificates (see DEPLOYMENT_GUIDE.md)"
echo "6. Update Stripe to use live keys instead of test keys"
echo ""
echo -e "${GREEN}🌐 Your site should now be accessible at: http://18.191.166.7${NC}"
