import hashlib
import hmac
import base64
import time
import random
import string
from urllib.parse import urlencode
import uuid


# This is a new function that would generate the device_id and device_id_type based on the given OS
def generate_device_id(os_type):
    device_id = ''
    device_id_type = ''

    if os_type == 'Android':
        device_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=32)) 
        device_id_type = 'OAID' if bool(random.getrandbits(1)) else 'Android_ID' 

    elif os_type == 'iOS':
        device_id = str(uuid.uuid4())
        device_id_type = 'IDFA' if bool(random.getrandbits(1)) else 'UUID'

    elif os_type == 'Linux':
        device_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=12))

    elif os_type == 'Web':
        device_id = str(uuid.uuid4())

    return device_id, device_id_type

def generate_sig(params, app_secret):
    sorted_params = sorted(params.items(), key=lambda x:x[0])
    raw_string = '&'.join(f"{k}={v}" for k, v in sorted_params)
    base64_encoded_str = base64.b64encode(raw_string.encode('utf-8')).decode('utf-8')
    
    sha1_key = app_secret
    hashed = hmac.new(sha1_key.encode('utf-8'), base64_encoded_str.encode('utf-8'), hashlib.sha1)
    return hashlib.md5(hashed.digest()).hexdigest()

def generate_request_url(app_key, app_secret, device_id, device_id_type, ids):
    params = {
        'app_key': app_key,
        'client_os_type': 4,
        'nonce': ''.join(random.choices(string.ascii_letters + string.digits, k=16)),
        'timestamp': int(time.time() * 1000),
        'server_api_version': '1.0.0',
        'device_id': device_id,
        'device_id_type': device_id_type,
        'ids': ids
    }

    sig = generate_sig(params, app_secret)
    params['sig'] = sig

    url_encoded_params = urlencode(params)
    url = f"https://api.ximalaya.com/albums/get_batch?{url_encoded_params}"

    return url

os_type = 'iOS'
device_id, device_id_type = generate_device_id(os_type)

# Use the function
app_key = 'b617866c20482d133d5de66fceb37da3'
app_secret = '4d8e605fa7ed546c4bcb33dee1381179'  # please replace with your app secret
ids = '4769101'

url = generate_request_url(app_key, app_secret, device_id, device_id_type, ids)
print(url)
