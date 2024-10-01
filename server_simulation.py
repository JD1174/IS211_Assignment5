import csv
from queue import Queue

class Request:
    def __init__(self, time, file, process_time):
        self.time = time
        self.file = file
        self.process_time = process_time

class Server:
    def __init__(self):
        self.current_request = None
        self.time_remaining = 0

    def tick(self):
        if self.current_request:
            self.time_remaining -= 1
            if self.time_remaining <= 0:
                self.current_request = None

    def busy(self):
        return self.current_request is not None

    def start_next(self, new_request):
        self.current_request = new_request
        self.time_remaining = new_request.process_time

def simulateOneServer(filename):
    server = Server()
    request_queue = Queue()
    waiting_times = []

    # Read the CSV file and populate the request queue
    with open(filename) as file:
        reader = csv.reader(file)
        for row in reader:
            time, file, process_time = int(row[0]), row[1], int(row[2])
            request = Request(time, file, process_time)
            request_queue.put(request)

    current_time = 0
    while not request_queue.empty():
        if not server.busy() and not request_queue.empty():
            next_request = request_queue.get()
            waiting_times.append(current_time - next_request.time)
            server.start_next(next_request)
            #print(f"Starting request {next_request.file} at time {current_time}")

        server.tick()
        current_time += 1

    average_wait = sum(waiting_times) / len(waiting_times)
    #print(f"Average wait time: {average_wait} seconds")
    return average_wait

def simulateManyServers(filename, num_servers):
    servers = [Server() for i in range(num_servers)]
    request_queues = [Queue() for i in range(num_servers)]
    waiting_times = []

    # Read the CSV file and distribute requests to queues in a round-robin fashion
    with open(filename) as file:
        reader = csv.reader(file)
        for row in reader:
            time, file, process_time = int(row[0]), row[1], int(row[2])
            request = Request(time, file, process_time)
            request_queues[time % num_servers].put(request)

    current_time = 0
    while any(not q.empty() for q in request_queues):
        for i in range(num_servers):
            if not servers[i].busy() and not request_queues[i].empty():
                next_request = request_queues[i].get()
                waiting_times.append(current_time - next_request.time)
                servers[i].start_next(next_request)
                #print(f"Server {i} starting request {next_request.file} at time {current_time}")

            servers[i].tick()
        current_time += 1

    average_wait = sum(waiting_times) / len(waiting_times)
    #print(f"Average wait time with {num_servers} servers: {average_wait} seconds")
    return average_wait

if __name__ == "__main__":
    import sys
    filename = sys.argv[1]
    if len(sys.argv) > 2:
        num_servers = int(sys.argv[2])
        print(f"Average Wait Time with {num_servers} servers: {simulateManyServers(filename, num_servers)} seconds")
    else:
        print(f"Average Wait Time with 1 server: {simulateOneServer(filename)} seconds")