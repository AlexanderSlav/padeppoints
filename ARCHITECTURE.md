# 🏗️ Tornetic System Architecture

This document describes the system architecture of Tornetic, a padel tournament management platform, using the C4 model approach.

## 📋 Table of Contents

- [System Context](#system-context)
- [Container Architecture](#container-architecture)
- [Current Deployment](#current-deployment)
- [Future Architecture (with iOS App)](#future-architecture-with-ios-app)
- [Technology Stack](#technology-stack)
- [Data Flow](#data-flow)

---

## 🌍 System Context

### What is Tornetic?

Tornetic is a cloud-based tournament management system for padel (paddle tennis) that enables:
- Tournament organizers to create and manage tournaments
- Players to register, view schedules, and track scores
- Real-time leaderboards and statistics
- Support for multiple tournament formats (Americano, Mexicano planned)

### Users & External Systems

```
┌─────────────────────────────────────────────────────────────────────┐
│                        TORNETIC SYSTEM                              │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                                                              │  │
│  │              Tournament Management Platform                  │  │
│  │        (Web App + API + Database + Rating System)           │  │
│  │                                                              │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
         ▲                ▲                    ▲
         │                │                    │
         │                │                    │
    ┌────────┐      ┌────────┐          ┌──────────┐
    │Tournament│      │ Player │          │  Google  │
    │Organizer │      │        │          │  OAuth   │
    └────────┘      └────────┘          └──────────┘

    Creates &         Registers &        Authentication
    manages          participates         provider
    tournaments      in matches
```

**Key Actors:**
- **Tournament Organizers**: Create tournaments, manage rounds, enter scores
- **Players**: Register for tournaments, view schedules, track performance
- **Google OAuth**: External authentication provider

---

## 📦 Container Architecture

### High-Level Components

```
┌──────────────────────────────────────────────────────────────────────┐
│                         USER'S BROWSER                               │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │                  React Web Application                         │ │
│  │              (SPA - Single Page Application)                   │ │
│  │                                                                │ │
│  │  • Tournament browsing      • Player registration             │ │
│  │  • Live leaderboards        • Score entry                     │ │
│  │  • Profile management       • Statistics                      │ │
│  └────────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────┘
                              │
                              │ HTTPS / JSON
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────────┐
│                      HETZNER VPS SERVER                              │
│                       (128.140.4.76)                                 │
│                                                                      │
│  ┌────────────────┐                                                 │
│  │     nginx      │  Reverse proxy, SSL termination, CORS           │
│  │  (Port 80/443) │                                                 │
│  └────────────────┘                                                 │
│          │                                                           │
│          ▼                                                           │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │              FastAPI Application (Docker)                  │    │
│  │                    (Port 8000)                             │    │
│  │                                                            │    │
│  │  API Layer:                                                │    │
│  │  • /api/v1/tournaments  • /api/v1/auth                    │    │
│  │  • /api/v1/users        • /api/v1/players                 │    │
│  │                                                            │    │
│  │  Business Logic:                                           │    │
│  │  • TournamentService    • AmericanoTournamentService      │    │
│  │  • RatingService        • AuthService (fastapi-users)     │    │
│  │                                                            │    │
│  │  Data Access:                                              │    │
│  │  • SQLAlchemy ORM       • Repository Pattern              │    │
│  │  • Alembic Migrations   • Async PostgreSQL Driver         │    │
│  └────────────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────────────┘
                              │
                              │ PostgreSQL Protocol (SSL)
                              │ Port 25060
                              ▼
┌──────────────────────────────────────────────────────────────────────┐
│                   DIGITAL OCEAN MANAGED DATABASE                     │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │              PostgreSQL 17 Database                        │    │
│  │                                                            │    │
│  │  Tables:                                                   │    │
│  │  • users               • tournaments                       │    │
│  │  • rounds              • tournament_player                 │    │
│  │  • player_ratings      • rating_history                   │    │
│  │  • tournament_results  • alembic_version                  │    │
│  │                                                            │    │
│  │  Features:                                                 │    │
│  │  • Automated backups   • SSL/TLS encryption               │    │
│  │  • Connection pooling  • Performance monitoring           │    │
│  └────────────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Current Deployment Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         INTERNET / DNS                                  │
│                                                                         │
│  tornetic.com (A → Cloudflare)                                         │
│  api.tornetic.com (A → 128.140.4.76)                                   │
└─────────────────────────────────────────────────────────────────────────┘
          │                                    │
          │                                    │
          ▼                                    ▼
┌──────────────────────────┐        ┌──────────────────────────────┐
│   CLOUDFLARE PAGES       │        │    HETZNER VPS (€4-10/mo)   │
│   (FREE)                 │        │    Ubuntu 24.04              │
│                          │        │    IP: 128.140.4.76          │
│  ┌────────────────────┐  │        │                              │
│  │  React Frontend    │  │        │  ┌────────────────────────┐  │
│  │  (Static Build)    │  │        │  │    nginx + Certbot     │  │
│  │                    │  │        │  │   (SSL Termination)    │  │
│  │  • HTML/CSS/JS     │  │        │  └────────────────────────┘  │
│  │  • Code Splitting  │  │        │            │                 │
│  │  • Asset Caching   │  │        │            ▼                 │
│  └────────────────────┘  │        │  ┌────────────────────────┐  │
│                          │        │  │   Docker Container     │  │
│  Features:               │        │  │                        │  │
│  • Global CDN            │        │  │  ┌──────────────────┐  │  │
│  • Auto SSL              │        │  │  │  FastAPI + Gunicorn  │
│  • GitHub Auto-deploy    │        │  │  │  (4 workers)     │  │  │
│  • Unlimited Bandwidth   │        │  │  │                  │  │  │
│  • HTTP/2 & HTTP/3       │        │  │  │  Port: 8000      │  │  │
│  • DDoS Protection       │        │  │  └──────────────────┘  │  │
└──────────────────────────┘        │  └────────────────────────┘  │
                                    │                              │
         API Calls                  │  Resources:                  │
    (https://api.tornetic.com)      │  • 2 vCPU                    │
         └──────────────────────────┤  • 4 GB RAM                  │
                                    │  • 40 GB SSD                 │
                                    └──────────────────────────────┘
                                                │
                                                │ PostgreSQL
                                                │ SSL (Port 25060)
                                                ▼
                              ┌──────────────────────────────────┐
                              │  DIGITAL OCEAN MANAGED DB        │
                              │  ($15/mo)                        │
                              │                                  │
                              │  ┌────────────────────────────┐  │
                              │  │  PostgreSQL 17             │  │
                              │  │                            │  │
                              │  │  • 1 GB RAM                │  │
                              │  │  • 10 GB Storage           │  │
                              │  │  • Daily Backups           │  │
                              │  │  • SSL Required            │  │
                              │  └────────────────────────────┘  │
                              └──────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│  EXTERNAL SERVICES                                                      │
│                                                                         │
│  ┌─────────────────┐              ┌──────────────────┐                 │
│  │  Google OAuth   │              │  Let's Encrypt   │                 │
│  │                 │              │                  │                 │
│  │  Authentication │              │  SSL Certificates│                 │
│  └─────────────────┘              └──────────────────┘                 │
└─────────────────────────────────────────────────────────────────────────┘

TOTAL MONTHLY COST: ~€20-25 (~$22-27)
```

### Deployment Details

**Frontend (Cloudflare Pages):**
- Build: `cd padel-frontend && npm install && npm run build`
- Output: `padel-frontend/build`
- Auto-deploys from GitHub on push to `main` branch
- Served via Cloudflare's global CDN (200+ locations)

**Backend (Hetzner VPS):**
- Docker Compose production setup
- Gunicorn with 4 Uvicorn workers
- Nginx reverse proxy with:
  - SSL/TLS (Let's Encrypt)
  - CORS headers
  - Security headers (HSTS, CSP, etc.)
  - Rate limiting via FastAPI middleware

**Database (Digital Ocean):**
- Managed PostgreSQL 17
- Automated daily backups (7-day retention)
- SSL-only connections
- Connection pooling enabled

---

## 📱 Future Architecture (with iOS App)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                            CLIENTS                                      │
│                                                                         │
│  ┌──────────────────┐    ┌──────────────────┐    ┌─────────────────┐   │
│  │   Web Browser    │    │   iOS App        │    │  Android App    │   │
│  │                  │    │                  │    │  (Future)       │   │
│  │  React SPA       │    │  Swift/SwiftUI   │    │                 │   │
│  │  (Cloudflare)    │    │  Native iOS      │    │  Kotlin/Jetpack │   │
│  │                  │    │                  │    │                 │   │
│  └──────────────────┘    └──────────────────┘    └─────────────────┘   │
│         │                        │                        │             │
└─────────────────────────────────────────────────────────────────────────┘
          │                        │                        │
          │                        │                        │
          └────────────────────────┼────────────────────────┘
                                   │
                         HTTPS / JSON REST API
                         (api.tornetic.com)
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      API GATEWAY / LOAD BALANCER                        │
│                         (Future Enhancement)                            │
│                                                                         │
│  ┌────────────────────────────────────────────────────────────────┐    │
│  │  Nginx or Cloud Load Balancer                                  │    │
│  │                                                                 │    │
│  │  • SSL Termination              • Rate Limiting                │    │
│  │  • Request Routing              • API Versioning               │    │
│  │  • Health Checks                • DDoS Protection              │    │
│  └────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────┘
                                   │
                    ┌──────────────┼──────────────┐
                    │              │              │
                    ▼              ▼              ▼
         ┌────────────────┐ ┌────────────────┐ ┌────────────────┐
         │  API Server 1  │ │  API Server 2  │ │  API Server 3  │
         │  (FastAPI)     │ │  (FastAPI)     │ │  (FastAPI)     │
         │                │ │                │ │                │
         │  • Auth        │ │  • Tournaments │ │  • Ratings     │
         │  • Users       │ │  • Rounds      │ │  • Stats       │
         └────────────────┘ └────────────────┘ └────────────────┘
                    │              │              │
                    └──────────────┼──────────────┘
                                   │
                                   ▼
                  ┌─────────────────────────────────┐
                  │   PostgreSQL Database Cluster   │
                  │                                 │
                  │  Primary + Read Replicas        │
                  └─────────────────────────────────┘
                                   │
                                   │
         ┌─────────────────────────┼─────────────────────────┐
         │                         │                         │
         ▼                         ▼                         ▼
  ┌──────────────┐        ┌──────────────┐        ┌──────────────┐
  │   Redis      │        │   S3 / CDN   │        │  Push Notif  │
  │   Cache      │        │   Storage    │        │   Service    │
  │              │        │              │        │              │
  │  • Sessions  │        │  • Images    │        │  • APNs (iOS)│
  │  • Rankings  │        │  • Avatars   │        │  • FCM (And.)│
  └──────────────┘        └──────────────┘        └──────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│  ANALYTICS & MONITORING                                                 │
│                                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                  │
│  │  Prometheus  │  │   Grafana    │  │  Error Track │                  │
│  │   Metrics    │  │  Dashboards  │  │  (Sentry)    │                  │
│  └──────────────┘  └──────────────┘  └──────────────┘                  │
└─────────────────────────────────────────────────────────────────────────┘
```

### iOS App Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    iOS APPLICATION                              │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                    PRESENTATION LAYER                     │  │
│  │                                                           │  │
│  │  SwiftUI Views:                                           │  │
│  │  • TournamentListView      • TournamentDetailView        │  │
│  │  • LeaderboardView         • ProfileView                 │  │
│  │  • MatchResultsView        • RegistrationView            │  │
│  └───────────────────────────────────────────────────────────┘  │
│                            │                                    │
│                            ▼                                    │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                    VIEW MODELS (MVVM)                     │  │
│  │                                                           │  │
│  │  • TournamentViewModel     • AuthViewModel               │  │
│  │  • LeaderboardViewModel    • ProfileViewModel            │  │
│  │                                                           │  │
│  │  State Management: Combine / @Published                  │  │
│  └───────────────────────────────────────────────────────────┘  │
│                            │                                    │
│                            ▼                                    │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                    SERVICE LAYER                          │  │
│  │                                                           │  │
│  │  • APIService (URLSession)                                │  │
│  │  • AuthenticationService                                  │  │
│  │  • LocalStorageService (CoreData / UserDefaults)          │  │
│  │  • NotificationService                                    │  │
│  └───────────────────────────────────────────────────────────┘  │
│                            │                                    │
│                            ▼                                    │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                    DATA LAYER                             │  │
│  │                                                           │  │
│  │  • Network Models (Codable)                               │  │
│  │  • CoreData Models (Local Cache)                          │  │
│  │  • Keychain (Secure Token Storage)                        │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                            │
                            │ HTTPS
                            ▼
                  ┌──────────────────┐
                  │  Backend API     │
                  │  (FastAPI)       │
                  └──────────────────┘
```

### iOS Features Roadmap

**Phase 1 (MVP):**
- ✅ User authentication (OAuth + Email/Password)
- ✅ Browse tournaments
- ✅ Register for tournaments
- ✅ View live leaderboards
- ✅ View match schedules

**Phase 2:**
- 📱 Push notifications for match updates
- 📱 Offline mode with local caching
- 📱 QR code scanning for check-in
- 📱 Camera integration for score entry

**Phase 3:**
- 📱 Apple Watch companion app
- 📱 HealthKit integration (track activity)
- 📱 Social features (player connections)
- 📱 In-app payments (tournament fees)

---

## 🛠️ Technology Stack

### Frontend

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Framework** | React 18 | UI framework |
| **Routing** | React Router v6 | Client-side routing |
| **HTTP Client** | Axios | API communication |
| **Charts** | Recharts | Data visualization |
| **Styling** | CSS Modules | Component styling |
| **Build Tool** | Create React App | Bundling & optimization |
| **Hosting** | Cloudflare Pages | CDN & static hosting |

### Backend

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Framework** | FastAPI 0.115.8 | REST API framework |
| **Language** | Python 3.11 | Core language |
| **Server** | Gunicorn + Uvicorn | ASGI server (production) |
| **ORM** | SQLAlchemy 2.0 (async) | Database abstraction |
| **Migrations** | Alembic 1.14.1 | Schema versioning |
| **Auth** | fastapi-users 14.0.1 | Authentication system |
| **OAuth** | httpx-oauth 0.16.1 | Google OAuth integration |
| **Validation** | Pydantic 2.10.6 | Data validation |
| **Rate Limiting** | SlowAPI 0.1.9 | API rate limiting |
| **Logging** | Loguru 0.7.3 | Structured logging |

### Database

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **DBMS** | PostgreSQL 17 | Primary database |
| **Driver** | asyncpg 0.30.0 | Async PostgreSQL driver |
| **Connection Pool** | SQLAlchemy pool | Connection management |
| **Backup** | Digital Ocean automated | Daily backups (7-day retention) |

### Infrastructure

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Containerization** | Docker + Docker Compose | Application packaging |
| **Reverse Proxy** | Nginx | Load balancing, SSL |
| **SSL/TLS** | Let's Encrypt (Certbot) | Free SSL certificates |
| **VPS** | Hetzner Cloud | Backend hosting |
| **CDN** | Cloudflare | Frontend delivery |
| **Managed DB** | Digital Ocean | Database hosting |

### iOS (Planned)

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Language** | Swift 5.9+ | Native iOS development |
| **UI Framework** | SwiftUI | Declarative UI |
| **Architecture** | MVVM | Design pattern |
| **Networking** | URLSession + Combine | HTTP client |
| **Local Storage** | CoreData | Offline caching |
| **Secure Storage** | Keychain | Token storage |
| **Push Notifications** | APNs | Real-time updates |

---

## 🔄 Data Flow

### User Authentication Flow

```
┌─────────┐                ┌──────────┐                ┌─────────┐
│  Client │                │    API   │                │   DB    │
└────┬────┘                └────┬─────┘                └────┬────┘
     │                          │                           │
     │ POST /auth/jwt/login     │                           │
     │─────────────────────────>│                           │
     │ (email, password)        │                           │
     │                          │ Verify credentials        │
     │                          │──────────────────────────>│
     │                          │                           │
     │                          │ User data                 │
     │                          │<──────────────────────────│
     │                          │                           │
     │                          │ Generate JWT              │
     │                          │                           │
     │ JWT token + user data    │                           │
     │<─────────────────────────│                           │
     │                          │                           │
     │ Store token (localStorage)                           │
     │                          │                           │
     │ GET /users/me            │                           │
     │─────────────────────────>│                           │
     │ Authorization: Bearer... │                           │
     │                          │ Validate JWT              │
     │                          │                           │
     │                          │ Fetch user                │
     │                          │──────────────────────────>│
     │                          │                           │
     │ User profile data        │                           │
     │<─────────────────────────│                           │
```

### Tournament Creation & Management Flow

```
┌──────────┐         ┌──────────┐         ┌──────────────────┐         ┌─────┐
│Organizer │         │    API   │         │  Tournament      │         │ DB  │
│          │         │          │         │  Service         │         │     │
└────┬─────┘         └────┬─────┘         └────┬─────────────┘         └──┬──┘
     │                    │                     │                          │
     │ POST /tournaments  │                     │                          │
     │───────────────────>│                     │                          │
     │                    │                     │                          │
     │                    │ Create tournament   │                          │
     │                    │────────────────────>│                          │
     │                    │                     │                          │
     │                    │                     │ Save tournament          │
     │                    │                     │─────────────────────────>│
     │                    │                     │                          │
     │                    │                     │ Tournament created       │
     │                    │                     │<─────────────────────────│
     │                    │                     │                          │
     │                    │ Tournament data     │                          │
     │                    │<────────────────────│                          │
     │                    │                     │                          │
     │ Tournament ID      │                     │                          │
     │<───────────────────│                     │                          │
     │                    │                     │                          │
     │ POST /tournaments/{id}/start              │                          │
     │───────────────────>│                     │                          │
     │                    │                     │                          │
     │                    │ Generate rounds     │                          │
     │                    │────────────────────>│                          │
     │                    │                     │                          │
     │                    │                     │ Calculate pairings       │
     │                    │                     │ (Americano algorithm)    │
     │                    │                     │                          │
     │                    │                     │ Save rounds              │
     │                    │                     │─────────────────────────>│
     │                    │                     │                          │
     │                    │                     │ Rounds saved             │
     │                    │                     │<─────────────────────────│
     │                    │                     │                          │
     │                    │ Rounds data         │                          │
     │                    │<────────────────────│                          │
     │                    │                     │                          │
     │ Match schedule     │                     │                          │
     │<───────────────────│                     │                          │
```

### Rating System Update Flow

```
┌──────────┐    ┌──────────┐    ┌──────────────┐    ┌──────────┐    ┌─────┐
│Organizer │    │   API    │    │  Tournament  │    │  Rating  │    │ DB  │
│          │    │          │    │  Service     │    │  Service │    │     │
└────┬─────┘    └────┬─────┘    └──────┬───────┘    └────┬─────┘    └──┬──┘
     │               │                  │                 │             │
     │ PATCH /rounds/{id}/score         │                 │             │
     │──────────────>│                  │                 │             │
     │               │                  │                 │             │
     │               │ Update score     │                 │             │
     │               │─────────────────>│                 │             │
     │               │                  │                 │             │
     │               │                  │ Save score      │             │
     │               │                  │────────────────────────────────>│
     │               │                  │                 │             │
     │               │                  │ Calculate       │             │
     │               │                  │ player scores   │             │
     │               │                  │                 │             │
     │               │                  │ Update ratings  │             │
     │               │                  │────────────────>│             │
     │               │                  │                 │             │
     │               │                  │                 │ Get current │
     │               │                  │                 │ ratings     │
     │               │                  │                 │────────────>│
     │               │                  │                 │             │
     │               │                  │                 │ Calculate   │
     │               │                  │                 │ new ratings │
     │               │                  │                 │             │
     │               │                  │                 │ Save new    │
     │               │                  │                 │ ratings +   │
     │               │                  │                 │ history     │
     │               │                  │                 │────────────>│
     │               │                  │                 │             │
     │               │                  │ Ratings updated │             │
     │               │                  │<────────────────│             │
     │               │                  │                 │             │
     │               │ Score & rankings │                 │             │
     │               │<─────────────────│                 │             │
     │               │                  │                 │             │
     │ Updated data  │                  │                 │             │
     │<──────────────│                  │                 │             │
```

---

## 🔐 Security Measures

### Current Implementation

- ✅ SSL/TLS encryption (Let's Encrypt)
- ✅ HTTPS-only for all communications
- ✅ JWT-based authentication with secure token storage
- ✅ Password hashing (bcrypt via passlib)
- ✅ CORS configuration for allowed origins
- ✅ Rate limiting on API endpoints
- ✅ SQL injection prevention (SQLAlchemy ORM)
- ✅ Security headers (HSTS, CSP, X-Frame-Options)
- ✅ Database SSL mode required
- ✅ Environment variables for secrets (never committed)

### Planned Enhancements

- 🔄 API key rotation
- 🔄 Request signing for mobile apps
- 🔄 OAuth token refresh mechanism
- 🔄 2FA (Two-Factor Authentication)
- 🔄 IP-based rate limiting
- 🔄 DDoS protection (Cloudflare)
- 🔄 Automated security scanning (Dependabot)

---

## 📈 Scalability Considerations

### Current Limitations

- Single VPS server (vertical scaling only)
- Single database instance
- No caching layer
- No load balancing

### Future Scaling Strategy

1. **Horizontal Scaling**:
   - Multiple API server instances behind load balancer
   - Database read replicas for queries
   - Redis cache for frequently accessed data

2. **Performance Optimization**:
   - CDN for static assets (already implemented)
   - Database query optimization
   - API response caching
   - Connection pooling

3. **Infrastructure**:
   - Kubernetes for container orchestration
   - Auto-scaling based on load
   - Multi-region deployment
   - Managed Kubernetes (DigitalOcean, AWS EKS)

4. **Monitoring & Observability**:
   - Prometheus metrics collection
   - Grafana dashboards
   - Error tracking (Sentry)
   - Performance monitoring (New Relic / DataDog)

---

## 📊 Cost Analysis

### Current Monthly Costs

| Service | Cost | Notes |
|---------|------|-------|
| Cloudflare Pages | **FREE** | Unlimited bandwidth, auto SSL |
| Hetzner VPS | **€4-10** | 2 vCPU, 4 GB RAM, 40 GB SSD |
| Digital Ocean DB | **$15** | Managed PostgreSQL, automated backups |
| Domain (GoDaddy) | **~$1.25** | $15/year amortized |
| **TOTAL** | **~€20-25/mo** | **~$22-27/month** |

### Projected Costs with iOS App

| Service | Current | With iOS |
|---------|---------|----------|
| Cloudflare Pages | FREE | FREE |
| Hetzner VPS | €10/mo | €20/mo (upgraded) |
| Digital Ocean DB | $15/mo | $25/mo (upgraded) |
| Redis Cache | - | $10/mo |
| Push Notifications | - | FREE (APNs) |
| Apple Developer | - | $99/year (~$8.25/mo) |
| **TOTAL** | **~€25/mo** | **~€55-60/mo** |

---

## 🚦 System Status & Monitoring

### Health Checks

- `GET /health` - API health status
- `GET /` - Root endpoint (API running check)
- Database connection monitoring
- SSL certificate expiry monitoring (auto-renewal)

### Uptime Targets

- **API**: 99.5% uptime SLA
- **Database**: 99.9% uptime (managed service SLA)
- **Frontend**: 99.99% uptime (Cloudflare CDN)

---

## 📚 Related Documentation

- [Deployment Guide](DEPLOYMENT.md) - Step-by-step deployment instructions
- [Quick Reference](QUICK_REFERENCE.md) - Common commands and troubleshooting
- [Authentication System](docs/auth_system_design.md) - Auth architecture details
- [Development Guide](CLAUDE.md) - Local development setup

---

**Last Updated**: October 2, 2025
**Version**: 1.0.0
**Maintained by**: Tornetic Development Team
