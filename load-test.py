import requests
import concurrent.futures
import time

# Use Minikube tunnel URL
uri = "http://127.0.0.1:61230/data"
duration = 60          # seconds
concurrent_requests = 50

def make_request():
    try:
        response = requests.get(uri, timeout=5)
        return response.status_code
    except Exception:
        return "Error"

def load_test():
    start_time = time.time()
    request_count = 0

    print(f"Starting load test: {concurrent_requests} concurrent requests for {duration} seconds")

    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrent_requests) as executor:
        while time.time() - start_time < duration:
            futures = [executor.submit(make_request) for _ in range(concurrent_requests)]
            for f in concurrent.futures.as_completed(futures):
                _ = f.result()
                request_count += 1

    print(f"Total requests: {request_count}")
    print(f"Completed in {time.time() - start_time:.1f} seconds")

if __name__ == "__main__":
    load_test()

