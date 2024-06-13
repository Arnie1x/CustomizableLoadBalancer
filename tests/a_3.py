import requests
import docker
import time

client = docker.from_env()

# Test /rep endpoint
resp = requests.get("http://127.0.0.1:5000/rep")
print(resp.json())
time.sleep(3)

# Test /add endpoint
payload = {"n": 1, "hostnames": ["server_x"]}
resp = requests.post("http://127.0.0.1:5000/add", json=payload)
print(resp.json())
time.sleep(3)

# Test /rm endpoint
payload = {"n": 1, "hostnames": ["server_x"]}
resp = requests.delete("http://127.0.0.1:5000/rm", json=payload)
print(resp.json())
time.sleep(3)

# Test server failure recovery
server1 = client.containers.get("server_1")
server1.stop()
server1.remove(force=True)
time.sleep(5)  # Wait for the load balancer to recover

# Launch requests and observe the distribution