# 🚀 Local Deployment Guide

Complete guide to deploy the Padel Tournament Management System locally with the new Admin Panel.

## ✅ Current Status

**Backend**: ✅ Running on http://localhost:8000
**Frontend**: ✅ Running on http://localhost:3000
**Database**: ✅ PostgreSQL running

---

## 📋 Prerequisites

Make sure you have installed:
- Docker & Docker Compose
- Node.js (v14+) and npm
- Make (for convenience commands)

---

## 🎯 Quick Start (Everything Running)

### Backend is Already Running ✅

The backend is currently running via Docker. If you need to restart:

```bash
# Stop backend
make down

# Start backend (database + API)
make dev

# Or start full stack (backend + frontend in Docker)
make dev-full
```

### Frontend is Already Running ✅

The React frontend is running on port 3000. If you need to restart:

```bash
# In the project root
cd padel-frontend
npm start
```

---

## 🔐 Create Your First Admin User

To access the admin panel, you need a superuser account:

### Option 1: Direct Database Update (Recommended for Development)

```bash
# Get your email from an existing user
docker exec -it padel_db psql -U postgres -d torneticdb -c "SELECT id, email, full_name FROM users LIMIT 5;"

# Make a user superuser (replace email with yours)
docker exec -it padel_db psql -U postgres -d torneticdb -c "UPDATE users SET is_superuser = TRUE WHERE email = 'your-email@example.com';"

# Verify it worked
docker exec -it padel_db psql -U postgres -d torneticdb -c "SELECT id, email, full_name, is_superuser FROM users WHERE is_superuser = TRUE;"
```

### Option 2: Interactive Database Shell

```bash
# Connect to database
make connect-db

# In PostgreSQL shell:
\c torneticdb

-- View existing users
SELECT id, email, full_name, is_superuser FROM users;

-- Make yourself admin (replace email)
UPDATE users SET is_superuser = TRUE WHERE email = 'your-email@example.com';

-- Verify
SELECT id, email, full_name, is_superuser FROM users WHERE is_superuser = TRUE;

-- Exit
\q
```

---

## 🌐 Access Points

Once everything is running:

| Service | URL | Description |
|---------|-----|-------------|
| **Frontend** | http://localhost:3000 | Main application |
| **Backend API** | http://localhost:8000 | REST API |
| **API Docs** | http://localhost:8000/docs | Swagger UI |
| **Admin Dashboard** | http://localhost:3000/admin | Admin panel (superuser only) |
| **Database** | localhost:5432 | PostgreSQL |

---

## 📱 Using the Application

### 1. Regular User Flow

1. **Register/Login**
   - Go to http://localhost:3000
   - Click "Login" or "Register"
   - Create account with email/password or Google OAuth

2. **Use the App**
   - Create tournaments
   - Join tournaments
   - View matches and results
   - Check leaderboards

### 2. Admin User Flow

1. **Login as Admin**
   - Login with your superuser account
   - Navigate to http://localhost:3000/admin

2. **Admin Dashboard**
   - View system statistics
   - Monitor user activity
   - Check tournament metrics

3. **User Management**
   - Click "Manage Users" or go to `/admin/users`
   - Search and filter users
   - View user details and statistics
   - Perform admin actions:
     - Activate/Deactivate users
     - Verify users
     - Make users superuser
     - Delete users (soft or hard)

---

## 🛠️ Development Commands

### Backend Commands

```bash
# Start backend only (recommended for development)
make dev

# View backend logs
make logs-backend

# Connect to backend container
make connect-backend

# Run migrations
make migration m="description"
make fix-migration-sync

# Connect to database
make connect-db

# Reset database (WARNING: loses all data!)
make reset-db

# Run tests
make test
make test-unit
make test-integration
```

### Frontend Commands

```bash
cd padel-frontend

# Start development server
npm start

# Build for production
npm run build

# Run tests
npm test

# Install dependencies
npm install
```

### Docker Commands

```bash
# View all containers
docker ps

# View logs for specific service
docker logs padel_web
docker logs padel_db

# Restart a service
docker restart padel_web
docker restart padel_db

# Stop everything
make down

# Start full stack
make dev-full

# Force recreate containers
docker compose up --force-recreate
```

---

## 🔍 Checking Everything Works

### Backend Health Check

```bash
# Check API is running
curl http://localhost:8000/health

# Expected response:
# {"status":"healthy","service":"tornetic-api"}
```

### Admin Endpoints Check (requires auth token)

```bash
# First login and get token (replace with your credentials)
TOKEN=$(curl -X POST http://localhost:8000/api/v1/auth/jwt/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=your-email@example.com&password=yourpassword" \
  | jq -r '.access_token')

# Check admin stats (requires superuser)
curl http://localhost:8000/api/v1/admin/stats/overview \
  -H "Authorization: Bearer $TOKEN"
```

### Frontend Check

Open http://localhost:3000 in your browser - you should see the landing page.

---

## 📊 Monitoring & Debugging

### View Application Logs

```bash
# Backend logs (live)
make logs-backend

# Frontend logs (in the terminal where npm start is running)
# Or check browser console (F12)

# Database logs
docker logs padel_db
```

### Check Database Contents

```bash
# Connect to database
make connect-db

# Useful queries:
\c torneticdb

-- View all users
SELECT id, email, full_name, is_superuser, is_active, is_verified FROM users;

-- View all tournaments
SELECT id, name, status, created_at FROM tournaments ORDER BY created_at DESC LIMIT 10;

-- View audit logs
SELECT id, admin_id, action_type, target_type, target_id, timestamp FROM audit_logs ORDER BY timestamp DESC LIMIT 10;

-- Count users by status
SELECT is_active, is_verified, is_superuser, COUNT(*) FROM users GROUP BY is_active, is_verified, is_superuser;

\q
```

### Debug Mode

If you encounter issues:

```bash
# Check container status
docker ps -a

# Check backend health
curl http://localhost:8000/health

# Check database connection
docker exec -it padel_db psql -U postgres -c "SELECT version();"

# View environment variables (backend)
docker exec -it padel_web env | grep DB

# Restart everything
make down
make dev
cd padel-frontend && npm start
```

---

## 🔧 Troubleshooting

### Backend Issues

**Backend not starting:**
```bash
# Check logs
make logs-backend

# Common issues:
# - Database not ready: wait a few seconds and restart
# - Port 8000 in use: kill process or change port
make down
make dev
```

**Database connection errors:**
```bash
# Reset database
make reset-db

# Rerun migrations
make fix-migration-sync
```

### Frontend Issues

**Frontend not starting:**
```bash
cd padel-frontend

# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Start again
npm start
```

**CORS errors:**
- Check that backend is running on port 8000
- Verify CORS configuration in `app/main.py` includes `http://localhost:3000`

**Admin panel not accessible:**
1. Verify you're logged in as superuser
2. Check console for errors (F12)
3. Verify backend is running: `curl http://localhost:8000/api/v1/admin/stats/overview -H "Authorization: Bearer YOUR_TOKEN"`

### Database Issues

**Can't connect to database:**
```bash
# Check database is running
docker ps | grep padel_db

# Restart database
docker restart padel_db

# Wait for it to be healthy
docker ps
```

**Migration errors:**
```bash
# Check migration status
make migration-status

# Force sync
make fix-migration-sync

# If all else fails, reset (WARNING: loses data!)
make reset-db
```

---

## 🔄 Restarting Everything from Scratch

If you want to start completely fresh:

```bash
# Stop all services
make down
pkill -f "react-scripts start" # If frontend is running

# Reset database (WARNING: loses all data!)
make reset-db

# Start backend
make dev

# Wait for backend to be ready (check logs)
make logs-backend

# In a new terminal, start frontend
cd padel-frontend
npm start

# Create admin user (see "Create Your First Admin User" section)
```

---

## 📝 Environment Variables

### Backend (.env)

The backend uses environment variables from `.env` file:

```bash
# Database
DB_USERNAME=postgres
DB_PASSWORD=postgres
DB_NAME=torneticdb
DB_HOST=db
DB_PORT=5432

# JWT
JWT_SECRET_KEY=your-secret-key
JWT_EXPIRE_MINUTES=60

# Google OAuth
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
```

### Frontend (.env)

Create `padel-frontend/.env` if it doesn't exist:

```bash
REACT_APP_API_URL=http://localhost:8000/api/v1
```

---

## ✅ Verification Checklist

- [ ] Backend running on port 8000
- [ ] Frontend running on port 3000
- [ ] Database accessible
- [ ] Can login to application
- [ ] Admin user created (is_superuser = TRUE)
- [ ] Can access `/admin` as admin user
- [ ] Can view `/admin/users`
- [ ] Non-admin users blocked from admin panel

---

## 🎉 You're All Set!

Your complete Padel Tournament Management System with Admin Panel is now running locally!

### Quick Access Links

- **Main App**: http://localhost:3000
- **Admin Panel**: http://localhost:3000/admin
- **API Docs**: http://localhost:8000/docs
- **API Health**: http://localhost:8000/health

### Next Steps

1. ✅ Login and explore the regular app
2. ✅ Login as admin and explore the admin panel
3. ✅ Create some test tournaments
4. ✅ Try managing users in the admin panel
5. 🔮 (Optional) Implement tournament management page
6. 🔮 (Optional) Implement audit log viewer

Enjoy your new admin panel! 🎊
