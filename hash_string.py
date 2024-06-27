import hashlib
import sys
import json


def main(json_string):
    # Ensure the JSON string is valid
    try:
        json_data = json.loads(json_string)
    except json.JSONDecodeError:
        print("Invalid JSON string")
        sys.exit(1)

    # Convert JSON string to bytes
    json_bytes = json_string.encode("utf-8")

    # Calculate SHA256 hash
    hash_object = hashlib.sha256(json_bytes)
    hash_hex = hash_object.hexdigest()

    # Output the hash
    print(f"hash={hash_hex}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python generate_hash.py '<json_string>'")
        sys.exit(1)

    json_string = sys.argv[1]
    main(json_string)
