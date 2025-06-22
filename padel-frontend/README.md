# 🎾 Padel Points Frontend

A super simple React frontend for the Padel Points tournament management system.

## Features

- 🔐 **Google OAuth Authentication**
- 🏆 **Tournament Creation**
- 📊 **Tournament Dashboard**
- 📱 **Responsive Design**
- ✨ **Clean, Modern UI**

## Prerequisites

- Node.js 18+ 
- npm or yarn
- FastAPI backend running on `http://localhost:8000`

## Quick Start

### 1. Install Dependencies

```bash
npm install
```

### 2. Start Development Server

```bash
npm start
```

The app will open at `http://localhost:3000`

## Usage

### Login Methods

1. **Google OAuth** (Production)
   - Click "Login with Google"
   - Authenticate with your Google account
   - Get redirected back to the app

2. **Test Login** (Development)
   - Click "Test Login" for quick development access
   - Creates a mock user session

### Creating Tournaments

1. Login to the app
2. Click "Create Tournament" on the dashboard
3. Fill in tournament details:
   - Name (required)
   - Description
   - Location (required)
   - Start Date (required)
   - Entry Fee (required)
   - Max Players (8, 16, 32, or 64)
4. Click "Create Tournament"

## API Integration

The frontend communicates with the FastAPI backend at:
- Base URL: `http://localhost:8000`
- Authentication: JWT Bearer tokens
- Endpoints:
  - `GET /auth/google/login` - Get Google OAuth URL
  - `POST /auth/google/callback` - Handle OAuth callback
  - `POST /auth/test-login` - Development login
  - `GET /auth/me` - Get current user
  - `GET /tournaments` - List tournaments
  - `POST /tournaments` - Create tournament

## Project Structure

```
padel-frontend/
├── public/
│   └── index.html          # Main HTML template
├── src/
│   ├── components/
│   │   └── AuthContext.js  # Authentication context
│   ├── pages/
│   │   ├── LoginPage.js    # Login page
│   │   ├── CallbackPage.js # OAuth callback handler
│   │   ├── DashboardPage.js # Main dashboard
│   │   └── CreateTournamentPage.js # Tournament creation
│   ├── services/
│   │   └── api.js          # API service layer
│   ├── App.js              # Main app component
│   └── index.js            # Entry point
├── package.json
└── README.md
```

## Authentication Flow

1. **User clicks "Login with Google"**
2. **Frontend calls** `GET /auth/google/login`
3. **Backend returns** Google OAuth URL
4. **User redirects to Google** for authentication
5. **Google redirects back** to `/auth/callback?code=...`
6. **Frontend calls** `POST /auth/google/callback` with code
7. **Backend returns** JWT token and user data
8. **Frontend stores** token and redirects to dashboard

## Styling

The app uses inline styles with CSS classes defined in `public/index.html`:
- Clean, modern design
- Purple gradient background
- Card-based layout
- Responsive design
- Hover effects and animations

## Available Scripts

- `npm start` - Start development server
- `npm build` - Build for production
- `npm test` - Run tests
- `npm run eject` - Eject from Create React App

## Environment Setup

### Backend Requirements

Make sure your FastAPI backend is running with:
- CORS enabled for `http://localhost:3000`
- Google OAuth configured
- JWT authentication working

### Google OAuth Setup

The backend needs Google OAuth credentials configured:
- Google Client ID
- Google Client Secret  
- Redirect URI: `http://localhost:3000/auth/callback`

## Deployment

### Development
```bash
npm start
```

### Production
```bash
npm run build
# Serve the build folder
```

## Notes

- The `proxy` field in `package.json` routes API calls to the backend
- Authentication state is managed with React Context
- JWT tokens are stored in localStorage
- The app automatically handles token expiration
- All API calls include the JWT token in headers

## Troubleshooting

### Common Issues

1. **"Not Found" on OAuth callback**
   - Make sure the backend has both GET and POST `/auth/google/callback` endpoints
   - Check that the redirect URI matches in Google OAuth settings

2. **CORS errors**
   - Ensure the backend allows `http://localhost:3000` in CORS settings

3. **API connection issues**
   - Verify the backend is running on `http://localhost:8000`
   - Check the proxy configuration in `package.json`

4. **Authentication failures**
   - Check browser console for errors
   - Verify JWT token is being stored and sent correctly

## License

MIT License - feel free to use this code for your own projects! 