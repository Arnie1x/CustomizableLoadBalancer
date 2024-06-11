import requests
import threading
import random
from requests_futures.sessions import FuturesSession

num_requests = 10000
server_counts = {1: 0, 2: 0, 3: 0}
session = FuturesSession(max_workers=100)
futures = []

for _ in range(num_requests):
    futures.append(session.get('http://localhost:5000/home'))

for future in futures:
    resp = future.result()
    if resp.status_code == 200:
        server_id = int(resp.json()["message"].split("_")[1].strip())
        server_counts[server_id] += 1

# Plot the results in a bar chart
import matplotlib.pyplot as plt
server_ids, counts = zip(*server_counts.items())
plt.bar(server_ids, counts)
plt.xlabel("Server ID")
plt.ylabel("Request Count")
plt.title("Request Distribution among Servers (N=3)")
plt.savefig('./outputs/a-1.png', bbox_inches='tight')
plt.show()