from flask import Flask, jsonify
import os

app = Flask(__name__)

@app.route('/')
def index():
    return jsonify({
        "message": "Flask app is running!",
        "url": "http://localhost:8080/",
        "storage_info": {
            "deploy_dir": os.path.exists("/app/deploy"),
            "sql_dir": os.path.exists("/app/sql")
        }
    })

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
