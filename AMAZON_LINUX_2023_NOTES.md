# Amazon Linux 2023 Package Names

Amazon Linux 2023 has different package names compared to Amazon Linux 2. Here are the key differences:

## Package Changes

| Component | Old Package (AL2) | New Package (AL2023) |
|-----------|-------------------|----------------------|
| MySQL Development | mysql-devel | mariadb105-devel |
| MySQL Server | mysql-server | mariadb105-server |
| Redis | redis | redis6 |
| Python 3.11 | python3 | python3.11 |

## Service Names

| Service | Old Name | New Name |
|---------|----------|----------|
| MySQL | mysqld | mariadb |
| Redis | redis | redis6 |

## Manual Installation Commands

If you need to install packages manually:

```bash
# MariaDB (MySQL)
sudo yum install mariadb105-server mariadb105-devel -y
sudo systemctl start mariadb
sudo systemctl enable mariadb

# Redis
sudo yum install redis6 -y
sudo systemctl start redis6
sudo systemctl enable redis6

# Python 3.11
sudo yum install python3.11 python3.11-pip python3.11-devel -y

# Nginx
sudo yum install nginx -y
sudo systemctl start nginx
sudo systemctl enable nginx
```

## Service Status Commands

```bash
# Check MariaDB
sudo systemctl status mariadb

# Check Redis
sudo systemctl status redis6

# Check Nginx
sudo systemctl status nginx
```

## Database Connection

MariaDB is 100% MySQL compatible:

```bash
# Connect to database (same as MySQL)
mysql -u plotvote -p plotvote

# Backup
mysqldump -u plotvote -p plotvote > backup.sql

# Restore
mysql -u plotvote -p plotvote < backup.sql
```

## Redis Connection

```bash
# Test Redis connection
redis-cli ping
# Should return: PONG
```

## Notes

- **MariaDB** is a drop-in replacement for MySQL and is fully compatible
- **Redis 7** is the latest version and works the same as Redis 6
- All Django and Python code remains unchanged
- The deployment scripts have been updated for AL2023 compatibility
