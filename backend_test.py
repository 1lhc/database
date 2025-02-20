import requests
import time
from concurrent.futures import ThreadPoolExecutor
from locust import HttpUser, task, between

# Existing functions for sequential and thread-based load testing
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

    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(test_backend) for _ in range(100)]
        results = [f.result() for f in futures]

    elapsed_time = time.time() - start_time  # End timer for the load test
    
    success_count = sum(1 for success, _ in results if success)
    total_time = sum(time for _, time in results)
    print(f"Processed 100 cases with 20 concurrent users")
    print(f"- Success Rate: {success_count}/100")
    print(f"- Total Time Reported by Threads: {total_time:.2f}s")
    print(f"- Avg Reported Time/Case: {total_time/100:.2f}s")
    print(f"- Actual Elapsed Time: {elapsed_time:.2f}s")
    print(f"- Average Actual Elapsed Time: {elapsed_time/100:.2f}s")

# # Locust Integration
# class WorkPassUser(HttpUser):
#     wait_time = between(0, 0)  # Simulate users waiting between 1 and 5 seconds between tasks

#     @task
#     def full_backend_workflow(self):
#         """
#         Simulates the full backend workflow:
#         1. Search for an application.
#         2. Create an STVP for the found application.
#         """
#         # Step 1: Search for an application
#         search_response = self.client.get(
#             "/api/applications/search?fin=S1234567X",
#             headers={"X-API-Key": "default_key"},
#             name="Search Application"
#         )

#         if search_response.status_code != 200:
#             # Log failure and stop this task
#             print(f"Search failed: {search_response.text}")
#             return

#         # Parse the search result to extract the application ID
#         search_data = search_response.json()
#         if not search_data:
#             print("No application found for FIN S1234567X")
#             return

#         application_id = search_data[0]["id"]

#         # Step 2: Create an STVP for the application
#         stvp_response = self.client.post(
#             f"/api/applications/{application_id}/create-stvp",
#             headers={"X-API-Key": "default_key"},
#             name="Create STVP"
#         )

#         if stvp_response.status_code not in [200, 201]:
#             # Log failure
#             print(f"STVP creation failed: {stvp_response.text}")
#             return

#         # Log success
#         print("Full backend workflow completed successfully.")

# if __name__ == "__main__":
#     # Run the Locust test
#     print("\nRunning Locust Load Test...")
#     print("To run Locust, execute the following command in your terminal:")
#     print("locust -f backend_test.py --host=http://localhost:5000")

if __name__ == "__main__":
    # # Run the backend test sequentially 10 times
    # success_count = 0
    # total_time = 0
    # for i in range(10):
    #     print(f"\nBackend Test {i+1}:")
    #     success, time_taken = test_backend()
    #     if success:
    #         success_count += 1
    #     total_time += time_taken
    # print(f"\nBackend Summary:")
    # print(f"- Success Rate: {success_count}/10")
    # print(f"- Average Time: {total_time/10:.2f}s")

    # Run the load test
    print("\nRunning Load Test...")
    load_test()