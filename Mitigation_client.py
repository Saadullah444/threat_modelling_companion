import argparse
import json
from pathlib import Path

import requests


def send_mitigation_request(input_path, api_url="http://127.0.0.1:8000/mitigate"):
    """Send a JSON list of threats to the local mitigation API."""
    payload = Path(input_path).read_text(encoding="utf-8")

    response = requests.post(
        api_url,
        data=payload,
        headers={"Content-Type": "application/json"},
        timeout=300,
    )
    response.raise_for_status()

    print(json.dumps(response.json()["data"], indent=2, ensure_ascii=False))
    print("Saved to:", response.json()["file"])
    return response.json()


def main():
    parser = argparse.ArgumentParser(description="Submit threats to the local mitigation API.")
    parser.add_argument("input_path", help="Path to the JSON file containing the threats list")
    parser.add_argument("--api-url", default="http://127.0.0.1:8000/mitigate", help="Mitigation API endpoint URL")
    args = parser.parse_args()

    send_mitigation_request(args.input_path, args.api_url)


if __name__ == "__main__":
    main()