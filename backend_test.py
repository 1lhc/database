import requests
import time
from concurrent.futures import ThreadPoolExecutor
from scipy import stats
import numpy as np

def test_backend_search(fin):
    """Tests the search endpoint of the backend API."""
    start_time = time.time()
    response = requests.get(
        f"http://localhost:5000/api/applications/search?fin={fin}",
        headers={"X-API-Key": "default_key"}
    )
    if response.status_code != 200:
        print(f"Backend: Search failed - {response.json()}")
        return None
    print("Backend: Search completed successfully.")
    return response.json(), time.time() - start_time


def test_backend_create_stvp(application_id):
    """Tests the STVP creation endpoint of the backend API."""
    start_time = time.time()
    response = requests.post(
        f"http://localhost:5000/api/applications/{application_id}/create-stvp",
        headers={"X-API-Key": "default_key"}
    )
    # Handle both creation (201) and extension (200)
    if response.status_code not in [200, 201]:
        print(f"Backend: STVP failed - {response.json()}")
        return None, 0
    
    print("Backend: STVP operation succeeded")
    return response.json(), time.time() - start_time


def test_backend():
    """Tests the full backend workflow."""
    start_time = time.time()
    
    # Step 1: Search for application
    search_result, search_time = test_backend_search("S1234567X")
    if not search_result:
        return False, 0
    
    # Step 2: Create STVP
    stvp_result, stvp_time = test_backend_create_stvp(search_result[0]["id"])
    if not stvp_result:
        return False, 0
    
    total_time = time.time() - start_time
    print(f"Backend: Total process time: {total_time:.2f} seconds")
    return True, total_time


def load_test():
    """Runs a load test by executing the test_backend function concurrently."""
    start_time = time.time()  # Start timer for the load test
    latencies = []  # To store latency measurements

    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(test_backend) for _ in range(100)]
        for future in futures:
            success, latency = future.result()
            if success:
                latencies.append(latency)

    elapsed_time = time.time() - start_time  # End timer for the load test

    # Calculate statistics
    success_count = len(latencies)
    total_time = sum(latencies)
    avg_latency = total_time / success_count if success_count > 0 else 0

    # Calculate 95% confidence interval
    try:
        ci = stats.t.interval(0.95, len(latencies)-1, loc=np.mean(latencies), scale=stats.sem(latencies))
    except ValueError:
        ci = (None, None)

    # Calculate Average Actual Elapsed Time
    avg_actual_elapsed_time = elapsed_time / success_count if success_count > 0 else 0

    print(f"Processed {success_count}/100 cases with 20 concurrent users")
    print(f"- Success Rate: {success_count}/100")
    print(f"- Total Time Reported by Threads: {total_time:.2f}s")
    print(f"- Avg Reported Latency: {avg_latency:.4f}s")
    print(f"- 95% Confidence Interval for Latency: {ci}")
    print(f"- Actual Elapsed Time: {elapsed_time:.2f}s")
    print(f"- Average Actual Elapsed Time: {avg_actual_elapsed_time:.2f}s")


if __name__ == "__main__":
    print("\nRunning Load Test...")
    load_test()