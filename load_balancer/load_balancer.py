import os
import random
import string
import docker
from flask import Flask, request, jsonify
import requests
# from consistent_hashing.consistent_hash import ConsistentHashMap

class ConsistentHashMap:
    def __init__(self, num_servers=3, num_slots=512, num_virtual_servers=9):
        self.num_servers = num_servers
        self.num_slots = num_slots
        self.num_virtual_servers = num_virtual_servers
        self.hash_map = [[] for _ in range(num_slots)]
        self.servers = {}
        self.virtual_servers = {}

    def add_server(self, server_id):
        for i in range(self.num_virtual_servers):
            virtual_server_id = (server_id, i)
            slot = self._hash(server_id, i)
            self.hash_map[slot].append(virtual_server_id)
            self.virtual_servers[virtual_server_id] = server_id
        self.servers[server_id] = True

    def remove_server(self, server_id):
        for i in range(self.num_virtual_servers):
            virtual_server_id = (server_id, i)
            slot = self._hash(server_id, i)
            self.hash_map[slot].remove(virtual_server_id)
            del self.virtual_servers[virtual_server_id]
        del self.servers[server_id]

    def get_server(self, request_id):
        slot = self._hash(request_id)
        
        virtual_servers = None
        for x in self.hash_map[slot:]:
            if len(x) != 0:
                virtual_servers = x
                break
        if virtual_servers is None:
            for x in self.hash_map:
                if len(x) != 0:
                    virtual_servers = x
                    break
        # virtual_servers = next((x for x in self.hash_map[slot:].copy() if x != []), (x for x in self.hash_map.copy() if x != []))
        # print(self.hash_map)
        if not virtual_servers:
            return None
        return self.virtual_servers[virtual_servers[0]]

    def _hash(self, value, seed=0):
        hash_fn = lambda x, y: (x ** 2 + 2 * x + seed * y) % self.num_slots
        if isinstance(value, int):
            return hash_fn(value, 17)
        elif isinstance(value, tuple):
            server_id, virtual_id = value
            return hash_fn(server_id, virtual_id + 25)
  

app = Flask(__name__)
client = docker.from_env()
load_balancer = ConsistentHashMap(num_servers=3, num_slots=512, num_virtual_servers=9)
api_client = docker.APIClient(base_url='unix://var/run/docker.sock')

ip_addresses = []

@app.route('/rep', methods=['GET'])
def get_replicas():
    replicas = [f"server_{server_id}" for server_id in load_balancer.servers.keys()]
    return jsonify({
        "message": {
            "N": len(replicas),
            "replicas": replicas
        },
        "status": "successful"
    }), 200
    
@app.route('/add', methods=['POST'])
def add_servers():
    global ip_addresses
    def create_ip():
        rand = random.randint(2, 200)
        ip = f'127.0.0.{rand}'
        try:
            _ = ip_addresses.index(ip)
            ip = create_ip()
        except:
            ip_addresses.append(ip)
        
        return ip
    
    payload = request.get_json()
    n = payload.get('n', 0)
    hostnames = payload.get('hostnames', [])

    if len(hostnames) > n:
        return jsonify({
            "message": "<Error> Length of hostname list is more than newly added instances",
            "status": "failure"
        }), 400
        
    # Create Randomized IP Address and assign it to the container

    for _ in range(n):
        ip_address = create_ip()
        server_id = len(load_balancer.servers) + 1
        hostname = hostnames.pop(0) if hostnames else f"server_{server_id}"
        container = client.containers.run("web_server-server", name=hostname, detach=True, environment={"SERVER_ID": str(server_id), "IP_ADDRESS":ip_address})
        load_balancer.add_server(server_id)

    replicas = [f"server_{server_id}" for server_id in load_balancer.servers.keys()]
    return jsonify({
        "message": {
            "N": len(replicas),
            "replicas": replicas
        },
        "status": "successful"
    }), 200
    
@app.route('/rm', methods=['DELETE'])
def remove_servers():
    payload = request.get_json()
    n = payload.get('n', 0)
    hostnames = payload.get('hostnames', [])

    if len(hostnames) > n:
        return jsonify({
            "message": "<Error> Length of hostname list is more than removable instances",
            "status": "failure"
        }), 400

    for _ in range(n):
        if not load_balancer.servers:
            break

        server_id = list(load_balancer.servers.keys())[0]
        hostname = hostnames.pop(0) if hostnames else f"server_{server_id}"
        container = client.containers.get(hostname)
        container.stop()
        container.remove()
        load_balancer.remove_server(server_id)

    replicas = [f"server_{server_id}" for server_id in load_balancer.servers.keys()]
    return jsonify({
        "message": {
            "N": len(replicas),
            "replicas": replicas
        },
        "status": "successful"
    }), 200

@app.route('/<path>', methods=['GET'])
def route_request(path):
    request_id = request_id = random.randint(100000, 999999)
    server_id = load_balancer.get_server(request_id)
    if server_id is None:
        return jsonify({
            "message": "No servers available",
            "status": "failure"
        }), 500

    server_name = f"server_{server_id}"
    container = client.containers.get(server_name)
    container_ip = api_client.inspect_container(container.name)['NetworkSettings']['IPAddress']

    try:
        resp = requests.get(f"http://{container_ip}:5000/{path}", headers=request.headers)
        return resp.content, resp.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({
            "message": f"<Error> '{path}' endpoint does not exist in server replicas",
            "status": "failure"
        }), 400

if __name__ == '__main__':
    app.run(port=5000)
