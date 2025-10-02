# 🎾 Tornetic - Padel Tournament Management Platform

A modern, cloud-based tournament management system for padel (paddle tennis) that enables tournament organizers to create and manage tournaments, and players to register, view schedules, and track scores in real-time.

## 🌟 Features

- **Tournament Management**: Create and manage Americano and Mexicano format tournaments
- **Player Registration**: Easy sign-up and tournament registration
- **Live Leaderboards**: Real-time rankings and statistics
- **Dual Authentication**: Google OAuth2 and email/password login powered by [fastapi-users](https://github.com/fastapi-users/fastapi-users)
- **Rating System**: ELO-based player rating system with historical tracking
- **Mobile-First Design**: Responsive web interface optimized for all devices

## 🏗️ Architecture

Tornetic uses a modern cloud-native architecture with separation of concerns:

- **Frontend**: React SPA hosted on Cloudflare Pages (global CDN)
- **Backend**: FastAPI on Hetzner VPS with Docker
- **Database**: Managed PostgreSQL on Digital Ocean
- **Authentication**: fastapi-users with Google OAuth2 integration

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed system design, deployment diagrams, and future roadmap including iOS app architecture.

## 🚀 Quick Start

### Local Development

```bash
# Start backend + database
make dev

# Start frontend (in another terminal)
cd padel-frontend
npm install
npm start
```

Visit `http://localhost:3000` for the frontend and `http://localhost:8000/docs` for API documentation.

### Testing

```bash
# Run all tests
make test

# Run unit tests only
make test-unit

# Run with coverage
make test-coverage
```

## 📚 Documentation

- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System architecture, diagrams, and technology stack
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Production deployment guide
- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - Common commands and troubleshooting
- **[CLAUDE.md](CLAUDE.md)** - Development guide and project instructions
- **[docs/auth_system_design.md](docs/auth_system_design.md)** - Authentication system details

## 🛠️ Technology Stack

### Backend
- **FastAPI** 0.115.8 - Modern Python web framework
- **SQLAlchemy** 2.0 - Async ORM
- **PostgreSQL** 17 - Database
- **fastapi-users** 14.0.1 - Authentication
- **Pydantic** 2.10.6 - Data validation

### Frontend
- **React** 18 - UI framework
- **React Router** v6 - Routing
- **Axios** - HTTP client
- **Recharts** - Data visualization

### Infrastructure
- **Docker** + Docker Compose - Containerization
- **Nginx** - Reverse proxy & SSL
- **Let's Encrypt** - SSL certificates
- **Cloudflare Pages** - CDN & static hosting

## 🌐 Live Deployment

- **Web App**: https://tornetic.com
- **API**: https://api.tornetic.com
- **API Docs**: https://api.tornetic.com/docs

## 📱 Roadmap

- ✅ Web application (React)
- ✅ Americano tournament format
- ✅ Player rating system
- 🔄 Mexicano tournament format
- 📱 iOS native application (Swift/SwiftUI)
- 📱 Android application (Kotlin)
- 🔄 Real-time match updates via WebSocket
- 🔄 Push notifications
- 🔄 In-app payments

## 📊 System Status

- **Current Version**: 1.0.0
- **API Uptime**: 99.5%+
- **Monthly Cost**: ~€20-25 (~$22-27)
- **Active Users**: Growing 🚀

## 🤝 Contributing

This is a private project. For development guidelines, see [CLAUDE.md](CLAUDE.md).

## 📄 License

Proprietary - All rights reserved

---

**Built with ❤️ for the padel community**
