from flask import Flask, jsonify, request
import os

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "service": "api"}), 200

@app.route('/api/games', methods=['GET'])
def get_games():
    """Proxy endpoint — demonstrates inter-service REST communication."""
    return jsonify({"message": "API service running", "games": []}), 200

@app.route('/api/echo', methods=['POST'])
def echo():
    data = request.get_json(force=True)
    return jsonify({"echo": data}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

