
import os
import socket
import subprocess
import sys
import time

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


BASE_URL = "http://127.0.0.1:5003/"


@pytest.fixture(scope="session", autouse=True)
def flask_server():
    # Check whether port 5003 is already occupied.
    try:
        with socket.create_connection(("127.0.0.1", 5003), timeout=1):
            pytest.fail(
                "Port 5003 is already in use. Stop the existing Flask server "
                "and rerun pytest."
            )
    except OSError:
        pass

    process = subprocess.Popen(
        [sys.executable, "app.py"],
        cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    deadline = time.time() + 30

    while time.time() < deadline:
        if process.poll() is not None:
            pytest.fail("Flask server stopped before it was ready.")

        try:
            with socket.create_connection(("127.0.0.1", 5003), timeout=1):
                break
        except OSError:
            time.sleep(0.5)
    else:
        process.terminate()
        pytest.fail("Flask server did not start on port 5003.")

    yield

    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait()


@pytest.fixture
def setup_teardown():
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install())
    )
    driver.maximize_window()

    yield driver

    driver.quit()


def get_alert_text(driver):
    alert = WebDriverWait(driver, 10).until(
        EC.alert_is_present()
    )

    text = alert.text
    print(f"\nJavaScript Alert: {text}")

    # Keep the alert visible so you can see it.
    time.sleep(5)

    alert.accept()
    return text


def test_empty_username(setup_teardown):
    driver = setup_teardown
    driver.get(BASE_URL)

    driver.find_element(By.NAME, "username").clear()
    driver.find_element(By.NAME, "pwd").send_keys("Password123")
    driver.find_element(By.NAME, "sb").click()

    assert get_alert_text(driver) == "Username cannot be empty."


def test_empty_password(setup_teardown):
    driver = setup_teardown
    driver.get(BASE_URL)

    driver.find_element(By.NAME, "username").send_keys("Mersi")
    driver.find_element(By.NAME, "pwd").clear()
    driver.find_element(By.NAME, "sb").click()

    assert get_alert_text(driver) == "Password cannot be empty."


def test_short_password(setup_teardown):
    driver = setup_teardown
    driver.get(BASE_URL)

    driver.find_element(By.NAME, "username").send_keys("Mersi")
    driver.find_element(By.NAME, "pwd").send_keys("abc1")
    driver.find_element(By.NAME, "sb").click()

    assert get_alert_text(driver) == (
        "Password must be at least 6 characters long."
    )


def test_valid_input(setup_teardown):
    driver = setup_teardown
    driver.get(BASE_URL)

    driver.find_element(By.NAME, "username").send_keys("Mersi")
    driver.find_element(By.NAME, "pwd").send_keys("abc123")
    driver.find_element(By.NAME, "sb").click()

    time.sleep(1)

    assert "/submit" in driver.current_url

    body_text = driver.find_element(By.TAG_NAME, "body").text
    assert "Hello, Mersi! Welcome to the website" in body_text
