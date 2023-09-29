import requests

def get_access_token(client_id, client_secret):
    token_url = "https://cloud.appscan.com/api/V2/Account/ApiKeyLogin"
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json'
    }
    data = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret
    }
    response = requests.post(token_url, headers=headers, data=data)
    return response.json().get('access_token')

def start_dast_scan(access_token, target_url):
    base_url = "https://cloud.appscan.com/api/v2/Scans/DynamicAnalyzer"
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }
    
    scan_config = {
        "target": target_url,
        "scan_type": "DAST",
        "profile": "Default",
        "incremental": False,
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36"
    }
    
    response = requests.post(base_url, json=scan_config, headers=headers)
    
    if response.status_code == 200:
        print("DAST scan started successfully.")
    else:
        print(f"Failed to start DAST scan. Status code: {response.status_code}")
        print(response.text)

# Replace these with your actual client ID and client secret, and target URL
client_id = '52b2038d-7047-e707-ec57-920e21f2a19b'
client_secret = 'x8QcZdUmZaaEfAkBnaw7Zb52ThasKRFFIw9wQOnmnOY1'
target_url = 'http://demo.testfire.net'

access_token = get_access_token(client_id, client_secret)
if access_token:
    start_dast_scan(access_token, target_url)
else:
    print("Failed to obtain access token.")
