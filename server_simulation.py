import csv
import argparse
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
    requests =[]

    # Read the CSV file into a list of Request objects
    with open(filename) as file:
        reader = csv.reader(file)
        for row in reader:
            # .strip() handles potential blank spaces in the CSV
            time, filepath, process_time = int(row[0].strip()), row[1].strip(), int(row[2].strip())
            requests.append(Request(time, filepath, process_time))
            
    # Sort requests by arrival time just in case the CSV isn't in perfect chronological order
    requests.sort(key=lambda r: r.time)

    current_time = 0
    req_idx = 0 # Updated: Using an index is much faster than popping from a list
    
    # Keep running while there are future requests, requests waiting in queue, or the server is busy
    while req_idx < len(requests) or not request_queue.empty() or server.busy():
        
        # If the request's arrival time matches the current time, it enters the queue
        while req_idx < len(requests) and requests[req_idx].time == current_time:
            request_queue.put(requests[req_idx])
            req_idx += 1

        if not server.busy() and not request_queue.empty():
            next_request = request_queue.get()
            waiting_times.append(current_time - next_request.time)
            server.start_next(next_request)
            #print(f"Starting request {next_request.file} at time {current_time}")

        server.tick()
        current_time += 1

    average_wait = sum(waiting_times) / len(waiting_times) if waiting_times else 0
    
    print(f"Average Wait Time for 1 server: {average_wait:.2f} seconds")
    return average_wait

def simulateManyServers(filename, num_servers):
    servers = [Server() for _ in range(num_servers)]
    request_queues = [Queue() for _ in range(num_servers)]
    waiting_times = []
    requests =[]

    with open(filename) as file:
        reader = csv.reader(file)
        for row in reader:
            time, filepath, process_time = int(row[0].strip()), row[1].strip(), int(row[2].strip())
            requests.append(Request(time, filepath, process_time))

    requests.sort(key=lambda r: r.time)

    current_time = 0
    req_idx = 0
    server_index = 0  # Used to track Round-Robin distribution

    # Keep running until all requests are processed
    while req_idx < len(requests) or any(not q.empty() for q in request_queues) or any(s.busy() for s in servers):
        
        # Requests arrive at the load balancer
        while req_idx < len(requests) and requests[req_idx].time == current_time:
            req = requests[req_idx]
            
            # Round-Robin distribution: goes to server_index, then updates index
            request_queues[server_index].put(req)
            server_index = (server_index + 1) % num_servers
            req_idx += 1

        # Process ticks for all servers
        for i in range(num_servers):
            if not servers[i].busy() and not request_queues[i].empty():
                next_request = request_queues[i].get()
                waiting_times.append(current_time - next_request.time)
                servers[i].start_next(next_request)
                #print(f"Server {i} starting request {next_request.file} at time {current_time}")

            servers[i].tick()
        current_time += 1

    average_wait = sum(waiting_times) / len(waiting_times) if waiting_times else 0
    
    # Print and return
    print(f"Average Wait Time with {num_servers} servers: {average_wait:.2f} seconds")
    return average_wait

def main():
    # Setup argparse to cleanly handle named parameters (--file and --servers)
    parser = argparse.ArgumentParser(description="Web Server Network Simulator")
    parser.add_argument("--file", required=True, help="The CSV file containing the network requests")
    parser.add_argument("--servers", type=int, help="The number of servers to simulate")
    
    args = parser.parse_args()

    if args.servers is not None:
        simulateManyServers(args.file, args.servers)
    else:
        simulateOneServer(args.file)

if __name__ == "__main__":
    main()