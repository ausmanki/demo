#!/usr/bin/env python3
import requests
import json
import sys
import time

# The ASoC REST APIs used in this script:
REST_APIKEYLOGIN = "https://cloud.appscan.com/api/v2/Account/ApiKeyLogin"
REST_SCANS = "https://cloud.appscan.com/api/v2/Scans/DynamicAnalyzer"
base_api_url = "https://cloud.appscan.com/api/v2"


def generate_engagement_id():
    return str(int(time.time()))  # Use timestamp as engagement ID


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

    # Generate engagement ID
    engagement_id = generate_engagement_id()

    print(f"Waiting for scan to finish")
    start = time.time()
    elapsed = 0
    max_time = 60 * 30

    while elapsed < max_time:
        prev_status = ""
        status_obj = get_scan_status(token, scan_id)
        if status_obj is None:
            print("Error getting status")
            break

        status = status_obj["Status"]

        if status != prev_status:
            prev_status = status
            print(f"Scan Status: {prev_status}")

        if status == "Completed":
            print(f"Scan completed with status: {status}")
            print("Scan Summary:")
            print(f"\t High Issues: {status_obj['HighVulnerabilities']}")
            print(f"\t Med Issues: {status_obj['MediumVulnerabilities']}")
            print(f"\t Low Issues: {status_obj['LowVulnerabilities']}")
            print()
            print(f"For full details visit: https://cloud.appscan.com/main/myapps/{APP_ID}/scans/{scan_id}/scanOverview")
            report_id = generate_report(token, scan_id, SCAN_NAME)
            if report_id is not None:
                break
        elif status == "Error":
            print(f"Scan completed with status: {status}")
            print(f"Error message: {status_obj['ErrorMessage']}")
            break

        time.sleep(30)
        elapsed = time.time() - start

    if elapsed >= max_time:
        print("Scan timed out after 30 minutes.")


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
            "Profile": "Default",
            "PresenceId" : "1791027c-d05e-ee11-8457-14cb65725114",
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


def get_scan_status(token, scan_id):
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {token}",
    }
    r = requests.get(f"https://cloud.appscan.com/api/v2/Scans/DynamicAnalyzer/{scan_id}", headers=headers)
    if r.status_code != 200:
        print(f"Error getting scan status: {r.status_code}")
        return None
    response_json = r.json()
    return {
        "Status": response_json.get("LatestExecution", {}).get("ExecutionProgress"),
        "HighVulnerabilities": response_json.get("LatestExecution", {}).get("NHighIssues"),
        "MediumVulnerabilities": response_json.get("LatestExecution", {}).get("NMediumIssues"),
        "LowVulnerabilities": response_json.get("LatestExecution", {}).get("NLowIssues"),
        "ErrorMessage": response_json.get("LatestExecution", {}).get("ErrorMessage")
    }


def generate_report(token, scan_id, scan_name):
    url = f"https://cloud.appscan.com/api/v2/Reports/Security/Scan/{scan_id}"

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }

    body = {
        'Configuration': {
            'Summary': 'true',
            'Details': 'true',
            'Discussion': 'true',
            'Overview': 'true',
            'TableOfContent': 'true',
            'Advisories': 'true',
            'FixRecommendation': 'true',
            'History': 'true',
            'Coverage': 'true',
            'MinimizeDetails': 'true',
            'Articles': 'true',
            'ReportFileType': 'XML',
            'Title': scan_name,
            'Locale': 'en-US',
            'Notes': 'Generated by Python script',
            'Comments': 'true'
        }
    }

    try:
        response = requests.post(url, headers=headers, json=body)
        response.raise_for_status()
        report_id = response.json().get('Id')
        print(f"Report generated successfully. Report ID: {report_id}")
        return report_id

    except requests.exceptions.RequestException as e:
        print(f"Error generating report: {e}")


if __name__ == "__main__":
    main()
