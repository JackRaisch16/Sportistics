from flask import Blueprint, request, jsonify
from backend.database.db import get_db_connection

compare_bp = Blueprint('compare', __name__)

@compare_bp.route("/compare", methods=["GET"])
def compare_players():
    player_ids = request.args.get("players")
    
    if not player_ids:
        return jsonify({"error": "Please provide player IDs using ?players=1,2,3"}), 400

    try:
        id_list = tuple(map(int, player_ids.split(",")))
    except ValueError:
        return jsonify({"error": "Player IDs must be integers"}), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = f"""
        SELECT 
            p.id, p.name, ps.season_id,
            ps.games_played, ps.plate_appearances, ps.at_bats, ps.runs, ps.hits,
            ps.doubles, ps.triples, ps.home_runs, ps.runs_batted_in,
            ps.stolen_bases, ps.caught_stealing,
            ps.walks, ps.strikeouts, ps.hit_by_pitch, ps.sacrifice_flies,
            ps.batting_avg, ps.on_base_pct, ps.slugging_pct, ps.ops,
            ps.war, ps.woba, ps.wrc_plus, ps.babip
        FROM Players p
        JOIN PlayerStats ps ON p.id = ps.player_id
        WHERE p.id IN {id_list}
    """

    cursor.execute(query)
    results = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify(results)
