#!/bin/bash

# Deployment script for Tornetic API on Hetzner VPS
# This script should be run on the production server (128.140.4.76)

set -e  # Exit on error

echo "🚀 Starting Tornetic API deployment..."

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration
APP_DIR="/opt/tornetic"
REPO_URL="https://github.com/yourusername/yourrepo.git"  # UPDATE THIS
BRANCH="main"

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}Please run as root (use sudo)${NC}"
    exit 1
fi

echo -e "${YELLOW}📦 Updating system packages...${NC}"
apt-get update
apt-get upgrade -y

echo -e "${YELLOW}🐳 Installing Docker and Docker Compose...${NC}"
if ! command -v docker &> /dev/null; then
    # Install Docker
    apt-get install -y ca-certificates curl gnupg
    install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    chmod a+r /etc/apt/keyrings/docker.gpg

    echo \
      "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
      "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | \
      tee /etc/apt/sources.list.d/docker.list > /dev/null

    apt-get update
    apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

    systemctl enable docker
    systemctl start docker
    echo -e "${GREEN}✅ Docker installed successfully${NC}"
else
    echo -e "${GREEN}✅ Docker already installed${NC}"
fi

echo -e "${YELLOW}🌐 Installing Nginx...${NC}"
if ! command -v nginx &> /dev/null; then
    apt-get install -y nginx
    systemctl enable nginx
    echo -e "${GREEN}✅ Nginx installed successfully${NC}"
else
    echo -e "${GREEN}✅ Nginx already installed${NC}"
fi

echo -e "${YELLOW}🔒 Installing Certbot for SSL...${NC}"
if ! command -v certbot &> /dev/null; then
    apt-get install -y certbot python3-certbot-nginx
    echo -e "${GREEN}✅ Certbot installed successfully${NC}"
else
    echo -e "${GREEN}✅ Certbot already installed${NC}"
fi

echo -e "${YELLOW}📁 Setting up application directory...${NC}"
mkdir -p $APP_DIR
cd $APP_DIR

# Clone or pull repository
if [ -d ".git" ]; then
    echo -e "${YELLOW}📥 Pulling latest changes...${NC}"
    git fetch origin
    git checkout $BRANCH
    git pull origin $BRANCH
else
    echo -e "${YELLOW}📥 Cloning repository...${NC}"
    git clone -b $BRANCH $REPO_URL .
fi

# Check if .env.production exists
if [ ! -f ".env.production" ]; then
    echo -e "${RED}❌ Error: .env.production file not found!${NC}"
    echo "Please create .env.production with your production credentials"
    exit 1
fi

echo -e "${YELLOW}🔨 Building and starting Docker containers...${NC}"
docker compose -f docker-compose.production.yml down
docker compose -f docker-compose.production.yml build --no-cache
docker compose -f docker-compose.production.yml up -d

echo -e "${YELLOW}⏳ Waiting for API to start...${NC}"
sleep 10

# Check if container is running
if docker ps | grep -q padel_api; then
    echo -e "${GREEN}✅ API container is running${NC}"
else
    echo -e "${RED}❌ API container failed to start${NC}"
    docker compose -f docker-compose.production.yml logs
    exit 1
fi

# Test health endpoint
echo -e "${YELLOW}🏥 Testing health endpoint...${NC}"
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Health check passed${NC}"
else
    echo -e "${RED}❌ Health check failed${NC}"
    exit 1
fi

echo -e "${YELLOW}🌐 Configuring Nginx...${NC}"
cp nginx.conf /etc/nginx/sites-available/padel-api
ln -sf /etc/nginx/sites-available/padel-api /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test nginx configuration
nginx -t

# Reload nginx
systemctl reload nginx

echo -e "${GREEN}✅ Nginx configured successfully${NC}"

echo ""
echo -e "${GREEN}🎉 Deployment completed successfully!${NC}"
echo ""
echo "Next steps:"
echo "1. Update your domain DNS to point to this server IP: 128.140.4.76"
echo "2. Update nginx.conf and replace 'api.yourdomain.com' with your actual domain"
echo "3. Run the following command to get SSL certificate:"
echo "   sudo certbot --nginx -d api.yourdomain.com"
echo ""
echo "Useful commands:"
echo "  - View logs: docker compose -f docker-compose.production.yml logs -f"
echo "  - Restart API: docker compose -f docker-compose.production.yml restart"
echo "  - Stop API: docker compose -f docker-compose.production.yml down"
echo ""
