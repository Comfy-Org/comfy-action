import requests
import time
import sys

def is_successful():
    try:
        response = requests.get("http://localhost:8188/queue")
        if response.status_code == 200:
            return True
    except requests.exceptions.ConnectionError:
        print("Not started yet")
        return False
    return False

def main():
    start_time = time.time()
    print("Polling server start...")
    while True:
        success = is_successful()
        if success:
            print("Server started.")
            break

        if time.time() - start_time > 60:
            print("Error: Server did start within timeout.")
            sys.exit(1)
        print("Server not started yet. Waiting...")
        time.sleep(5)

if __name__ == "__main__":
    main()
