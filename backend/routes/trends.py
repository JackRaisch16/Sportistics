from flask import Blueprint

trends_bp = Blueprint('trends', __name__)

@trends_bp.route("/trends")
def get_trends():
    return {"message": "Trends route works!"}
