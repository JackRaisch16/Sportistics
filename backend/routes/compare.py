from flask import Blueprint, request, jsonify
from backend.database.db import get_db_connection

compare_bp = Blueprint('compare', __name__)

@compare_bp.route("/compare", methods=["GET"])
def compare_players():
    names = request.args.get("names")
    
    if not names:
        return jsonify({"error": "Please provide player names using ?names=Player1,Player2"}), 400

    try:
        name_list = tuple(map(str.strip, names.split(",")))
    except Exception:
        return jsonify({"error": "Invalid format for player names"}), 400

    if len(name_list) == 1:
        # Single element tuples in Python need a trailing comma
        name_list = (name_list[0],)

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Dynamically build placeholders for IN clause
    placeholders = ','.join(['%s'] * len(name_list))

    query = f"""
        SELECT 
            p.id, p.name, ps.season_id,
            ps.games_played, ps.plate_appearances, ps.at_bats, ps.runs, ps.hits,
            ps.doubles, ps.triples, ps.home_runs, ps.runs_batted_in,
            ps.stolen_bases, ps.caught_stealing,
            ps.walks, ps.strikeouts, ps.hit_by_pitch, ps.sacrifice_flies,
            ps.batting_avg, ps.on_base_pct, ps.slugging_pct, ps.ops,
            ps.war, ps.woba, ps.wrc_plus
        FROM Players p
        JOIN PlayerStats ps ON p.id = ps.player_id
        WHERE p.name IN ({placeholders}) AND ps.season_id = 2
    """

    try:
        cursor.execute(query, name_list)
        results = cursor.fetchall()
    except Exception as e:
        cursor.close()
        conn.close()
        return jsonify({"error": str(e)}), 500

    cursor.close()
    conn.close()

    return jsonify(results)
