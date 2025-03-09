from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def test_swagger_search():
    driver = webdriver.Chrome()
    try:
        driver.get("http://localhost:5000/api/docs")
        
        # Wait for Swagger UI to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='FIN']"))
        )
        
        # Input FIN and execute search
        fin_input = driver.find_element(By.CSS_SELECTOR, "input[placeholder='FIN']")
        fin_input.send_keys("S1234567X")
        execute_btn = driver.find_element(By.CLASS_NAME, "execute")
        execute_btn.click()
        
        # Verify response
        response = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "response"))
        )
        assert "200" in response.text
    finally:
        driver.quit()