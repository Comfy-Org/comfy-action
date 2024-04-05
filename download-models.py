import os
import sys
import json
import requests
import base64
import argparse

def ensure_directory_exists(path):
    """Ensure that a directory exists; if it doesn't, create it."""
    if not os.path.exists(path):
        os.makedirs(path)
        print("Created directory: " + path)

def download_model(url, directory, model_name):
    """Download a model file from a URL into a specific directory."""
    print(f"Downloading {model_name} from {url} to {directory}")
    file_path = os.path.join(directory, model_name)
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(file_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192): 
                f.write(chunk)
    print(f"Downloaded {model_name} to {directory}")

def main(args):
    """Main function to parse JSON and download models based on the input
    mode."""
    if args.mode == 'base64':
        models_json = base64.b64decode(args.input).decode("utf-8")
    elif args.mode == 'raw':
        models_json = args.input
    
    print(models_json)
    print("Base directory: " + args.directory)
    models = json.loads(models_json)

    for model_name, model_info in models.items():
        url = model_info["url"]
        directory = model_info.get("directory", "")
        target_directory = os.path.join(args.directory, directory)
        ensure_directory_exists(target_directory)
        download_model(url, target_directory, model_name)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download models based on a JSON input.")
    parser.add_argument('mode', choices=['base64', 'raw'], help="Input mode: 'base64' for a base64 encoded string, 'raw' for a JSON content itself.")
    parser.add_argument('input', help="Input string or json content, depending on the mode.")
    parser.add_argument('directory', help="Base directory where models will be downloaded.")
    
    args = parser.parse_args()
    main(args)
