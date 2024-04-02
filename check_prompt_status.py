import requests
import time
import sys

def get_status(prompt_id, url):
    response = requests.get(f"{url}/{prompt_id}")
    if response.status_code == 200:
        return response.json()
    return None

def is_completed(status_response, prompt_id):
    # Check if the expected fields exist in the response
    return (
        status_response and 
        prompt_id in status_response and 
        'status' in status_response[prompt_id] and 
        status_response[prompt_id]['status'].get('completed', False)
    )

def main(prompt_id, server_url, timeout):
    start_time = time.time()
    while True:
        status_response = get_status(prompt_id, server_url)
        if is_completed(status_response, prompt_id):
            print("Prompt completed.")
            break

        if time.time() - start_time > timeout:
            print("Timeout reached without completion.")
            sys.exit(1)

        time.sleep(10)  # Check every 10 seconds

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python check_prompt_status.py <prompt_id> <server_url> <timeout>")
        sys.exit(1)

    prompt_id_arg = sys.argv[1]
    server_url_arg = sys.argv[2]
    timeout_arg = int(sys.argv[3])

    main(prompt_id_arg, server_url_arg, timeout_arg)
