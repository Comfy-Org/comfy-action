import os
import sys
import json
import requests

def ensure_directory_exists(path):
    """Ensure that a directory exists; if it doesn't, create it."""
    if not os.path.exists(path):
        os.makedirs(path)

def download_model(url, directory, model_name):
    """Download a model file from a URL into a specific directory."""
    response = requests.get(url, allow_redirects=True)
    file_path = os.path.join(directory, model_name)
    with open(file_path, 'wb') as file:
        file.write(response.content)
    print(f"Downloaded {model_name} to {directory}")

def main(models_json):
    """Main function to parse JSON and download models."""
    base_directory = os.path.expanduser('~/ComfyUI/models')
    models = json.loads(models_json)
    
    for model_name, model_info in models.items():
        url = model_info["url"]
        directory = model_info.get("directory", "")
        target_directory = os.path.join(base_directory, directory)
        ensure_directory_exists(target_directory)
        download_model(url, target_directory, model_name)

if __name__ == "__main__":
    models_json = sys.argv[1]
    main(models_json)
