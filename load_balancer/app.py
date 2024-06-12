import hashlib
import random
import threading
import time
import docker
from flask import Flask, request, jsonify
import requests
import json

# Constants from the assignment
NUM_SERVERS = 3
NUM_SLOTS = 512
NUM_VIRTUAL_SERVERS = 9
SERVER_HASH_FUNCTION = lambda i: i + 2*i**2 + 17
VIRTUAL_SERVER_HASH_FUNCTION = lambda i, j: i + j + 2*j**2 + 25

# Consistent Hash Map implementation
class ConsistentHashMap:
    def __init__(self):
        self.hash_ring = [None] * NUM_SLOTS
        self.servers = {}

    def add_server(self, server_id, num_virtual_servers):
        self.servers[server_id] = []
        for i in range(num_virtual_servers):
            slot = self.hash_function(server_id, i) % NUM_SLOTS
            while self.hash_ring[slot] is not None:
                slot = (slot + 1) % NUM_SLOTS
            self.hash_ring[slot] = server_id
            self.servers[server_id].append(slot)

    def remove_server(self, server_id):
        for slot in self.servers[server_id]:
            self.hash_ring[slot] = None
        del self.servers[server_id]

    def get_server(self, request_id):
        slot = self.hash_function(request_id) % NUM_SLOTS
        while self.hash_ring[slot] is None:
            slot = (slot + 1) % NUM_SLOTS
        return self.hash_ring[slot]

    def hash_function(self, *args):
        key = ''.join(str(arg) for arg in args).encode()
        return int(hashlib.sha256(key).hexdigest(), 16)

# Load Balancer implementation
app = Flask(__name__)
client = docker.from_env()
api_client = docker.APIClient(base_url='unix://var/run/docker.sock')
ports = []

@app.route('/rep', methods=['GET'])
def get_replicas():
    replicas = list(consistent_hash_map.servers.keys())
    return jsonify({"message": {"N": len(replicas), "replicas": replicas}, "status": "successful"})

@app.route('/add', methods=['POST'])
def add_replicas():
    data = request.get_json()
    new_replicas = data.get('hostnames', [])
    num_new_replicas = data.get('n', 0)
    if len(new_replicas) > num_new_replicas:
        return jsonify({"message": "<Error> Length of hostname list is more than newly added instances", "status": "failure"}), 400
    for i in range(num_new_replicas):
        if i < len(new_replicas):
            replica_id = new_replicas[i]
        else:
            replica_id = f"Server{len(consistent_hash_map.servers)+i+1}"
        consistent_hash_map.add_server(replica_id, NUM_VIRTUAL_SERVERS)
        spawn_replica(replica_id)
    return jsonify({"message": {"N": len(consistent_hash_map.servers), "replicas": list(consistent_hash_map.servers.keys())}, "status": "successful"})

@app.route('/rm', methods=['DELETE'])
def remove_replicas():
    data = request.get_json()
    replicas_to_remove = data.get('hostnames', [])
    num_replicas_to_remove = data.get('n', 0)
    if len(replicas_to_remove) > num_replicas_to_remove:
        return jsonify({"message": "<Error> Length of hostname list is more than removable instances", "status": "failure"}), 400
    for i in range(num_replicas_to_remove):
        if i < len(replicas_to_remove):
            replica_id = replicas_to_remove[i]
        else:
            replica_id = random.choice(list(consistent_hash_map.servers.keys()))
        consistent_hash_map.remove_server(replica_id)
        remove_replica(replica_id)
    return jsonify({"message": {"N": len(consistent_hash_map.servers), "replicas": list(consistent_hash_map.servers.keys())}, "status": "successful"})

@app.route('/<path:path>', methods=['GET'])
def route_request(path):
    request_id = f"{request.remote_addr}:{request.environ['REMOTE_PORT']}"
    server_id = consistent_hash_map.get_server(request_id)
    
    container = client.containers.get(server_id)
    ports = [container.ports[i] for i in container.ports if container.ports[i] != None][0]
    port = [int(i['HostPort']) for i in ports][0]
    try:
        resp = requests.get(f"http://127.0.0.1:{port}/{path}", headers=request.headers)
        return resp.content, resp.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({
            "message": f"<Error> '{path}' endpoint does not exist in server replicas",
            "status": "failure",
            "error": str(e)
        }), 400

def spawn_replica(replica_id):
  global ports
  def create_port() -> int:
    port = random.randint(5001, 5100)
    try:
        _ = ports.index(port)
        port = create_port()
    except:
        ports.append(port)
    return port
  
  port = create_port()
  container = client.containers.run("load_balancer-server", name=replica_id, ports={port: port}, detach=True, network='bridge', environment={"SERVER_ID": str(replica_id), "PORT":port})

def remove_replica(replica_id):
    container = client.containers.get(replica_id)
    container.stop()
    container.remove(force=True)

def spawn_servers():
  time.sleep(10)
  hostnames = [f"server_{n+1}" for n in range(NUM_SERVERS)]
  payload = {"n": NUM_SERVERS, "hostnames": hostnames}
  resp = requests.post("http://127.0.0.1:5000/add", json=payload)
  print(resp)
  
def get_active_servers():
    resp = requests.get("http://127.0.0.1:5000/rep")
    data = json.loads(resp.content)
    replicas = data['message']['replicas']
    return replicas
  
# def check_container_status():
#     global client
#     running_containers = client.containers.list()
#     running_container_ids = [container.id for container in running_containers]
#     active_servers = get_active_servers()
#     if len(running_container_ids) < NUM_SERVERS:
#         for server in active_servers:
#             if running_container_ids.__contains__(server) == False:
#                 print(f"Server down: {server} servers running. Spawning new container.")
#                 spawn_replica(server)

# def monitor_servers():
#     time.sleep(20)
#     while True:
#         check_container_status()
#         time.sleep(10)  # Monitor every 10 seconds
        
def check_server_health(server_id):
    try:
        container = client.containers.get(server_id)
        ports = [container.ports[i] for i in container.ports if container.ports[i] != None][0]
        port = [int(i['HostPort']) for i in ports][0]
        resp = requests.get(f"http://127.0.0.1:{port}/heartbeat", timeout=5)
        if resp.status_code == 200:
            return True
        else:
            return False
    except:
        return False
        
def monitor_servers():
    time.sleep(30)
    while True:
        for server in get_active_servers():
            if not check_server_health(server):
                print(f"Server {server} is down. Spawning a new container...")
                payload = {"n": 1, "hostnames": [f"{server}"]}
                resp = requests.post("http://127.0.0.1:5000/add", json=payload)
        time.sleep(10)  # Check server health every 10 seconds

if __name__ == '__main__':
  server_start_thread = threading.Thread(target=spawn_servers)
  server_start_thread.start()
  
  monitor_server_thread = threading.Thread(target=monitor_servers)
  monitor_server_thread.start()  
  
  consistent_hash_map = ConsistentHashMap()
  app.run(host='0.0.0.0', port=5000)
