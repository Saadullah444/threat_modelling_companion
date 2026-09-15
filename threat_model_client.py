import argparse
import json

import requests


def process_threat_model_request(threat_model_path, detected_threats_path, threat_model_endpoint="http://127.0.0.1:8010/process-threat-model"):
    """Send a threat model payload to the local processing endpoint."""
    with open(threat_model_path, "r", encoding="utf-8") as file:
        threat_model = json.load(file)

    with open(detected_threats_path, "r", encoding="utf-8") as file:
        detected_threats = json.load(file)

    payload = {
        "threat_model": threat_model,
        "detected_threats": detected_threats,
    }

    response = requests.post(threat_model_endpoint, json=payload, timeout=3000)

    if response.status_code == 200:
        print("Threat Model API Response:")
        print(json.dumps(response.json(), indent=4))
        return response.json()

    print(f"Threat Model API Error: {response.status_code}")
    print(response.text)
    return None


def main():
    parser = argparse.ArgumentParser(description="Submit a threat model and detected threats to the local threat-model API.")
    parser.add_argument("threat_model_path", help="Path to the threat model JSON file")
    parser.add_argument("detected_threats_path", help="Path to the detected threats JSON file")
    parser.add_argument("--endpoint", default="http://127.0.0.1:8010/process-threat-model", help="Threat model API endpoint URL")
    args = parser.parse_args()

    process_threat_model_request(args.threat_model_path, args.detected_threats_path, args.endpoint)


if __name__ == "__main__":
    main()
