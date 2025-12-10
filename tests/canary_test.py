import requests
import time
import sys


def wait_for_server(url, timeout=60):
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                print(f"Server is up! Status code: {response.status_code}")
                return True
        except requests.exceptions.ConnectionError:
            pass
        time.sleep(2)
        print("Waiting for server...")
    return False


def run_canary():
    base_url = "http://localhost:8000"
    metrics_url = f"{base_url}/metrics"

    print(f"Checking {metrics_url}...")
    if not wait_for_server(metrics_url):
        print("Failed to connect to server.")
        sys.exit(1)

    print("Canary check passed: Server is reachable and metrics endpoint is active.")
    sys.exit(0)


if __name__ == "__main__":
    run_canary()
