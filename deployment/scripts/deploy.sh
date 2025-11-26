#!/bin/bash

# PlotVote Deployment Script
# This script handles code updates and service restarts

set -e  # Exit on error

echo "🚀 Starting PlotVote deployment..."

# Configuration
PROJECT_DIR="/home/ec2-user/plotvote"
VENV_DIR="$PROJECT_DIR/venv"
REPO_URL="https://github.com/yourusername/plotvote.git"  # Update this

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Navigate to project directory
cd $PROJECT_DIR

echo -e "${YELLOW}📥 Pulling latest code from repository...${NC}"
git pull origin main

echo -e "${YELLOW}🔄 Activating virtual environment...${NC}"
source $VENV_DIR/bin/activate

echo -e "${YELLOW}📦 Installing/updating dependencies...${NC}"
pip install -r requirements.txt --upgrade

echo -e "${YELLOW}📊 Running database migrations...${NC}"
python manage.py migrate --noinput

echo -e "${YELLOW}📁 Collecting static files...${NC}"
python manage.py collectstatic --noinput

echo -e "${YELLOW}🔧 Restarting services...${NC}"
sudo systemctl restart plotvote
sudo systemctl restart plotvote-celery
sudo systemctl restart plotvote-celery-beat
sudo systemctl reload nginx

echo -e "${YELLOW}✅ Checking service status...${NC}"
sudo systemctl status plotvote --no-pager
sudo systemctl status plotvote-celery --no-pager

echo -e "${GREEN}✅ Deployment completed successfully!${NC}"
echo -e "${GREEN}🌐 Your site is now live at: http://18.191.166.7${NC}"
