import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from pybaseball import batting_stats
import mysql.connector
from backend.config import DB_CONFIG

def get_batting_data(year=2024):
    df = batting_stats(year)
    df = df.fillna(0)  # Replace missing values with 0
    return df

def insert_player_stats(df):
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()

    season_id = 2   # Corresponds to 2024
    league_id = 1   # Assuming MLB

    for _, row in df.iterrows():
        name = row["Name"].strip()
        team_name = row["Team"]

        # Basic stats
        stats = {
            "games_played": int(row["G"]),
            "plate_appearances": int(row["PA"]),
            "at_bats": int(row["AB"]),
            "runs": int(row["R"]),
            "hits": int(row["H"]),
            "doubles": int(row["2B"]),
            "triples": int(row["3B"]),
            "home_runs": int(row["HR"]),
            "runs_batted_in": int(row["RBI"]),
            "stolen_bases": int(row["SB"]),
            "caught_stealing": int(row["CS"]),
            "walks": int(row["BB"]),
            "strikeouts": int(row["SO"]),
            "hit_by_pitch": int(row["HBP"]),
            "sacrifice_flies": int(row["SF"]),
            "batting_avg": float(row["AVG"]),
            "on_base_pct": float(row["OBP"]),
            "slugging_pct": float(row["SLG"]),
            "ops": float(row["OPS"]),
        }

        # Insert team if not exists
        cursor.execute("SELECT id FROM Teams WHERE name = %s", (team_name,))
        team_result = cursor.fetchone()
        if team_result:
            team_id = team_result[0]
        else:
            cursor.execute("INSERT INTO Teams (name, league_id) VALUES (%s, %s)", (team_name, league_id))
            team_id = cursor.lastrowid

        # Insert player if not exists
        cursor.execute("SELECT id FROM Players WHERE name = %s", (name,))
        player_result = cursor.fetchone()
        if player_result:
            player_id = player_result[0]
        else:
            cursor.execute(
                "INSERT INTO Players (name, debut_year, team_id, position) VALUES (%s, %s, %s, %s)",
                (name, 2024, team_id, "Unknown"),
            )
            player_id = cursor.lastrowid

        # Skip if stats already exist for player + season
        cursor.execute("""
            SELECT id FROM PlayerStats WHERE player_id = %s AND season_id = %s
        """, (player_id, season_id))
        if cursor.fetchone():
            continue  # already exists

        # Insert stats
        cursor.execute("""
            INSERT INTO PlayerStats (
                player_id, season_id, league_id,
                games_played, plate_appearances, at_bats, runs, hits,
                doubles, triples, home_runs, runs_batted_in,
                stolen_bases, caught_stealing,
                walks, strikeouts, hit_by_pitch, sacrifice_flies,
                batting_avg, on_base_pct, slugging_pct, ops,
                war, woba, wrc_plus, babip
            ) VALUES (
                %s, %s, %s,
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s,
                %s, %s, %s, %s,
                %s, %s, %s, %s,
                NULL, NULL, NULL, NULL
            )
        """, (
            player_id, season_id, league_id,
            stats["games_played"], stats["plate_appearances"], stats["at_bats"], stats["runs"], stats["hits"],
            stats["doubles"], stats["triples"], stats["home_runs"], stats["runs_batted_in"],
            stats["stolen_bases"], stats["caught_stealing"],
            stats["walks"], stats["strikeouts"], stats["hit_by_pitch"], stats["sacrifice_flies"],
            stats["batting_avg"], stats["on_base_pct"], stats["slugging_pct"], stats["ops"],
        ))

    conn.commit()
    cursor.close()
    conn.close()
    print("2024 stats successfully imported.")

if __name__ == "__main__":
    data = get_batting_data(2024)
    insert_player_stats(data)
