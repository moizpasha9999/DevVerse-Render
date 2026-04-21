import random
import pickle
import requests
import base64

APP_PASSWORD="zkjx wagf vzid xinp"
def get_verification_code():
    code = random.randint(100000, 999999)
    return code
def encrypted(password):
    return password
def image_url_to_base64(image_url):
    response = requests.get(image_url, timeout=10)
    response.raise_for_status()  # raises error for bad status

    image_bytes = response.content
    base64_string = base64.b64encode(image_bytes).decode('utf-8')

    return base64_string
def image_to_base64(image):
    return 0