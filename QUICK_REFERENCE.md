# 🚀 Tornetic Quick Reference Card

## 📍 Server Information

- **Hetzner VPS IP**: 128.140.4.76
- **Database Host**: tornetic-postgres-dev-do-user-15092707-0.f.db.ondigitalocean.com
- **Database Port**: 25060
- **Database Name**: defaultdb
- **Database User**: postgres-api

## 🌐 URLs (After Deployment)

- **Frontend**: https://yourdomain.com
- **API**: https://api.yourdomain.com
- **API Docs**: https://api.yourdomain.com/docs
- **Health Check**: https://api.yourdomain.com/health

## 🔑 Common Commands

### On Hetzner Server

```bash
# SSH into server
ssh root@128.140.4.76

# Navigate to app directory
cd /opt/tornetic

# Pull latest code and update
./update.sh

# View logs
docker compose -f docker-compose.production.yml logs -f

# Restart API
docker compose -f docker-compose.production.yml restart

# Stop everything
docker compose -f docker-compose.production.yml down

# Start everything
docker compose -f docker-compose.production.yml up -d

# Rebuild from scratch
docker compose -f docker-compose.production.yml down
docker compose -f docker-compose.production.yml build --no-cache
docker compose -f docker-compose.production.yml up -d

# Check container status
docker ps

# Access container shell
docker compose -f docker-compose.production.yml exec web bash

# Run migrations
docker compose -f docker-compose.production.yml exec web alembic upgrade head

# Check migration status
docker compose -f docker-compose.production.yml exec web alembic current

# Nginx commands
nginx -t                    # Test config
systemctl status nginx      # Check status
systemctl reload nginx      # Reload config
systemctl restart nginx     # Restart nginx

# SSL certificate management
certbot certificates        # Check certificates
certbot renew              # Renew certificates
```

### On Local Machine

```bash
# Push code changes
git add .
git commit -m "your message"
git push origin main

# Test backend locally
make dev

# Test frontend locally
cd padel-frontend
npm start

# Build frontend for production
cd padel-frontend
npm run build
```

## 📁 Important Files

- **`.env.production`** - Production environment variables (NEVER commit!)
- **`docker-compose.production.yml`** - Production Docker configuration
- **`nginx.conf`** - Nginx reverse proxy configuration
- **`deploy.sh`** - Initial deployment script
- **`update.sh`** - Quick update script
- **`DEPLOYMENT.md`** - Full deployment guide

## 🔧 Deployment Workflow

### Initial Deployment

1. Update `.env.production` with production values
2. Update `nginx.conf` with your domain
3. Update `deploy.sh` with your GitHub repo URL
4. Push to GitHub
5. SSH to server and run `./deploy.sh`
6. Set up DNS records
7. Get SSL certificate with Certbot
8. Deploy frontend to Cloudflare Pages

### Updating Code

**Backend:**
1. Make changes locally
2. Test with `make dev`
3. Commit and push to GitHub
4. SSH to server: `ssh root@128.140.4.76`
5. Run: `cd /opt/tornetic && ./update.sh`

**Frontend:**
1. Make changes locally
2. Test with `cd padel-frontend && npm start`
3. Commit and push to GitHub
4. Cloudflare Pages auto-deploys (2-3 minutes)

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| API not responding | Check logs: `docker compose -f docker-compose.production.yml logs` |
| 502 Bad Gateway | Container might be down: `docker ps` and restart if needed |
| Database connection error | Check `.env.production` credentials and Digital Ocean database status |
| SSL certificate expired | Run `certbot renew` |
| Frontend not loading | Check Cloudflare Pages build logs |
| CORS errors | Update CORS origins in `app/main.py` |

## 📊 Monitoring

### Health Checks

```bash
# API health
curl https://api.yourdomain.com/health

# Expected response
{"status":"healthy","service":"tornetic-api"}

# Check API root
curl https://api.yourdomain.com/
```

### Log Locations

- **Nginx Access**: `/var/log/nginx/padel-api-access.log`
- **Nginx Error**: `/var/log/nginx/padel-api-error.log`
- **Docker Logs**: `docker compose -f docker-compose.production.yml logs`

## 💾 Backup & Recovery

### Database Backup (Digital Ocean)

1. Log into Digital Ocean
2. Navigate to Databases → Your Database
3. Go to Settings → Backups
4. Enable daily automated backups

### Manual Database Backup

```bash
# Create backup
docker compose -f docker-compose.production.yml exec web pg_dump \
  -h tornetic-postgres-dev-do-user-15092707-0.f.db.ondigitalocean.com \
  -p 25060 \
  -U postgres-api \
  -d defaultdb > backup_$(date +%Y%m%d).sql

# Restore from backup
docker compose -f docker-compose.production.yml exec -T web psql \
  -h tornetic-postgres-dev-do-user-15092707-0.f.db.ondigitalocean.com \
  -p 25060 \
  -U postgres-api \
  -d defaultdb < backup_20250101.sql
```

## 🔐 Security Checklist

- [ ] `.env.production` is in `.gitignore`
- [ ] Strong JWT secret key (32+ characters random)
- [ ] SSL certificates installed
- [ ] Firewall configured (UFW)
- [ ] Database SSL mode enabled
- [ ] CORS configured for production domains only
- [ ] Regular security updates (`apt update && apt upgrade`)

## 💰 Monthly Costs

- Hetzner VPS: ~€4-10
- Digital Ocean PostgreSQL: ~$15
- Cloudflare Pages: FREE
- **Total: ~€20-25/month**

## 📞 Support Resources

- **Hetzner Support**: https://www.hetzner.com/support
- **Digital Ocean Support**: https://www.digitalocean.com/support
- **Cloudflare Support**: https://support.cloudflare.com/
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **Docker Docs**: https://docs.docker.com/
- **Nginx Docs**: https://nginx.org/en/docs/

---

**Last Updated**: 2025-10-01
