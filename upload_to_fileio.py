import requests

def upload_to_fileio(file_path: str):
        response = requests.post('https://file.io', files={'file': open(file_path, 'rb')})
        return response.json()['link']
