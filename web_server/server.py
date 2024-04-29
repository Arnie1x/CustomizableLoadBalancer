import os
from flask import Flask
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

@app.route('/home', methods=['GET'])
def home():
    server_id = os.environ.get('SERVER_ID', 'Unknown')
    message = f"Hello from Server: {server_id}"
    return {"message": message, "status": "successful"}, 200

@app.route('/heartbeat', methods=['GET'])
def heartbeat():
    return '', 200

if __name__ == '__main__':
    app.run(host='127.0.0.3', port=5000)