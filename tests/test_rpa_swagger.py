import os
import time
import random
import logging
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from scipy import stats
import numpy as np
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway

# Configuration
BASE_URL = os.getenv("TEST_URL", "http://localhost:5000/api/docs")
FAILURE_RATE = float(os.getenv("RPA_FAILURE_RATE", 0.10))
TEST_FIN = "S1234567X"
TEST_APPLICATION_ID = "A0001"

@pytest.fixture(scope="module")
def driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)
    yield driver
    driver.quit()

def simulate_rpa_failure():
    if random.random() < FAILURE_RATE:
        logging.warning("RPA: Simulated failure triggered")
        return True
    return False

def test_swagger_search(driver):
    """Tests application search via Swagger UI"""
    if simulate_rpa_failure():
        pytest.skip("Simulated RPA failure")
        
    try:
        driver.get(f"{BASE_URL}/#/Applications/get_applications_search")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='fin']"))
        ).send_keys(TEST_FIN)
        
        driver.find_element(By.CLASS_NAME, "execute").click()
        response = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "response"))
        )
        assert "200" in response.text
        assert TEST_APPLICATION_ID in response.text
        return time.time()
    except Exception as e:
        logging.error(f"Search failed: {str(e)}")
        raise

def test_swagger_create_stvp(driver):
    """Tests STVP creation via Swagger UI"""
    if simulate_rpa_failure():
        pytest.skip("Simulated RPA failure")
        
    try:
        driver.get(f"{BASE_URL}/#/Applications/post_applications__application_id__create_stvp")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='application_id']"))
        ).send_keys(TEST_APPLICATION_ID)
        
        driver.find_element(By.CLASS_NAME, "execute").click()
        response = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "response"))
        )
        assert "STVP" in response.text
        assert "20" in response.text  # Check for 200 or 201
        return time.time()
    except Exception as e:
        logging.error(f"STVP creation failed: {str(e)}")
        raise

def run_full_rpa_process():
    """Simulates full RPA workflow with metrics collection"""
    registry = CollectorRegistry()
    test_duration = Gauge('rpa_test_duration_seconds', 'Full RPA process duration', registry=registry)
    success = False
    
    try:
        start = time.time()
        driver = webdriver.Chrome()  # Use context manager in real implementation
        test_swagger_search(driver)
        test_swagger_create_stvp(driver)
        duration = time.time() - start
        test_duration.set(duration)
        success = True
    except Exception:
        duration = time.time() - start
        raise
    finally:
        push_to_gateway('localhost:9091', job='rpa-tests', registry=registry)
        return success, duration

@pytest.mark.parametrize("iteration", range(10))
def test_rpa_simulation(iteration):
    """Runs RPA simulation 10 times with metrics"""
    success, duration = run_full_rpa_process()
    assert success, "RPA process failed"
    logging.info(f"Iteration {iteration+1}: {duration:.2f}s")

def test_load():
    """Simulates load test with 100 serial executions"""
    latencies = []
    success_count = 0
    
    for _ in range(100):
        success, duration = run_full_rpa_process()
        if success:
            latencies.append(duration)
            success_count += 1
    
    # Calculate metrics
    avg_latency = np.mean(latencies)
    ci = stats.t.interval(0.95, len(latencies)-1, loc=avg_latency, scale=stats.sem(latencies))
    
    logging.info(f"""
    RPA Load Test Results:
    - Success Rate: {success_count}/100
    - Average Latency: {avg_latency:.2f}s
    - 95% CI: {ci}
    """)
    assert success_count >= 90, "Success rate below 90%"