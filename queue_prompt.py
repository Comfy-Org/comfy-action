import json
import requests
import argparse

def read_json_file(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def post_json_to_server(json_data, url):
    return requests.post(url, json=json_data)

def main(json_file_path, server_url):
    # Read JSON file
    json_contents = read_json_file(json_file_path)
    # Print the json_contents
    #print(json.dumps(json_contents, indent=4))
    # Construct the new JSON object
    data_to_send = {"prompt": json_contents}

    # Post the JSON to the server
    response = post_json_to_server(data_to_send, server_url)
    #print("Status Code:" + str(response.status_code))
    #print("Response:" + response.text)
    response_json = response.json()
    if ('prompt_id' not in response_json):
        print("Error: prompt_id not found in response.")
        print(response_json)
    else:
        print(response_json['prompt_id'])

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Send a JSON file contents to a server as a prompt.')
    parser.add_argument('json_file_path', type=str, help='Path to the JSON file to send.')
    parser.add_argument('--server-url', type=str, default='http://localhost:8188/prompt', help='URL of the server to send the JSON to.')

    args = parser.parse_args()
    main(args.json_file_path, args.server_url)
