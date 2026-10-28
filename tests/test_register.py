
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

BASE_URL = "http://127.0.0.1:5001"
@pytest.fixture
def setup_teardown():
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install())
    )
    driver.maximize_window()
    yield driver
    driver.quit()

def read_alert(driver):
    alert = WebDriverWait(driver, 5).until(
        EC.alert_is_present()
    )
    message = alert.text
    alert.accept()
    return message

def test_empty_name(setup_teardown):
    driver = setup_teardown
    driver.get(BASE_URL)

    driver.find_element(By.ID, "name").clear()
    driver.find_element(By.ID, "password").send_keys("testpassword")
    driver.find_element(By.ID, "submit").click()

    assert read_alert(driver) == "Username cannot be empty"

def test_empty_password(setup_teardown):
    driver = setup_teardown
    driver.get(BASE_URL)

    driver.find_element(By.ID, "name").send_keys("testuser")
    driver.find_element(By.ID, "password").clear()
    driver.find_element(By.ID, "submit").click()

    assert read_alert(driver) == "Password cannot be empty"

def test_short_password(setup_teardown):
    driver = setup_teardown
    driver.get(BASE_URL)

    driver.find_element(By.ID, "name").send_keys("testuser")
    driver.find_element(By.ID, "password").send_keys("123")
    driver.find_element(By.ID, "submit").click()

    assert read_alert(driver) == "Password must be at least 6 characters long"

def test_valid_registration(setup_teardown):
    driver = setup_teardown
    driver.get(BASE_URL)

    driver.find_element(By.ID, "name").send_keys("testuser")
    driver.find_element(By.ID, "password").send_keys("testpass123")
    driver.find_element(By.ID, "submit").click()

    WebDriverWait(driver, 5).until(
        EC.url_contains("/register")
    )

    assert "Registration Successful testuser" in driver.page_source
