#!/bin/bash

# CrashCatcher Deployment Script for Ubuntu 22.04
# Run this script on your fresh VM to deploy CrashCatcher

set -e

echo "🚀 CrashCatcher Production Deployment Script"
echo "=============================================="

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   echo "❌ This script should not be run as root"
   echo "Please run as a regular user with sudo privileges"
   exit 1
fi

# Update system
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install Docker
echo "🐳 Installing Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
else
    echo "✅ Docker already installed"
fi

# Install Docker Compose
echo "🔧 Installing Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
else
    echo "✅ Docker Compose already installed"
fi

# Install essential tools
echo "🛠️ Installing essential tools..."
sudo apt install -y git curl wget unzip ufw fail2ban

# Configure firewall
echo "🔥 Configuring firewall..."
sudo ufw --force reset
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable

# Configure fail2ban for SSH protection
echo "🛡️ Configuring fail2ban..."
sudo systemctl enable fail2ban
sudo systemctl start fail2ban

# Create deployment directory
echo "📁 Creating deployment directory..."
mkdir -p ~/crashcatcher
cd ~/crashcatcher

# Clone repository (if not already present)
if [ ! -d ".git" ]; then
    echo "📥 Cloning CrashCatcher repository..."
    git clone https://github.com/Mats6102hamberg/crashcatcher.git .
fi

# Create production environment file
echo "⚙️ Setting up environment configuration..."
if [ ! -f ".env.prod" ]; then
    cp .env.prod.example .env.prod
    echo "📝 Please edit .env.prod with your actual values:"
    echo "   - DOMAIN (your domain name)"
    echo "   - POSTGRES_PASSWORD (secure database password)"
    echo "   - SECRET_KEY (JWT signing key)"
    echo "   - API_KEY (watchdog API key)"
    echo ""
    echo "⚠️  IMPORTANT: Update .env.prod before proceeding!"
    echo "   nano .env.prod"
    exit 0
fi

# Build and start services
echo "🏗️ Building and starting CrashCatcher..."
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d --build

# Wait for services to start
echo "⏳ Waiting for services to initialize..."
sleep 30

# Check service health
echo "🔍 Checking service health..."
docker-compose -f docker-compose.prod.yml ps

echo "✅ CrashCatcher deployment completed!"
echo ""
echo "🌐 Your CrashCatcher should be available at: https://$(grep DOMAIN .env.prod | cut -d'=' -f2)"
echo ""
echo "📋 Next steps:"
echo "1. Point your domain DNS to this server's IP address"
echo "2. Wait a few minutes for Let's Encrypt SSL certificate"
echo "3. Visit your domain to access CrashCatcher"
echo ""
echo "🔧 Useful commands:"
echo "   View logs: docker-compose -f docker-compose.prod.yml logs -f"
echo "   Restart:   docker-compose -f docker-compose.prod.yml restart"
echo "   Stop:      docker-compose -f docker-compose.prod.yml down"
echo "   Update:    git pull && docker-compose -f docker-compose.prod.yml up -d --build"
