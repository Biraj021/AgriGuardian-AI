import urllib.request
import json

def get(url):
    return urllib.request.urlopen(url).read().decode()

def post(url, payload):
    data = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    return urllib.request.urlopen(req).read().decode()

if __name__ == '__main__':
    print('health ->', get('http://127.0.0.1:8000/health'))
    print('recommendation ->', post('http://127.0.0.1:8000/api/v1/recommendation/generate', {"temperature": 30, "humidity": 50, "soil_moisture": 0.2}))
