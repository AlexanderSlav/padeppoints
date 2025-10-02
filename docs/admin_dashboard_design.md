# Admin Dashboard Design Document

## Overview
A comprehensive admin panel for platform administrators to monitor system health, manage users, and maintain data integrity. Access is strictly limited to users with `is_superuser=True`.

## Architecture

### 1. Access Control Layer

#### Backend Authentication
- **Admin Dependency**: Already exists as `get_current_superuser` in `app/core/dependencies.py`
- **Usage**: All admin endpoints must use `Depends(get_current_superuser)`
- **Security**: Returns 403 Forbidden for non-superuser accounts

#### Frontend Protection
- **Route Guard**: React route wrapper to check user's `is_superuser` status
- **Redirect**: Non-admin users redirected to dashboard with error message
- **Navigation**: Admin menu item only visible to superusers

### 2. Database Schema Changes

#### User Model Enhancement
**Current**: User model already has `is_superuser` field ✓
**No changes needed** - existing structure supports admin roles

#### New Model: AuditLog
```python
class AuditLog(Base):
    id: UUID
    admin_id: str (FK -> User)
    action_type: enum (USER_DELETE, TOURNAMENT_EDIT, SCORE_RECALC)
    target_type: str (user, tournament, match)
    target_id: str
    details: JSON (old_values, new_values, reason)
    timestamp: datetime
    ip_address: str
```

**Purpose**: Track all admin actions for accountability and rollback capability

### 3. Backend API Endpoints

#### 3.1 Statistics & Analytics
**Base Route**: `/api/v1/admin/stats`

**GET `/api/v1/admin/stats/overview`**
```json
{
  "users": {
    "total": 1500,
    "active": 1200,
    "inactive": 300,
    "verified": 1100,
    "unverified": 400,
    "new_this_week": 45,
    "new_this_month": 180
  },
  "tournaments": {
    "total": 350,
    "active": 12,
    "pending": 8,
    "completed": 330,
    "by_format": {
      "americano": 320,
      "mexicano": 30
    }
  },
  "activity": {
    "matches_today": 45,
    "matches_this_week": 320,
    "avg_players_per_tournament": 12.5,
    "peak_concurrent_tournaments": 15
  },
  "system": {
    "last_backup": "2025-10-01T10:00:00Z",
    "database_size_mb": 450,
    "api_health": "healthy"
  }
}
```

**GET `/api/v1/admin/stats/growth`**
- User signups over time (daily/weekly/monthly)
- Tournament creation trends
- Active user retention rates

**GET `/api/v1/admin/stats/engagement`**
- Most active users (by tournaments played)
- Tournament organizers leaderboard
- Peak usage hours/days

#### 3.2 User Management
**Base Route**: `/api/v1/admin/users`

**GET `/api/v1/admin/users`**
- Query params: `search`, `status` (active/inactive), `verified`, `limit`, `offset`
- Returns: Paginated user list with extended details

**GET `/api/v1/admin/users/{user_id}`**
```json
{
  "user": {...},
  "statistics": {
    "tournaments_created": 15,
    "tournaments_played": 45,
    "matches_played": 280,
    "account_age_days": 120,
    "last_login": "2025-10-01T15:30:00Z"
  },
  "recent_activity": [...]
}
```

**DELETE `/api/v1/admin/users/{user_id}`**
- Soft delete by default (set `is_active=False`)
- Hard delete option with `?permanent=true`
- Cascade options:
  - Delete guest accounts created by user
  - Transfer tournament ownership or delete pending tournaments
  - Preserve historical data in completed tournaments

**PATCH `/api/v1/admin/users/{user_id}`**
- Modify user status: `is_active`, `is_verified`, `is_superuser`
- Update user details if needed

#### 3.3 Tournament Management
**Base Route**: `/api/v1/admin/tournaments`

**GET `/api/v1/admin/tournaments`**
- Extended filters: creator, status, date range, format
- Include problem tournaments (stuck in active state, no players, etc.)

**PATCH `/api/v1/admin/tournaments/{tournament_id}/results`**
```json
{
  "round_id": "uuid",
  "match_id": "uuid",
  "team1_score": 6,
  "team2_score": 4,
  "reason": "Score correction requested by organizer"
}
```

**POST `/api/v1/admin/tournaments/{tournament_id}/recalculate`**
- Recalculate all scores from match results
- Option to recalculate ELO ratings
- Returns updated standings

**PATCH `/api/v1/admin/tournaments/{tournament_id}/status`**
- Force status change (for stuck tournaments)
- Options: `PENDING`, `ACTIVE`, `COMPLETED`, `CANCELLED`

#### 3.4 Audit Logging
**Base Route**: `/api/v1/admin/audit`

**GET `/api/v1/admin/audit/logs`**
- Query params: `admin_id`, `action_type`, `start_date`, `end_date`, `limit`, `offset`
- Returns: Paginated audit trail

**GET `/api/v1/admin/audit/stats`**
- Admin actions summary
- Most common operations
- Recent critical changes

### 4. Frontend Structure

#### 4.1 Admin Dashboard Layout
```
/admin
├── /admin/dashboard        # Overview & Statistics
├── /admin/users            # User Management
├── /admin/tournaments      # Tournament Management
└── /admin/audit            # Audit Logs
```

#### 4.2 Admin Dashboard Page (`/admin/dashboard`)

**Layout Sections:**

1. **Statistics Cards** (Top Row)
   - Total Users (with trend indicator)
   - Active Users (last 7 days)
   - Total Tournaments
   - Active Tournaments

2. **Growth Charts** (Middle Section)
   - User Signups (line chart - last 30 days)
   - Tournament Activity (bar chart - last 30 days)

3. **Quick Actions** (Right Sidebar)
   - Search Users
   - Search Tournaments
   - View Recent Activity
   - System Health

4. **Recent Activity Feed** (Bottom)
   - Latest user registrations
   - New tournaments created
   - Completed tournaments

#### 4.3 User Management Page (`/admin/users`)

**Features:**
- **Search & Filter Bar**
  - Text search (name, email)
  - Filter by status (active/inactive/all)
  - Filter by verification status
  - Sort by: join date, name, tournaments played

- **User Table**
  | Avatar | Name | Email | Status | Verified | Joined | Tournaments | Actions |
  |--------|------|-------|--------|----------|--------|-------------|---------|
  | 👤 | John Doe | john@... | Active | ✓ | Sep 1 | 15 | Edit/Delete |

- **User Detail Modal**
  - Full user information
  - Statistics & activity history
  - Tournament participation
  - Admin actions:
    - Toggle active/inactive
    - Toggle verified
    - Delete account (with confirmation)

#### 4.4 Tournament Management Page (`/admin/tournaments`)

**Features:**
- **Filter & Search**
  - Search by name, creator
  - Filter by status, format, date range
  - Show problem tournaments (toggle)

- **Tournament Table**
  | Name | Creator | Format | Status | Players | Rounds | Created | Actions |
  |------|---------|--------|--------|---------|--------|---------|---------|
  | Summer Cup | Alice | Americano | Active | 12 | 5/8 | Sep 15 | Edit/Manage |

- **Tournament Editor Modal**
  - View all rounds & matches
  - Edit match results with reason
  - Recalculate scores
  - Force status change
  - View change history

#### 4.5 Audit Log Page (`/admin/audit`)

**Features:**
- **Filter Bar**
  - Date range picker
  - Filter by admin user
  - Filter by action type
  - Search by target ID

- **Audit Table**
  | Timestamp | Admin | Action | Target | Details | IP |
  |-----------|-------|--------|--------|---------|-----|
  | Oct 2, 15:30 | Admin User | USER_DELETE | user123 | Deleted inactive user | 192.168.1.1 |

- **Detail View**
  - Full JSON diff (old vs new values)
  - Reason/notes
  - Rollback capability (future)

### 5. Component Architecture

#### 5.1 Backend Services

**AdminStatsService** (`app/services/admin/stats_service.py`)
```python
class AdminStatsService:
    async def get_overview_stats() -> OverviewStats
    async def get_user_growth(period: str) -> GrowthData
    async def get_engagement_metrics() -> EngagementMetrics
    async def get_system_health() -> SystemHealth
```

**AdminUserService** (`app/services/admin/user_service.py`)
```python
class AdminUserService:
    async def get_users_paginated(...) -> PaginatedUsers
    async def get_user_details(user_id) -> UserDetails
    async def delete_user(user_id, permanent: bool) -> None
    async def update_user_status(user_id, updates) -> User
```

**AdminTournamentService** (`app/services/admin/tournament_service.py`)
```python
class AdminTournamentService:
    async def get_tournaments_admin(...) -> PaginatedTournaments
    async def update_match_result(...) -> Match
    async def recalculate_tournament_scores(...) -> Tournament
    async def force_status_change(...) -> Tournament
```

**AuditService** (`app/services/admin/audit_service.py`)
```python
class AuditService:
    async def log_action(admin_id, action_type, target_type, target_id, details, ip)
    async def get_audit_logs(...) -> PaginatedLogs
    async def get_audit_stats() -> AuditStats
```

#### 5.2 Frontend Components

**AdminLayout Component**
```jsx
<AdminLayout>
  <AdminSidebar>
    - Dashboard
    - Users
    - Tournaments
    - Audit Logs
  </AdminSidebar>
  <AdminContent>
    {children}
  </AdminContent>
</AdminLayout>
```

**Reusable Admin Components**
- `StatCard` - Dashboard statistics cards
- `AdminTable` - Sortable, filterable data table
- `AdminModal` - Consistent modal dialogs
- `ConfirmDialog` - Destructive action confirmations
- `AuditTrail` - Display audit log entries
- `DateRangeFilter` - Date filtering component

#### 5.3 Frontend Services

**adminService.js** (`padel-frontend/src/services/adminService.js`)
```javascript
class AdminService {
  // Statistics
  async getOverviewStats()
  async getUserGrowth(period)
  async getEngagementMetrics()

  // Users
  async getUsers(filters)
  async getUserDetails(userId)
  async deleteUser(userId, permanent)
  async updateUserStatus(userId, updates)

  // Tournaments
  async getTournaments(filters)
  async updateMatchResult(tournamentId, matchId, data)
  async recalculateScores(tournamentId)
  async forceStatusChange(tournamentId, status)

  // Audit
  async getAuditLogs(filters)
  async getAuditStats()
}
```

### 6. Security & Validation

#### Backend Validation
- All admin endpoints: `Depends(get_current_superuser)`
- Input validation via Pydantic schemas
- Cascade delete validation (prevent data loss)
- Audit logging for all mutations
- IP address tracking for audit trail

#### Frontend Validation
- Route protection with superuser check
- Confirmation dialogs for destructive actions
- Reason field required for result edits
- Double confirmation for permanent deletes
- Real-time validation feedback

### 7. UI/UX Design Principles

#### Design System
- **Colors**:
  - Admin primary: Deep blue (#1e40af)
  - Success: Green (#10b981)
  - Warning: Orange (#f59e0b)
  - Danger: Red (#ef4444)

- **Layout**:
  - Sidebar navigation (persistent)
  - Breadcrumb trail
  - Page header with actions
  - Data table with pagination

- **Interactions**:
  - Loading states for async operations
  - Success/error toast notifications
  - Optimistic UI updates where safe
  - Confirmation for destructive actions

#### Accessibility
- Keyboard navigation support
- ARIA labels for screen readers
- Color contrast compliance (WCAG AA)
- Focus management in modals

### 8. Data Flow Examples

#### User Deletion Flow
1. Admin clicks "Delete" on user
2. Frontend shows confirmation dialog
3. Admin confirms with reason (optional)
4. Frontend calls DELETE `/api/v1/admin/users/{id}`
5. Backend:
   - Validates admin permission
   - Checks cascade implications
   - Soft deletes user (or hard if specified)
   - Creates audit log entry
6. Frontend:
   - Shows success notification
   - Updates user table
   - Removes user from local state

#### Tournament Result Edit Flow
1. Admin opens tournament editor
2. Selects match to edit
3. Enters new scores + reason
4. Frontend calls PATCH `.../tournaments/{id}/results`
5. Backend:
   - Validates scores (sum to points_per_match)
   - Updates match result
   - Triggers score recalculation
   - Creates audit log
6. Frontend:
   - Updates match display
   - Refreshes standings
   - Shows success notification

### 9. Testing Strategy

#### Backend Tests
**Unit Tests**:
- `test_admin_stats_service.py` - Statistics calculations
- `test_admin_user_service.py` - User management operations
- `test_admin_tournament_service.py` - Tournament operations
- `test_audit_service.py` - Audit logging

**Integration Tests**:
- `test_admin_endpoints.py` - Full API workflow
  - Non-admin access returns 403
  - Admin can retrieve stats
  - User deletion cascades correctly
  - Tournament edits recalculate scores
  - Audit logs created for all actions

#### Frontend Tests
- Route protection (non-admin redirected)
- Component rendering
- User interaction flows
- API error handling
- Confirmation dialog behavior

### 10. Migration Plan

#### Phase 1: Database & Backend
1. Create AuditLog model
2. Generate Alembic migration
3. Implement admin services
4. Create admin API endpoints
5. Add audit logging to all mutations
6. Write backend tests

#### Phase 2: Frontend
1. Create AdminLayout component
2. Build admin dashboard page
3. Build user management page
4. Build tournament management page
5. Build audit log page
6. Add route protection
7. Write frontend tests

#### Phase 3: Testing & Deployment
1. Integration testing
2. Security audit
3. Performance testing (large datasets)
4. Documentation
5. Deploy to staging
6. UAT with admin users
7. Production deployment

### 11. Future Enhancements

**Phase 2 Features**:
- Bulk operations (bulk user status change)
- Advanced analytics (revenue, retention cohorts)
- Audit log rollback capability
- Export data to CSV/Excel
- Email notifications for critical actions
- Admin role hierarchy (super admin, moderator)
- Scheduled reports
- Real-time dashboard updates (WebSocket)

**Metrics & Monitoring**:
- Admin action frequency alerts
- Unusual activity detection
- Performance monitoring dashboard
- Error tracking integration

## Implementation Priority

### High Priority (MVP)
1. ✅ Admin authentication & route protection
2. ✅ Basic statistics dashboard
3. ✅ User management (view, delete)
4. ✅ Audit logging system
5. ✅ Tournament result editing

### Medium Priority
6. Tournament management (status change, recalculate)
7. Advanced filtering & search
8. Audit log viewer
9. Comprehensive test coverage

### Low Priority
10. Growth charts & analytics
11. Engagement metrics
12. System health monitoring
13. Export functionality

## Technical Dependencies

### Backend
- No new dependencies (existing FastAPI, SQLAlchemy, Pydantic)
- Audit logging uses existing database

### Frontend
- No new dependencies (existing React, React Router)
- Charts: Consider recharts or chart.js (if adding visualizations)

## Success Metrics

- **Security**: Zero unauthorized access to admin endpoints
- **Auditability**: 100% of admin actions logged
- **Performance**: Admin dashboard loads < 2s
- **Usability**: Admin tasks completed in < 5 clicks
- **Reliability**: 99.9% uptime for admin features
