from flask import Flask, jsonify
import threading
import os

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'discord-bot',
        'message': 'Bot is running'
    }), 200

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'message': 'Discord Bot Health Check Server',
        'endpoints': {
            '/health': 'Health check endpoint for monitoring'
        }
    }), 200

def run_server():
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

if __name__ == '__main__':
    run_server()
