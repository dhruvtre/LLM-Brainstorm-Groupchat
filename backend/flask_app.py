from flask import Flask, request, jsonify
from flask_cors import CORS
from main_logic import *

app = Flask(__name__)
CORS(app)

@app.route('/api/send-message', methods=['POST'])
def send_message():
    agent_transcripts = request.json.get('agentTranscripts', {})
    user_input = request.json.get('message')

    # Ensure we have all required transcripts
    if not all(key in agent_transcripts for key in ["white_hat", "black_hat", "green_hat"]):
        return jsonify({"error": "Missing required agent transcripts"}), 400
    
    responses = asyncio.run(process_agent_responses(agent_transcripts))
    
    return jsonify({
        "responses": responses
    })

if __name__ == '__main__':
    app.run(debug=True)
