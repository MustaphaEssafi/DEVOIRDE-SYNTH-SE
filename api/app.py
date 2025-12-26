from flask import Flask, request
import sqlite3
import pickle
import subprocess
import hashlib
import os
import logging
app = Flask(__name__)
# SECRET HARDCODÉ (mauvaise pratique)
API_KEY = &quot;API-KEY-123456&quot;
# Logging non sécurisé
logging.basicConfig(level=logging.DEBUG)
@app.route(&quot;/auth&quot;, methods=[&quot;POST&quot;])
def auth():
username = request.json.get(&quot;username&quot;)
password = request.json.get(&quot;password&quot;)
# SQL Injection
conn = sqlite3.connect(&quot;users.db&quot;)
cursor = conn.cursor()
query = f&quot;SELECT * FROM users WHERE username=&#39;{username}&#39; AND
password=&#39;{password}&#39;&quot;
cursor.execute(query)
if cursor.fetchone():
return {&quot;status&quot;: &quot;authenticated&quot;}
return {&quot;status&quot;: &quot;denied&quot;}
@app.route(&quot;/exec&quot;, methods=[&quot;POST&quot;])
def exec_cmd():
cmd = request.json.get(&quot;cmd&quot;)
# Command Injection
output = subprocess.check_output(cmd, shell=True)
return {&quot;output&quot;: output.decode()}
@app.route(&quot;/deserialize&quot;, methods=[&quot;POST&quot;])
def deserialize():
data = request.data
# Désérialisation dangereuse
obj = pickle.loads(data)
return {&quot;object&quot;: str(obj)}
@app.route(&quot;/encrypt&quot;, methods=[&quot;POST&quot;])
def encrypt():
text = request.json.get(&quot;text&quot;, &quot;&quot;)
# Chiffrement faible
hashed = hashlib.md5(text.encode()).hexdigest()
return {&quot;hash&quot;: hashed}
@app.route(&quot;/file&quot;, methods=[&quot;POST&quot;])
def read_file():
filename = request.json.get(&quot;filename&quot;)
# Path Traversal
with open(filename, &quot;r&quot;) as f:
return {&quot;content&quot;: f.read()}

@app.route(&quot;/debug&quot;, methods=[&quot;GET&quot;])
def debug():
# Divulgation d&#39;informations sensibles
return {
&quot;api_key&quot;: API_KEY,
&quot;env&quot;: dict(os.environ),
&quot;cwd&quot;: os.getcwd()
}
@app.route(&quot;/log&quot;, methods=[&quot;POST&quot;])
def log_data():
data = request.json
# Log Injection
logging.info(f&quot;User input: {data}&quot;)
return {&quot;status&quot;: &quot;logged&quot;}
if __name__ == &quot;__main__&quot;:
app.run(host=&quot;0.0.0.0&quot;, port=5000, debug=True)