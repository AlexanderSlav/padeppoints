# 🚀 Tornetic Production Deployment Guide

This guide covers the complete deployment process for the Tornetic padel tournament management system.

## 📋 Architecture Overview

- **Backend API**: Hetzner VPS (128.140.4.76) running FastAPI in Docker with nginx
- **Database**: Digital Ocean Managed PostgreSQL
- **Frontend**: Cloudflare Pages (static hosting with CDN)

## 🎯 Prerequisites

- Hetzner VPS (Ubuntu 22.04 or later)
- Digital Ocean Managed PostgreSQL (already configured)
- Domain name (e.g., `yourdomain.com`)
- GitHub account (for Cloudflare Pages deployment)

---

## 🔧 Part 1: Backend Deployment (Hetzner VPS)

### 1.1 Update Production Environment File

On your **local machine**, update `.env.production`:

```bash
# Database (Digital Ocean Managed PostgreSQL)
DB_USERNAME="your-db-username"
DB_PASSWORD="your-db-password"
DB_NAME="your-db-name"
DB_HOSTNAME="your-db-hostname.db.ondigitalocean.com"
DB_PORT=25060

# App Configuration
APP_HOST=0.0.0.0
APP_PORT=8000

# Google OAuth - UPDATE WITH YOUR PRODUCTION DOMAIN
GOOGLE_CLIENT_ID=your-actual-google-client-id
GOOGLE_CLIENT_SECRET=your-actual-google-client-secret
GOOGLE_REDIRECT_URI=https://api.tornetic.com/api/v1/auth/google/callback
FRONTEND_URL=https://tornetic.com

# Security - GENERATE A STRONG RANDOM SECRET
JWT_SECRET_KEY="your-strong-random-secret-key"

# SSL Mode for PostgreSQL
PGSSLMODE=require
```

**⚠️ IMPORTANT**: Generate a strong JWT secret key:
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 1.2 Update Nginx Configuration

Edit `nginx.conf` and replace all instances of `yourdomain.com` with your actual domain.

### 1.3 Update Deploy Script

Edit `deploy.sh` and update:
```bash
REPO_URL="https://github.com/yourusername/yourrepo.git"  # Your GitHub repo URL
```

### 1.4 Push Code to GitHub

```bash
git add .
git commit -m "feat: add production deployment configuration"
git push origin main
```

### 1.5 SSH into Hetzner Server

```bash
ssh root@128.140.4.76
```

### 1.6 Run Deployment Script

```bash
# Download and run the deployment script
curl -O https://raw.githubusercontent.com/yourusername/yourrepo/main/deploy.sh
chmod +x deploy.sh
sudo ./deploy.sh
```

Or manually:

```bash
# Install Git
apt-get update && apt-get install -y git

# Clone repository
mkdir -p /opt/tornetic
cd /opt/tornetic
git clone https://github.com/yourusername/yourrepo.git .

# Create .env.production (copy from local or create manually)
nano .env.production
# Paste your production environment variables

# Run deployment script
chmod +x deploy.sh
sudo ./deploy.sh
```

### 1.7 Configure DNS

Point your API subdomain to your Hetzner server:

**DNS Records:**
```
Type: A
Name: api (or api.yourdomain.com)
Value: 128.140.4.76
TTL: 300
```

Wait for DNS propagation (5-30 minutes).

### 1.8 Set Up SSL Certificate

Once DNS is propagated:

```bash
# Update nginx.conf with your actual domain
nano /opt/tornetic/nginx.conf
# Replace 'api.yourdomain.com' with your actual domain

# Copy to nginx sites
cp /opt/tornetic/nginx.conf /etc/nginx/sites-available/padel-api
ln -sf /etc/nginx/sites-available/padel-api /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test nginx configuration
nginx -t

# Reload nginx
systemctl reload nginx

# Get SSL certificate with Certbot
certbot --nginx -d api.yourdomain.com

# Follow prompts:
# 1. Enter your email
# 2. Agree to terms
# 3. Choose redirect HTTP to HTTPS (option 2)
```

### 1.9 Verify Backend Deployment

```bash
# Test health endpoint
curl https://api.yourdomain.com/health

# Should return:
# {"status":"healthy","service":"tornetic-api"}

# Test API root
curl https://api.yourdomain.com/

# View logs
cd /opt/tornetic
docker compose -f docker-compose.production.yml logs -f
```

---

## 🎨 Part 2: Frontend Deployment (Cloudflare Pages)

### 2.1 Prepare Frontend for Production

Update `padel-frontend/.env.production`:

```bash
REACT_APP_API_URL=https://api.yourdomain.com
REACT_APP_GOOGLE_CLIENT_ID=your-actual-google-client-id
```

### 2.2 Test Frontend Build Locally

```bash
cd padel-frontend
npm install
npm run build

# Test the build
npx serve -s build
# Open http://localhost:3000 to verify
```

### 2.3 Push to GitHub

```bash
git add .
git commit -m "feat: configure frontend for production"
git push origin main
```

### 2.4 Deploy to Cloudflare Pages

1. **Sign up for Cloudflare** (if you haven't already): https://dash.cloudflare.com/sign-up

2. **Go to Cloudflare Pages**: https://dash.cloudflare.com/ → Pages

3. **Connect to Git**:
   - Click "Create a project"
   - Click "Connect to Git"
   - Select GitHub
   - Authorize Cloudflare
   - Select your repository

4. **Configure Build Settings**:
   ```
   Project name: tornetic (or your preferred name)
   Production branch: main
   Build command: cd padel-frontend && npm install && npm run build
   Build output directory: padel-frontend/build
   Root directory: /
   ```

5. **Environment Variables**:
   Add the following environment variables:
   ```
   REACT_APP_API_URL = https://api.yourdomain.com
   REACT_APP_GOOGLE_CLIENT_ID = your-actual-google-client-id
   ```

6. **Click "Save and Deploy"**

7. **Wait for Build** (usually 2-3 minutes)

8. **Get Cloudflare URL**: You'll get a URL like `tornetic.pages.dev`

### 2.5 Set Up Custom Domain

1. In Cloudflare Pages → Your Project → Custom domains
2. Click "Set up a custom domain"
3. Enter your domain: `yourdomain.com` or `www.yourdomain.com`
4. Follow Cloudflare's DNS instructions

**If your domain is NOT on Cloudflare:**
Add a CNAME record:
```
Type: CNAME
Name: @ (for root) or www
Value: tornetic.pages.dev (your Cloudflare Pages URL)
TTL: Auto
```

**If your domain IS on Cloudflare:**
Cloudflare will automatically configure DNS for you.

### 2.6 Update CORS Settings

Since your frontend is now on a different domain, update the backend CORS settings.

SSH into your Hetzner server:

```bash
ssh root@128.140.4.76
cd /opt/tornetic
```

Edit `app/main.py` and update CORS origins:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://yourdomain.com",
        "https://www.yourdomain.com",
        "https://tornetic.pages.dev",  # Your Cloudflare Pages URL
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)
```

Then redeploy:

```bash
git pull origin main
docker compose -f docker-compose.production.yml down
docker compose -f docker-compose.production.yml build
docker compose -f docker-compose.production.yml up -d
```

---

## 🔐 Part 3: Google OAuth Configuration

### 3.1 Update Google OAuth Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project
3. Navigate to APIs & Services → Credentials
4. Click on your OAuth 2.0 Client ID

**Add Authorized JavaScript origins:**
```
https://yourdomain.com
https://www.yourdomain.com
https://api.yourdomain.com
```

**Add Authorized redirect URIs:**
```
https://api.yourdomain.com/api/v1/auth/google/callback
```

5. Click Save

---

## 📊 Part 4: Database Migrations

### 4.1 Run Migrations on Production

The migrations run automatically on container startup, but you can manually run them:

```bash
ssh root@128.140.4.76
cd /opt/tornetic

# Run migrations inside container
docker compose -f docker-compose.production.yml exec web alembic upgrade head

# Check migration status
docker compose -f docker-compose.production.yml exec web alembic current
```

---

## 🔍 Monitoring & Maintenance

### Useful Commands

```bash
# SSH into server
ssh root@128.140.4.76
cd /opt/tornetic

# View logs
docker compose -f docker-compose.production.yml logs -f

# Restart API
docker compose -f docker-compose.production.yml restart

# Stop everything
docker compose -f docker-compose.production.yml down

# Update code and redeploy
git pull origin main
docker compose -f docker-compose.production.yml down
docker compose -f docker-compose.production.yml build --no-cache
docker compose -f docker-compose.production.yml up -d

# Check container status
docker ps

# Check nginx status
systemctl status nginx

# Reload nginx after config change
nginx -t && systemctl reload nginx

# Check SSL certificate expiry
certbot certificates

# Renew SSL certificate (automatic renewal is set up by certbot)
certbot renew --dry-run
```

### Log Locations

- **Nginx Access Logs**: `/var/log/nginx/padel-api-access.log`
- **Nginx Error Logs**: `/var/log/nginx/padel-api-error.log`
- **Docker Logs**: `docker compose -f docker-compose.production.yml logs`

### Health Checks

```bash
# API health
curl https://api.yourdomain.com/health

# Frontend
curl https://yourdomain.com

# Database connection (from within container)
docker compose -f docker-compose.production.yml exec web python -c "from app.db.session import configure_db; import asyncio; asyncio.run(configure_db('postgresql+asyncpg://...'))"
```

---

## 🚨 Troubleshooting

### API Not Responding

```bash
# Check if container is running
docker ps | grep padel_api

# If not running, check logs
docker compose -f docker-compose.production.yml logs

# Restart container
docker compose -f docker-compose.production.yml restart
```

### Database Connection Issues

```bash
# Test connection from server
docker compose -f docker-compose.production.yml exec web python -c "import asyncpg; asyncio.run(asyncpg.connect('postgresql://...'))"

# Check if Digital Ocean database is accessible
telnet tornetic-postgres-dev-do-user-15092707-0.f.db.ondigitalocean.com 25060
```

### Nginx Configuration Issues

```bash
# Test nginx config
nginx -t

# Check nginx logs
tail -f /var/log/nginx/padel-api-error.log

# Reload nginx
systemctl reload nginx
```

### SSL Certificate Issues

```bash
# Check certificate status
certbot certificates

# Renew certificate
certbot renew

# Force renewal
certbot renew --force-renewal
```

### Frontend Not Loading

1. Check Cloudflare Pages build logs
2. Verify environment variables in Cloudflare Pages settings
3. Check browser console for errors
4. Verify CORS settings in backend

---

## 💰 Cost Breakdown

| Service | Cost | Notes |
|---------|------|-------|
| Hetzner VPS | ~€4-10/month | Depending on size |
| Digital Ocean PostgreSQL | ~$15/month | Basic tier |
| Cloudflare Pages | **FREE** | Unlimited bandwidth |
| Domain | ~$10-15/year | From any registrar |
| **Total** | **~€20-25/month** | Very affordable! |

---

## 🔒 Security Best Practices

✅ **Completed:**
- SSL/HTTPS for both frontend and backend
- Environment variables for secrets
- Non-root user in Docker container
- Rate limiting enabled
- Security headers in nginx
- Database SSL mode enabled

✅ **Recommended:**
- Set up firewall (UFW):
  ```bash
  ufw allow 22/tcp   # SSH
  ufw allow 80/tcp   # HTTP
  ufw allow 443/tcp  # HTTPS
  ufw enable
  ```
- Regular backups of Digital Ocean database
- Set up monitoring (Uptime Robot, etc.)
- Rotate JWT secret periodically
- Keep Docker images updated

---

## 📝 Post-Deployment Checklist

- [ ] Backend API accessible at `https://api.yourdomain.com`
- [ ] Health check returns 200: `https://api.yourdomain.com/health`
- [ ] Frontend accessible at `https://yourdomain.com`
- [ ] Google OAuth login works
- [ ] Database migrations completed
- [ ] SSL certificates installed and auto-renewal configured
- [ ] CORS configured correctly
- [ ] Firewall configured
- [ ] Backup strategy in place
- [ ] Monitoring/alerting set up (optional but recommended)

---

## 🎉 Success!

Your Tornetic application is now live in production!

- **Frontend**: https://yourdomain.com
- **API**: https://api.yourdomain.com
- **API Docs**: https://api.yourdomain.com/docs

For questions or issues, refer to the troubleshooting section above.
