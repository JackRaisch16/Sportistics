from flask import Blueprint, jsonify
from backend.database.db import get_db_connection

players_bp = Blueprint('players', __name__)

@players_bp.route("/players", methods=["GET"])
def get_players():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT id, name, position FROM Players LIMIT 10;")
    players = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify(players)
