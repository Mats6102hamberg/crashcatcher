# CrashCatcher Production Deployment Guide

## 🚀 Quick Start

### 1. Create VM
**Recommended: Hetzner CX21 (Frankfurt)**
- OS: Ubuntu 22.04 LTS
- RAM: 4GB
- CPU: 2 vCPU
- Storage: 40GB SSD
- Price: ~€4.15/month

### 2. Initial Server Setup
```bash
# Connect to your server
ssh root@your-server-ip

# Create user (replace 'username' with your choice)
adduser username
usermod -aG sudo username

# Switch to new user
su - username
```

### 3. Deploy CrashCatcher
```bash
# Download and run deployment script
curl -fsSL https://raw.githubusercontent.com/Mats6102hamberg/crashcatcher/main/deploy.sh -o deploy.sh
chmod +x deploy.sh
./deploy.sh
```

### 4. Configure Environment
```bash
# Edit production configuration
nano .env.prod
```

**Required changes in .env.prod:**
- `DOMAIN=your-domain.com`
- `POSTGRES_PASSWORD=your-secure-password`
- `SECRET_KEY=your-jwt-secret-key`
- `API_KEY=your-api-key`

### 5. Start Services
```bash
# After editing .env.prod, run deploy script again
./deploy.sh
```

### 6. DNS Configuration
Point your domain to your server's IP:
```
A     your-domain.com          your-server-ip
A     www.your-domain.com      your-server-ip
```

## 🔧 Management Commands

### View Logs
```bash
# All services
docker-compose -f docker-compose.prod.yml logs -f

# Specific service
docker-compose -f docker-compose.prod.yml logs -f watchdog
```

### Update Application
```bash
git pull
docker-compose -f docker-compose.prod.yml up -d --build
```

### Restart Services
```bash
docker-compose -f docker-compose.prod.yml restart
```

### Backup Database
```bash
./backup.sh
```

### Monitor Resources
```bash
# System resources
htop
df -h

# Docker stats
docker stats
```

## 🛡️ Security Features

### Automatic HTTPS
- Caddy automatically obtains Let's Encrypt certificates
- Auto-renewal every 60 days
- Modern TLS configuration

### Firewall Protection
- UFW configured with minimal open ports
- Only 22 (SSH), 80 (HTTP), 443 (HTTPS) open
- Fail2ban protects against SSH brute force

### Security Headers
- HSTS enabled
- XSS protection
- Content Security Policy
- Frame options protection

## 📊 Monitoring

### Health Checks
All services have built-in health checks:
- Database: PostgreSQL ready check
- Backend: HTTP health endpoint
- Frontend: HTTP availability
- Watchdog: Process monitoring

### Log Locations
- Application logs: `docker-compose logs`
- Caddy access logs: `/data/logs/access.log`
- System logs: `/var/log/`

## 🚨 Troubleshooting

### Service Won't Start
```bash
# Check logs
docker-compose -f docker-compose.prod.yml logs service-name

# Check configuration
docker-compose -f docker-compose.prod.yml config
```

### SSL Certificate Issues
```bash
# Check Caddy logs
docker-compose -f docker-compose.prod.yml logs caddy

# Verify DNS is pointing correctly
nslookup your-domain.com
```

### Database Connection Issues
```bash
# Check database logs
docker-compose -f docker-compose.prod.yml logs db

# Connect to database manually
docker-compose -f docker-compose.prod.yml exec db psql -U crashcatcher_user security_monitor
```

## 💰 Cost Optimization

### Hetzner CX21 (Recommended)
- €4.15/month
- 4GB RAM, 2 vCPU
- 40GB SSD
- Frankfurt location (GDPR compliant)

### Resource Usage
- Expected RAM usage: ~2-3GB
- Expected CPU usage: ~10-20%
- Expected storage: ~5-10GB for logs/data

## 🔄 Automatic Backups

### Setup Cron Job
```bash
# Edit crontab
crontab -e

# Add daily backup at 2 AM
0 2 * * * /home/username/crashcatcher/backup.sh
```

### Backup Contents
- PostgreSQL database dump
- Application configuration
- Environment variables
- Caddy configuration

## 📈 Scaling

### Vertical Scaling (Upgrade VM)
```bash
# Update docker-compose limits if needed
nano docker-compose.prod.yml

# Restart services
docker-compose -f docker-compose.prod.yml up -d
```

### Horizontal Scaling
For high traffic, consider:
- Load balancer (nginx/HAProxy)
- Multiple backend instances
- Redis clustering
- Database read replicas

## 🎯 Production Checklist

- [ ] VM created with Ubuntu 22.04
- [ ] Domain DNS pointing to server IP
- [ ] .env.prod configured with secure passwords
- [ ] Services started and healthy
- [ ] HTTPS certificate obtained automatically
- [ ] Firewall configured and enabled
- [ ] Fail2ban protecting SSH
- [ ] Automatic backups scheduled
- [ ] Monitoring alerts configured
- [ ] Log rotation configured
