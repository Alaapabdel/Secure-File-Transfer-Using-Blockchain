import requests

def add_file_to_ipfs(file_data):
    url = "http://localhost:5001/api/v0/add"
    try:
        files = {'file': ('file', file_data)}
        response = requests.post(url, files=files)
        response.raise_for_status()
        add_info = response.json()
        # print(add_info)
        return add_info
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"Other error occurred: {err}")
    return None

def get_file_from_ipfs(ipfs_hash):
    url = f"http://localhost:5001/api/v0/cat?arg={ipfs_hash}"
    try:
        response = requests.post(url)
        response.raise_for_status()
        # print(response.content)
        return response.content
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"Other error occurred: {err}")
    return None
