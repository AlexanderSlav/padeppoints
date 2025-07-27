# Tournament Management - Frontend Testing Guide

This guide will help you test all the new tournament features that have been implemented.

## 🚀 Getting Started

1. **Start the Backend Server**
   ```bash
   cd /path/to/padelpoints
   uvicorn app.main:app --reload
   ```

2. **Start the Frontend Server**
   ```bash
   cd padel-frontend
   npm install  # if not already installed
   npm start
   ```

3. **Open your browser to**: `http://localhost:3000`

## 🧪 Features to Test

### 1. **Dashboard Updates** (`/dashboard`)
- ✅ New "Quick Actions" section with navigation buttons
- ✅ "Discover Tournaments" button links to tournament discovery
- ✅ "Create Tournament" button links to tournament creation
- ✅ "View Details" button on tournament cards links to tournament detail page

### 2. **Tournament Discovery** (`/tournaments`)
**Features to test:**
- ✅ **Filtering by Format**: Select AMERICANO/MEXICANO from dropdown
- ✅ **Filtering by Status**: Choose pending/active/completed
- ✅ **Location Search**: Type location name for partial matching
- ✅ **Date Range Filtering**: Set start date from/to
- ✅ **My Tournaments Toggle**: Show only tournaments created by you
- ✅ **Clear Filters**: Reset all filters button
- ✅ **Pagination**: Limit/offset controls (shows total count)

**Tournament Cards Features:**
- ✅ **Join Tournament**: Click "Join" button (only for pending tournaments)
- ✅ **Leave Tournament**: Click "Leave" button (if already joined)
- ✅ **Smart Join Status**: Shows different states:
  - "Join" (green) - Can join
  - "Already joined" - User is in tournament
  - "Tournament is full" - No more spots
  - "Tournament has already started" - Can't join active tournaments
- ✅ **Tournament Details**: Click tournament name to view details

### 3. **Tournament Detail Page** (`/tournaments/{id}`)
**Overview Tab:**
- ✅ Tournament information display
- ✅ Player count and statistics
- ✅ Status indicators and badges
- ✅ Join/Leave buttons (context-aware)
- ✅ Start Tournament button (for tournament creators)

**Players Tab:**
- ✅ List of all players in tournament
- ✅ Player details (name, email)
- ✅ Player count display

**Matches Tab:**
- ✅ Shows current round matches (when tournament is active)
- ✅ Team compositions for each match
- ✅ Score recording interface (for tournament creators)
- ✅ Match completion status

**Leaderboard Tab:**
- ✅ Player rankings by score
- ✅ Tournament winner display (when completed)
- ✅ Current points for each player

### 4. **Tournament Creation** (`/create-tournament`)
- ✅ All existing functionality still works
- ✅ Created tournaments appear in "My Tournaments"

## 🎯 Test Scenarios

### Scenario 1: **Creating and Managing a Tournament**
1. Login to the application
2. Go to Dashboard → Click "Create Tournament"
3. Create a new tournament with AMERICANO format
4. Navigate to Tournament Discovery
5. Find your tournament and verify it shows "MY TOURNAMENT" badge
6. Click tournament name to view details
7. Invite friends or use multiple accounts to join
8. Start the tournament when you have enough players
9. Record match results as matches are played
10. View the leaderboard as scores are updated

### Scenario 2: **Joining Someone's Tournament**
1. Login with a different user account
2. Navigate to Tournament Discovery
3. Find a pending tournament (not created by you)
4. Click "Join" button
5. Verify you receive success message
6. Check tournament detail page to see yourself in players list
7. Try to join again (should show "Already joined")
8. Leave the tournament and verify removal

### Scenario 3: **Advanced Filtering**
1. Go to Tournament Discovery
2. Create tournaments with different:
   - Formats (AMERICANO/MEXICANO)
   - Locations (Madrid, Barcelona, etc.)
   - Start dates (past, today, future)
3. Test each filter combination:
   - Filter by format only
   - Filter by location search
   - Filter by date range
   - Toggle "My Tournaments Only"
   - Combined filters
4. Verify result counts and clear filters functionality

### Scenario 4: **Tournament Lifecycle**
1. **Creation**: Create tournament (status: pending)
2. **Joining**: Multiple players join
3. **Starting**: Creator starts tournament (status: active)
4. **Playing**: Record match results
5. **Completion**: All rounds completed (status: completed)
6. **Leaderboard**: View final results and winner

## 🐛 Things to Watch For

### Expected Behavior:
- ✅ Only tournament creators can start tournaments
- ✅ Only tournament creators can record match results
- ✅ Players can only join pending tournaments
- ✅ Players can only leave pending tournaments
- ✅ Tournament cards show appropriate action buttons
- ✅ Real-time updates when joining/leaving tournaments
- ✅ Proper validation messages for all actions

### Error Cases to Test:
- ❌ Try to join a full tournament
- ❌ Try to join an active tournament
- ❌ Try to start tournament with insufficient players
- ❌ Try to record invalid match scores
- ❌ Access tournaments with invalid IDs

## 🔧 API Endpoints Being Used

The frontend now uses these new endpoints:
- `GET /tournaments` - Tournament discovery with filters
- `GET /tournaments/my` - User's created tournaments
- `GET /tournaments/joined` - User's joined tournaments
- `GET /tournaments/{id}` - Tournament details
- `POST /tournaments/{id}/join` - Join tournament
- `POST /tournaments/{id}/leave` - Leave tournament
- `GET /tournaments/{id}/can-join` - Check join eligibility
- `GET /tournaments/{id}/players` - Tournament players
- `POST /tournaments/{id}/start` - Start tournament
- `GET /tournaments/{id}/matches/current` - Current matches
- `PUT /tournaments/matches/{id}/result` - Record results
- `GET /tournaments/{id}/leaderboard` - Tournament standings

## 🎉 Success Criteria

You've successfully tested the features when:
1. ✅ Tournament discovery filters work correctly
2. ✅ Join/leave functionality works with proper validation
3. ✅ Tournament detail page shows complete information
4. ✅ Tournament lifecycle flows smoothly from creation to completion
5. ✅ Leaderboard updates correctly as matches are completed
6. ✅ Navigation between pages works seamlessly
7. ✅ Error messages are clear and helpful
8. ✅ UI is responsive and user-friendly

---

**Have fun testing the new tournament management system! 🎾** 