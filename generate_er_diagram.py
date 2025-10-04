#!/usr/bin/env python3
"""Generate PNG ER diagram from Mermaid definition"""

import subprocess
import sys
import os

# Mermaid diagram definition
mermaid_diagram = """
graph TB
    subgraph "Core Entities"
        Users["<b>users</b><br/>id (PK)<br/>email (UK)<br/>full_name<br/>picture<br/>hashed_password<br/>is_active<br/>is_superuser<br/>is_verified"]
        Tournaments["<b>tournaments</b><br/>id (PK)<br/>name<br/>description<br/>location<br/>start_date<br/>entry_fee<br/>max_players<br/>system (ENUM)<br/>points_per_match<br/>courts<br/>created_at<br/>created_by (FK→users)<br/>status<br/>current_round<br/>average_player_rating"]
    end

    subgraph "Match Management"
        Rounds["<b>rounds</b><br/>id (PK)<br/>tournament_id (FK)<br/>round_number<br/>team1_player1_id (FK→users)<br/>team1_player2_id (FK→users)<br/>team2_player1_id (FK→users)<br/>team2_player2_id (FK→users)<br/>team1_score<br/>team2_score<br/>is_completed"]
    end

    subgraph "Rating System"
        PlayerRatings["<b>player_ratings</b><br/>id (PK)<br/>user_id (FK,UK→users)<br/>current_rating<br/>peak_rating<br/>lowest_rating<br/>matches_played<br/>matches_won<br/>total_points_scored<br/>total_points_possible<br/>tournaments_played<br/>first_place_finishes<br/>second_place_finishes<br/>third_place_finishes<br/>created_at<br/>updated_at"]
        RatingHistory["<b>rating_history</b><br/>id (PK)<br/>player_rating_id (FK)<br/>tournament_id (FK)<br/>match_id (FK→rounds)<br/>old_rating<br/>new_rating<br/>rating_change<br/>opponent_ratings<br/>match_result<br/>timestamp"]
    end

    subgraph "Tournament Results"
        TournamentResults["<b>tournament_results</b><br/>id (PK)<br/>tournament_id (FK)<br/>player_id (FK→users)<br/>final_position<br/>total_score<br/>points_difference<br/>matches_played<br/>matches_won<br/>matches_lost<br/>matches_tied<br/>created_at<br/>UK: (tournament_id, player_id)"]
    end

    subgraph "Join Tables"
        TournamentPlayer["<b>tournament_player</b><br/>tournament_id (PK,FK)<br/>player_id (PK,FK→users)"]
    end

    %% Relationships
    Users -.->|"1:1"| PlayerRatings
    Users -->|"1:N creates"| Tournaments
    Users <-->|"M:N via"| TournamentPlayer
    Tournaments <-->|"M:N via"| TournamentPlayer
    Users -->|"1:N plays as"| Rounds
    Users -->|"1:N has"| TournamentResults

    Tournaments -->|"1:N has"| Rounds
    Tournaments -->|"1:N has"| TournamentResults
    Tournaments -->|"1:N affects"| RatingHistory

    Rounds -->|"N:1 belongs to"| Tournaments
    Rounds -->|"1:N creates"| RatingHistory

    PlayerRatings -->|"1:N tracks"| RatingHistory

    style Users fill:#e1f5fe
    style Tournaments fill:#fff3e0
    style Rounds fill:#f3e5f5
    style PlayerRatings fill:#e8f5e9
    style RatingHistory fill:#e8f5e9
    style TournamentResults fill:#fff3e0
    style TournamentPlayer fill:#fce4ec
"""

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        # Check for Node.js
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        if result.returncode != 0:
            print("Error: Node.js is not installed. Please install Node.js first.")
            print("Visit: https://nodejs.org/")
            return False
    except FileNotFoundError:
        print("Error: Node.js is not installed. Please install Node.js first.")
        print("Visit: https://nodejs.org/")
        return False

    # Check for mermaid-cli
    try:
        result = subprocess.run(['npx', 'mmdc', '--version'], capture_output=True, text=True)
        if result.returncode != 0 or 'mermaid' not in result.stdout.lower():
            print("Installing mermaid-cli...")
            subprocess.run(['npm', 'install', '-g', '@mermaid-js/mermaid-cli'], check=True)
    except FileNotFoundError:
        print("Installing mermaid-cli...")
        subprocess.run(['npm', 'install', '-g', '@mermaid-js/mermaid-cli'], check=True)

    return True

def generate_diagram():
    """Generate the ER diagram PNG"""
    # Write Mermaid file
    mermaid_file = "er_diagram.mmd"
    output_file = "database_er_diagram.png"

    with open(mermaid_file, 'w') as f:
        f.write(mermaid_diagram)

    print(f"Generating {output_file}...")

    # Generate PNG using mermaid-cli
    try:
        result = subprocess.run(
            ['npx', 'mmdc', '-i', mermaid_file, '-o', output_file, '--width', '2400', '--height', '1800', '--backgroundColor', 'white'],
            capture_output=True,
            text=True,
            check=True
        )
        print(f"✅ Successfully generated {output_file}")

        # Clean up temp file
        os.remove(mermaid_file)

    except subprocess.CalledProcessError as e:
        print(f"Error generating diagram: {e}")
        print(f"stdout: {e.stdout}")
        print(f"stderr: {e.stderr}")
        return False

    return True

def main():
    if not check_dependencies():
        sys.exit(1)

    if generate_diagram():
        print("\n📊 ER Diagram has been generated successfully!")
        print("Files created:")
        print("  - database_er_diagram.md (Mermaid format)")
        print("  - database_er_diagram.png (PNG image)")
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()