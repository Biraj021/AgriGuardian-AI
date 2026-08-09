from fastapi.testclient import TestClient
import sys

sys.path.insert(0, "./")
from src.api.main import app


def run_checks():
    client = TestClient(app)
    print('health ->', client.get('/health').json())
    print('rec ->', client.post('/api/v1/recommendation/generate', json={'temperature':30,'humidity':50,'soil_moisture':0.2}).json())
    print('weather ->', client.get('/api/v1/weather/current').json())


if __name__ == '__main__':
    run_checks()
