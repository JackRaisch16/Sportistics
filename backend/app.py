from flask import Flask
from flask_cors import CORS
from backend.routes.players import players_bp
from backend.routes.trends import trends_bp
from backend.routes.compare import compare_bp



app = Flask(__name__)
CORS(app)


app.register_blueprint(players_bp)
app.register_blueprint(trends_bp)
app.register_blueprint(compare_bp)

if __name__ == "__main__":
    app.run(debug=True)
