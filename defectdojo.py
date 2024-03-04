import sys
import requests
import datetime

def get_product_id_by_name(token, product_name, url):
    headers = {
        "Authorization": f"Token {token}",
        "Content-Type": "application/json"
    }
    response = requests.get(f"{url}/api/v2/products/", headers=headers)

    products = response.json()
    if 'results' in products:
        for product in products['results']:
            if product['name'] == product_name:
                return product['id']

    return None

def create_new_engagement(token, product_id, engagement_name, url):
    headers = {
        "Authorization": f"Token {token}",
        "Content-Type": "application/json"
    }
    url = f"{url}/api/v2/engagements/"
    
    today = datetime.date.today()
    target_end_date = today + datetime.timedelta(days=15)
    
    data = {
        "name": engagement_name,
        "product": product_id,
        "target_start": today.isoformat(),
        "target_end": target_end_date.isoformat()
    }
    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 201:
        engagement = response.json()
        return engagement['id']
    else:
        print(f"Failed to create new engagement. Status code: {response.status_code}")
        print(f"Response content: {response.text}")
        raise ValueError(f"Failed to create new engagement.")

def post_engagement_and_import_scan(token, product_name, engagement_name, file_path, url, scan_type):
    product_id = get_product_id_by_name(token, product_name, url)

    engagement_id = create_new_engagement(token, product_id, engagement_name, url)

    headers2 = {
        "Authorization": f"Token {token}"
    }

    data2 = {
        "scan_type": scan_type,
        "engagement": engagement_id,
        "product": product_id
    }

    files = {
        "file": open(file_path, "rb")
    }

    url2 = f"{url}/api/v2/import-scan/"

    response2 = requests.post(url2, headers=headers2, data=data2, files=files)

    print("Response 2:", response2.text)

def create_product(token, product_name, url):
    headers = {
        "Authorization": f"Token {token}",
        "Content-Type": "application/json"
    }
    url = f"{url}/api/v2/products/"

    data = {
        "name": product_name,
        "prod_type": 1,
        "description": "Sample description"
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 201:
        product = response.json()
        return product['id']
    elif response.status_code == 400:  # Product with the same name might already exist
        print(f"A product with the name '{product_name}' already exists.")
        return get_product_id_by_name(token, product_name, url)
    else:
        print(f"Failed to create new product. Status code: {response.status_code}")
        print(f"Response content: {response.text}")
        return None

def create_product_if_not_exists(token, product_name, url):
    product_id = get_product_id_by_name(token, product_name, url)
    if product_id is not None:
        return product_id

    return create_product(token, product_name, url)

if __name__ == '__main__':
    if len(sys.argv) != 7:
        print("Usage: python dojo.py <url> <token> <product_name> <engagement_name> <file_path> <scan_type>")
        sys.exit(1)

    url, token, product_name, engagement_name, file_path, scan_type = sys.argv[1:]

    product_id = create_product_if_not_exists(token, product_name, url)

    if product_id is None:
        raise ValueError(f"Product '{product_name}' not found or could not be created.")

    post_engagement_and_import_scan(token, product_name, engagement_name, file_path, url, scan_type)
