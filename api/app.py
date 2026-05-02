from flask import Flask, jsonify, request
import os
from pymongo import MongoClient
from bson import ObjectId

app = Flask(__name__)

MONGO_HOSTNAME = os.environ.get('MONGO_HOSTNAME', 'mongo')
MONGO_PORT = int(os.environ.get('MONGO_PORT', 27017))
MONGO_DB = os.environ.get('MONGO_DB', 'sharkinfo')

def get_db():
    client = MongoClient(f'mongodb://{MONGO_HOSTNAME}:{MONGO_PORT}/')
    return client[MONGO_DB]

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "service": "api"}), 200

@app.route('/api/games', methods=['GET'])
def get_games():
    """Return all games from MongoDB as JSON."""
    try:
        db = get_db()
        games = list(db.games.find({}, {'_id': 0}))
        return jsonify({"games": games, "count": len(games)}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/games/stats', methods=['GET'])
def get_stats():
    """Return genre breakdown statistics."""
    try:
        db = get_db()
        pipeline = [
            {"$group": {"_id": "$genre", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        stats = list(db.games.aggregate(pipeline))
        return jsonify({"genre_stats": stats}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/echo', methods=['POST'])
def echo():
    data = request.get_json(force=True)
    return jsonify({"echo": data}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
