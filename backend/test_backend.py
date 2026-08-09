import asyncio
import httpx
from src.api.main import app

async def run_tests():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Test Health
        r = await client.get("/health")
        print("GET /health:", r.status_code, r.json())
        assert r.status_code == 200

        # 2. Test Login (Form data for OAuth2)
        r = await client.post("/api/v1/auth/token", data={"username": "demo@agriguardian.com", "password": "Demo@12345"})
        print("POST /api/v1/auth/token:", r.status_code, r.json())
        assert r.status_code == 200
        token_data = r.json()
        access_token = token_data["access_token"]
        headers = {"Authorization": f"Bearer {access_token}"}

        # 3. Test GET /me
        r = await client.get("/api/v1/auth/me", headers=headers)
        print("GET /api/v1/auth/me:", r.status_code, r.json())
        assert r.status_code == 200

        # 4. Test GET /farm
        r = await client.get("/api/v1/farm/", headers=headers)
        print("GET /api/v1/farm/:", r.status_code, r.json())
        assert r.status_code == 200

        # 5. Test POST /recommendation/irrigation (AI Model)
        ai_payload = {
            "temperature": 32.5,
            "humidity": 45.0,
            "soil_moisture": 22.0,
            "rainfall_prev_day": 0.0
        }
        r = await client.post("/api/v1/recommendation/irrigation", json=ai_payload)
        print("POST /api/v1/recommendation/irrigation:", r.status_code, r.json())
        assert r.status_code == 200
        print("\nALL BACKEND API TESTS PASSED!")

if __name__ == "__main__":
    asyncio.run(run_tests())
