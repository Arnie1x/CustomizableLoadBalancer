import hashlib

NUM_SERVERS = 3
NUM_SLOTS = 512
NUM_VIRTUAL_SERVERS = 9
SERVER_HASH_FUNCTION = lambda i: i + 2*i**2 + 17
VIRTUAL_SERVER_HASH_FUNCTION = lambda i, j: i + j + 2*j**2 + 25

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