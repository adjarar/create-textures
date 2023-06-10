import json
import requests
import io
import base64
import glob
from PIL import Image, PngImagePlugin

def encode_img(image_path):
    base64_encoded_img = base64.b64encode(open(image_path, "rb").read())
    return 'data:image/png;base64,' + str(base64_encoded_img, encoding='utf-8')

def response2json(url, route, payload):
    txt2img_response_raw = requests.post(url=f'{url}/sdapi/v1/{route}', json=payload)
    return txt2img_response_raw.json()

def decode_img(img):
    return Image.open(io.BytesIO(base64.b64decode(img.split(",",1)[0])))