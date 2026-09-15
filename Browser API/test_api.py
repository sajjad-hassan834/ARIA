import asyncio
import httpx
from main import app
from services.browser_service import browser_service


async def run_tests():
    print("Starting API verification tests...")
    # Explicitly start the browser service as lifespan would on startup
    await browser_service.start()

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Health check
        res = await client.get("/health")
        print("1. Health Check:", res.status_code, res.json())
        assert res.status_code == 200
        assert res.json()["browser_active"] is True
        assert res.json()["status"] == "healthy"

        # 2. Open URL
        res = await client.post("/api/browser/open", json={"url": "https://example.com"})
        print("2. Open URL:", res.status_code, res.json())
        assert res.status_code == 200
        assert res.json()["status"] == "success"
        assert "example.com" in res.json()["url"]

        # 3. Screenshot
        res = await client.post("/api/browser/screenshot", json={"filename": "test_example.png"})
        print("3. Screenshot:", res.status_code, res.json())
        assert res.status_code == 200
        assert res.json()["status"] == "success"

        # 4. Search (Google test)
        res = await client.post("/api/browser/search", json={"query": "ARIA AI", "platform": "google"})
        print("4. Search Google:", res.status_code, res.json())
        assert res.status_code == 200
        assert res.json()["status"] == "success"

        # 5. History
        res = await client.get("/api/browser/history")
        print("5. History:", res.status_code, "entries count:", len(res.json().get("history", [])))
        assert res.status_code == 200
        assert res.json()["status"] == "success"
        assert len(res.json()["history"]) >= 3

        # 6. Execute Plan
        plan = {
            "steps": [
                {"step": 1, "action": "open_browser", "target": "https://example.com"},
                {"step": 2, "action": "screenshot", "filename": "plan_test.png"}
            ],
            "source": "brain_api"
        }
        res = await client.post("/api/browser/execute-plan", json=plan)
        print("6. Execute Plan:", res.status_code, res.json())
        assert res.status_code == 200
        assert res.json()["status"] == "completed"
        assert res.json()["steps_executed"] == 2

    # Clean shutdown
    await browser_service.stop()
    print("\n--- ALL VERIFICATION TESTS PASSED! ---")


if __name__ == "__main__":
    asyncio.run(run_tests())
