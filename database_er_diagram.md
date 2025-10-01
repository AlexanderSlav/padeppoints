# PadelPoints Database ER Diagram

## Mermaid ER Diagram

```mermaid
erDiagram
    users ||--o{ tournament_player : participates_in
    users ||--o{ tournaments : creates
    users ||--|| player_ratings : has_rating
    users ||--o{ rounds : plays_team1_p1
    users ||--o{ rounds : plays_team1_p2
    users ||--o{ rounds : plays_team2_p1
    users ||--o{ rounds : plays_team2_p2
    users ||--o{ tournament_results : has_results

    tournaments ||--o{ tournament_player : has_players
    tournaments ||--o{ rounds : has_rounds
    tournaments ||--o{ tournament_results : has_results
    tournaments ||--o{ rating_history : affects_ratings

    rounds }o--|| tournaments : belongs_to
    rounds ||--o{ rating_history : creates_history

    player_ratings ||--o{ rating_history : tracks_changes

    users {
        string id
        string email
        string full_name
        string picture
        string hashed_password
        boolean is_active
        boolean is_superuser
        boolean is_verified
    }

    tournaments {
        string id
        string name
        string description
        string location
        date start_date
        float entry_fee
        int max_players
        string system
        int points_per_match
        int courts
        datetime created_at
        string created_by
        string status
        int current_round
        float average_player_rating
    }

    tournament_player {
        string tournament_id
        string player_id
    }

    rounds {
        string id
        string tournament_id
        int round_number
        string team1_player1_id
        string team1_player2_id
        string team2_player1_id
        string team2_player2_id
        int team1_score
        int team2_score
        boolean is_completed
    }

    player_ratings {
        string id
        string user_id
        float current_rating
        float peak_rating
        float lowest_rating
        int matches_played
        int matches_won
        int total_points_scored
        int total_points_possible
        int tournaments_played
        int first_place_finishes
        int second_place_finishes
        int third_place_finishes
        datetime created_at
        datetime updated_at
    }

    rating_history {
        string id
        string player_rating_id
        string tournament_id
        string match_id
        float old_rating
        float new_rating
        float rating_change
        string opponent_ratings
        string match_result
        datetime timestamp
    }

    tournament_results {
        string id
        string tournament_id
        string player_id
        int final_position
        int total_score
        int points_difference
        int matches_played
        int matches_won
        int matches_lost
        int matches_tied
        datetime created_at
    }

```

## Database Relationships Summary

### Core Entities

1. **users** - Central user entity
   - Has one player_rating (1:1)
   - Can create many tournaments (1:N)
   - Can participate in many tournaments (M:N via tournament_player)
   - Can play in many rounds (1:N, as 4 different player positions)
   - Has many tournament_results (1:N)

2. **tournaments** - Tournament management
   - Created by one user (N:1)
   - Has many players (M:N via tournament_player)
   - Has many rounds (1:N)
   - Has many tournament_results (1:N)
   - Creates rating_history entries (1:N)

3. **rounds** - Match/game tracking
   - Belongs to one tournament (N:1)
   - Has 4 player relationships (N:1 each)
   - Creates rating_history entries (1:N)

4. **player_ratings** - ELO rating system
   - Belongs to one user (1:1)
   - Has many rating_history entries (1:N)

5. **rating_history** - Rating change tracking
   - References player_rating (N:1)
   - References tournament (N:1)
   - References round/match (N:1)

6. **tournament_results** - Final tournament standings
   - References tournament (N:1)
   - References user/player (N:1)
   - Unique constraint on (tournament_id, player_id)

7. **tournament_player** - Join table for M:N relationship
   - Links users and tournaments

### Key Relationships

- **Many-to-Many**: Users ↔ Tournaments (via tournament_player)
- **One-to-One**: Users → PlayerRatings
- **One-to-Many**:
  - Tournaments → Rounds
  - Tournaments → TournamentResults
  - Users → CreatedTournaments
  - PlayerRatings → RatingHistory
- **Complex**: Rounds have 4 separate foreign keys to Users (for team compositions)

### Business Rules Enforced by Schema

1. Each user can have only one player rating
2. Each tournament-player result combination is unique
3. Rounds track exactly 4 players (2 teams of 2)
4. Rating history tracks changes per match and tournament
5. Tournament status follows enum values (pending, active, completed)
6. Tournament system follows enum values (AMERICANO, MEXICANO)