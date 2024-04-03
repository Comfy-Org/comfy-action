import os
import sys
import json
import requests
import base64

def ensure_directory_exists(path):
    """Ensure that a directory exists; if it doesn't, create it."""
    if not os.path.exists(path):
        print("Directory does not exist: " + path)
        exit(1)

def download_model(url, directory, model_name):
    """Download a model file from a URL into a specific directory."""
    print(f"Downloading {model_name} from {url} to {directory}")
    response = requests.get(url, allow_redirects=True)
    file_path = os.path.join(directory, model_name)
    with open(file_path, 'wb') as file:
        file.write(response.content)
    print(f"Downloaded {model_name} to {directory}")

def main(models_json_base64, base_directory):
    """Main function to parse JSON and download models."""
    print(models_json_base64)
    print("Base directory: " + base_directory)
    models_json = base64.b64decode(models_json_base64).decode("utf-8")
    print(models_json)
    models = json.loads(models_json)

    for model_name, model_info in models.items():
        url = model_info["url"]
        directory = model_info.get("directory", "")
        target_directory = os.path.join(base_directory, directory)
        ensure_directory_exists(target_directory)
        download_model(url, target_directory, model_name)


if __name__ == "__main__":
    models_json = sys.argv[1]
    base_directory = sys.argv[2]
    main(models_json, base_directory)
