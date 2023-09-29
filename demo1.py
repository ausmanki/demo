#!/usr/bin/env python3
import requests
import json
import sys

# The ASoC REST APIs used in this script:
REST_APIKEYLOGIN = "https://cloud.appscan.com/api/v2/Account/ApiKeyLogin"
REST_SCANS = "https://cloud.appscan.com/api/v2/Scans/DynamicAnalyzer"

def main():
    if len(sys.argv) != 6:
        print("\nUsage: python appscan_dast.py <API_Key> <API_Secret> <App_ID> <Target_URL> <Scan_Name>\n")
        sys.exit(1)

    API_KEY = sys.argv[1]
    API_SECRET = sys.argv[2]
    APP_ID = sys.argv[3]
    TARGET_URL = sys.argv[4]
    SCAN_NAME = sys.argv[5]

    token = get_token(API_KEY, API_SECRET)

    scan_id = start_dast_scan(token, APP_ID, TARGET_URL, SCAN_NAME)
    print(f"DAST scan started successfully. Scan ID: {scan_id}")

def get_token(api_key, api_secret):
    try:
        json_data = {"KeyId": api_key, "KeySecret": api_secret}
        response = requests.post(REST_APIKEYLOGIN, json=json_data)
        response.raise_for_status()
        json_data = json.loads(response.text)
        return json_data['Token']
    except requests.exceptions.RequestException as e:
        print("Error in get_token():\n" + str(e))
        sys.exit(1)

def start_dast_scan(token, app_id, target_url, scan_name):
    try:
        headers = {
            "Authorization": "Bearer " + token,
            "Content-Type": "application/json"
        }
        json_data = {
            "AppId": app_id,
            "StartingUrl": target_url,
            "PresenceId" : "1791027c-d05e-ee11-8457-14cb65725114",
            "Profile": "Default",
            "ScanName": scan_name,
            "Incremental": False,
            "UserAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36"
        }
        response = requests.post(REST_SCANS, headers=headers, json=json_data)
        response.raise_for_status()
        json_data = json.loads(response.text)
        return json_data['Id']
    except requests.exceptions.RequestException as e:
        print("Error in start_dast_scan():\n" + str(e))
        sys.exit(1)

if __name__ == "__main__":
    main()
