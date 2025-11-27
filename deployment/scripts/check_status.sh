#!/bin/bash

# Quick script to check status of all services
# Usage: ./check_status.sh

echo "📊 PlotVote Service Status"
echo "=========================="
echo ""

# Check each service
check_service() {
    local service=$1
    local name=$2
    if sudo systemctl is-active --quiet $service; then
        echo "✅ $name: Running"
        sudo systemctl status $service --no-pager -l | grep "Active:" | head -1
    else
        echo "❌ $name: Not Running"
        sudo systemctl status $service --no-pager -l | grep "Active:" | head -1
    fi
    echo ""
}

check_service "plotvote" "Django App"
check_service "plotvote-celery" "Celery Worker"
check_service "plotvote-celery-beat" "Celery Beat"
check_service "nginx" "Nginx"
check_service "redis6" "Redis"
check_service "mariadb" "MariaDB"

echo "=========================="
echo ""
echo "Quick commands:"
echo "  Restart all: ./restart_services.sh"
echo "  View logs:   sudo journalctl -u plotvote -f"
echo "  Deploy:      ./deploy.sh"
