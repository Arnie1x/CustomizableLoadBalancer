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
        virtual_servers = self.hash_map[slot]
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
  