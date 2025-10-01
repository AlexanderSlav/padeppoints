#!/bin/bash

# Quick update script for production deployments
# Run this on the Hetzner server after pushing new code to GitHub

set -e

echo "🔄 Updating Tornetic API..."

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'
BRANCH="new_formats"

APP_DIR="/root/padeppoints"

cd $APP_DIR

echo -e "${YELLOW}📥 Pulling latest changes from GitHub...${NC}"
# git pull origin $BRANCH

echo -e "${YELLOW}🔨 Rebuilding Docker containers...${NC}"
docker compose -f docker-compose.production.yml down
docker compose -f docker-compose.production.yml build --no-cache
docker compose -f docker-compose.production.yml up -d

echo -e "${YELLOW}⏳ Waiting for API to start...${NC}"
sleep 10

# Test health endpoint
echo -e "${YELLOW}🏥 Testing health endpoint...${NC}"
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Update completed successfully!${NC}"
else
    echo -e "${RED}❌ Health check failed - check logs${NC}"
    docker compose -f docker-compose.production.yml logs --tail=50
    exit 1
fi

echo ""
echo "View logs: docker compose -f docker-compose.production.yml logs -f"
