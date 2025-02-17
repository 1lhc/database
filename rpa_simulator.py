import time
import random

def rpa_search_application(fin):
    """Simulates searching for an application in the old RPA system."""
    print(f"RPA: Searching for application with FIN {fin}...")
    time.sleep(2)  # Simulate UI navigation delay
    if random.random() < 0.1:  # 10% chance of failure
        print("RPA: Error - Search failed!")
        return None
    print("RPA: Search completed successfully.")
    return {"id": "A001", "fin": fin, "status": "ACTIVE"}

def rpa_create_stvp(application_id):
    """Simulates creating an STVP in the old RPA system."""
    print(f"RPA: Creating STVP for application {application_id}...")
    time.sleep(3)  # Simulate form filling and submission delay
    if random.random() < 0.1:  # 10% chance of failure
        print("RPA: Error - STVP creation failed!")
        return None
    print("RPA: STVP created successfully.")
    return {"stvp_id": f"STVP{application_id[1:]}"}

def rpa_process():
    """Simulates a full RPA workflow."""
    start_time = time.time()
    
    # Step 1: Search for application
    search_result = rpa_search_application("S1234567X")
    if not search_result:
        return False
    
    # Step 2: Create STVP
    stvp_result = rpa_create_stvp(search_result["id"])
    if not stvp_result:
        return False
    
    total_time = time.time() - start_time
    print(f"RPA: Total process time: {total_time:.2f} seconds")
    return True

# Run the RPA simulation 10 times
success_count = 0
total_time = 0
for i in range(10):
    print(f"\nRPA Test {i+1}:")
    if rpa_process():
        success_count += 1
    total_time += time.time() - start_time

print(f"\nRPA Summary:")
print(f"- Success Rate: {success_count}/10")
print(f"- Average Time: {total_time/10:.2f}s")