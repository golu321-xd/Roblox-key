from flask import Flask, request, jsonify
import json
from datetime import datetime, timedelta
import random

app = Flask(__name__)
DB_FILE = 'database.json'

# Load database
def load_db():
    try:
        with open(DB_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

# Save database
def save_db(data):
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=4)

# Generate key like SUBHU-XXXXX
def generate_key():
    return f"SUBHU-{random.randint(10000,99999)}"

# API: Get key for a username
@app.route('/getkey', methods=['POST'])
def get_key():
    data = request.json
    username = data.get('username')
    if not username:
        return jsonify({"error": "No username provided"}), 400

    db = load_db()
    
    # Check if username already has a key
    if username in db:
        key_data = db[username]
        # check expiry
        if datetime.fromisoformat(key_data['expiry']) > datetime.now():
            return jsonify({"key": key_data['key'], "expiry": key_data['expiry']})

    # Generate new key
    key = generate_key()
    expiry = (datetime.now() + timedelta(hours=24)).isoformat()
    db[username] = {"key": key, "expiry": expiry}
    save_db(db)
    return jsonify({"key": key, "expiry": expiry})

# API: Verify key for username
@app.route('/verify', methods=['POST'])
def verify_key():
    data = request.json
    username = data.get('username')
    key = data.get('key')

    if not username or not key:
        return jsonify({"status": "error", "message": "Missing username or key"}), 400

    db = load_db()
    if username not in db:
        return jsonify({"status": "denied"})
    key_data = db[username]
    if key_data['key'] != key:
        return jsonify({"status": "denied"})
    if datetime.fromisoformat(key_data['expiry']) < datetime.now():
        return jsonify({"status": "denied"})
    return jsonify({"status": "granted"})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
