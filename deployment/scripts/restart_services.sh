#!/bin/bash

# Quick script to restart all PlotVote services
# Usage: ./restart_services.sh

set -e

echo "🔄 Restarting PlotVote services..."

# Stop services in reverse order
echo "Stopping services..."
sudo systemctl stop plotvote-celery-beat 2>/dev/null || true
sudo systemctl stop plotvote-celery 2>/dev/null || true
sudo systemctl stop plotvote 2>/dev/null || true

# Reload systemd configuration
echo "Reloading systemd..."
sudo systemctl daemon-reload

# Start services
echo "Starting PlotVote..."
sudo systemctl start plotvote

echo "Starting Celery worker..."
sudo systemctl start plotvote-celery

echo "Starting Celery beat..."
sudo systemctl start plotvote-celery-beat

echo "Reloading Nginx..."
sudo systemctl reload nginx

echo ""
echo "✅ All services restarted!"
echo ""
echo "Service status:"
sudo systemctl is-active plotvote && echo "✓ PlotVote: running" || echo "✗ PlotVote: not running"
sudo systemctl is-active plotvote-celery && echo "✓ Celery Worker: running" || echo "✗ Celery Worker: not running"
sudo systemctl is-active plotvote-celery-beat && echo "✓ Celery Beat: running" || echo "✗ Celery Beat: not running"
sudo systemctl is-active nginx && echo "✓ Nginx: running" || echo "✗ Nginx: not running"
sudo systemctl is-active redis6 && echo "✓ Redis: running" || echo "✗ Redis: not running"
sudo systemctl is-active mariadb && echo "✓ MariaDB: running" || echo "✗ MariaDB: not running"

echo ""
echo "To view logs:"
echo "  sudo journalctl -u plotvote -f"
echo "  sudo journalctl -u plotvote-celery -f"
echo "  sudo journalctl -u plotvote-celery-beat -f"
