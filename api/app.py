from flask import Flask, request, jsonify
import sqlite3
import bcrypt
import os
import json
import logging

app = Flask(__name__)

# Chargement du secret depuis une variable d’environnement (pas hardcodé)
API_KEY = os.environ.get("API_KEY", "default-key")

# Configuration du logging sécurisé
logging.basicConfig(filename='app.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


# --- Authentification sécurisée (prévention SQL Injection) ---
@app.route("/auth", methods=["POST"])
def auth():
    try:
        username = request.json.get("username")
        password = request.json.get("password")

        if not username or not password:
            return jsonify({"error": "Missing credentials"}), 400

        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM users WHERE username=?", (username,))
        row = cursor.fetchone()
        conn.close()

        if row and bcrypt.checkpw(password.encode(), row[0].encode()):
            return jsonify({"status": "authenticated"}), 200
        return jsonify({"status": "denied"}), 401
    except Exception as e:
        logging.error(f"Error in auth: {e}")
        return jsonify({"error": "Server error"}), 500


# --- Suppression de l’exécution de commandes arbitraires ---
@app.route("/exec", methods=["POST"])
def exec_cmd():
    return jsonify({"error": "Command execution disabled for security reasons"}), 403


# --- Désérialisation sécurisée via JSON ---
@app.route("/deserialize", methods=["POST"])
def deserialize():
    try:
        data = json.loads(request.data)
        return jsonify({"object": data}), 200
    except Exception as e:
        logging.warning(f"Invalid JSON data: {e}")
        return jsonify({"error": "Invalid data"}), 400


# --- Chiffrement fort (bcrypt) ---
@app.route("/encrypt", methods=["POST"])
def encrypt():
    text = request.json.get("text", "")
    if not text:
        return jsonify({"error": "Text is required"}), 400
    hashed = bcrypt.hashpw(text.encode(), bcrypt.gensalt())
    return jsonify({"hash": hashed.decode()}), 200


# --- Lecture sécurisée de fichier (anti Path Traversal) ---
@app.route("/file", methods=["POST"])
def read_file():
    try:
        filename = request.json.get("filename")
        if not filename:
            return jsonify({"error": "Filename is required"}), 400

        base_path = "/app/files/"
        os.makedirs(base_path, exist_ok=True)
        safe_path = os.path.join(base_path, os.path.basename(filename))

        if not os.path.exists(safe_path):
            return jsonify({"error": "File not found"}), 404

        with open(safe_path, "r") as f:
            content = f.read()
        return jsonify({"content": content}), 200
    except Exception as e:
        logging.error(f"File read error: {e}")
        return jsonify({"error": "Unable to read file"}), 500


# --- Debug endpoint désactivé ---
@app.route("/debug", methods=["GET"])
def debug():
    return jsonify({"error": "Access forbidden"}), 403


# --- Logging sécurisé ---
@app.route("/log", methods=["POST"])
def log_data():
    try:
        data = request.json
        logging.info("User input safely logged: %s", json.dumps(data))
        return jsonify({"status": "logged"}), 200
    except Exception as e:
        logging.error(f"Logging error: {e}")
        return jsonify({"error": "Invalid log input"}), 400


# --- Exécution principale sécurisée ---
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)

