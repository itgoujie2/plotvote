#!/bin/bash

# Manual Redis Installation Script for Amazon Linux 2023
# Run this if the main setup script fails to install Redis

set -e

echo "Installing Redis on Amazon Linux 2023..."

# Method 1: Try redis6
echo "Attempting to install redis6..."
if sudo yum install redis6 -y 2>/dev/null; then
    echo "✅ Redis 6 installed successfully"
    sudo systemctl start redis6
    sudo systemctl enable redis6
    echo "Service name: redis6"
    redis-cli ping
    exit 0
fi

# Method 2: Try generic redis package
echo "Attempting to install redis..."
if sudo yum install redis -y 2>/dev/null; then
    echo "✅ Redis installed successfully"
    sudo systemctl start redis
    sudo systemctl enable redis
    echo "Service name: redis"
    redis-cli ping
    exit 0
fi

# Method 3: Install from EPEL
echo "Installing from EPEL repository..."
sudo yum install https://dl.fedoraproject.org/pub/epel/epel-release-latest-9.noarch.rpm -y
sudo yum install redis -y
sudo systemctl start redis
sudo systemctl enable redis
echo "✅ Redis installed from EPEL"
echo "Service name: redis"
redis-cli ping

echo ""
echo "Redis installation complete!"
echo "To check status: sudo systemctl status redis"
