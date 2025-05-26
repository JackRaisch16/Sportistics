import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from pybaseball import batting_stats
import mysql.connector
from backend.config import DB_CONFIG

def get_batting_data(year=2023):
    df = batting_stats(year)
    df = df.fillna(0)  # Handle missing values
    return df

def insert_player_stats(df):
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()

    # For now, assume league_id = 1 (MLB), season_id = 1 (2023)
    for _, row in df.iterrows():
        name = row['Name']
        team = row['Team']
        games_played = int(row['G'])
        at_bats = int(row['AB'])
        home_runs = int(row['HR'])
        batting_avg = round(float(row['AVG']), 3)
        war = None  # pybaseball doesn’t include WAR in this pull

        # Check if player exists
        cursor.execute("SELECT id FROM Players WHERE name = %s", (name,))
        result = cursor.fetchone()

        if result:
            player_id = result[0]
        else:
            # Add player (assign to dummy team_id = 1 for now)
            cursor.execute("INSERT INTO Players (name, debut_year, team_id, position) VALUES (%s, %s, %s, %s)", 
                           (name, 2023, 1, 'Unknown'))
            player_id = cursor.lastrowid

        # Insert simplified stats
        cursor.execute("""
            INSERT INTO PlayerStats (
                player_id, season_id, league_id,
                games_played, at_bats, home_runs, batting_avg, war
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (player_id, 1, 1, games_played, at_bats, home_runs, batting_avg, war))

    conn.commit()
    cursor.close()
    conn.close()

if __name__ == "__main__":
    data = get_batting_data(2023)
    insert_player_stats(data)
    print("Stats successfully imported.")
