import base64
import json
import argparse


def serialize_json_as_base64(data):
    # Convert the Python dictionary to a JSON string
    json_string = json.dumps(data)

    # Encode the JSON string as bytes, then encode to Base64
    json_bytes = json_string.encode("utf-8")
    base64_bytes = base64.b64encode(json_bytes)

    # Convert the Base64 bytes back to a string
    base64_string = base64_bytes.decode("utf-8")

    return base64_string


def main():
    parser = argparse.ArgumentParser(description="Serialize JSON data as Base64")
    parser.add_argument(
        "--json_file", type=str, required=True, help="Path to JSON file"
    )
    args = parser.parse_args()

    with open(args.json_file, "r") as file:
        data = json.load(file)

    base64_encoded_json = serialize_json_as_base64(data)
    print(base64_encoded_json)


if __name__ == "__main__":
    main()
