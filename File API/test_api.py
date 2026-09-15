import os
import sys
from pathlib import Path

# Add FileAPI to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent / "FileAPI"))

from fastapi.testclient import TestClient
from FileAPI.main import app
from FileAPI.config import HISTORY_FILE

client = TestClient(app)

def run_tests():
    print("--- 1. Testing /health ---")
    resp = client.get("/health")
    print(resp.status_code, resp.json())
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"
    assert resp.json()["port"] == 8004

    print("\n--- 2. Testing /api/folders/create ---")
    folder_name = "_aria_test_folder"
    resp = client.post("/api/folders/create", json={"name": folder_name, "location": "desktop"})
    print(resp.status_code, resp.json())
    assert resp.status_code == 201
    test_folder_path = resp.json()["data"]["path"]

    print("\n--- 3. Testing /api/files/create ---")
    resp = client.post("/api/files/create", json={
        "name": "aria_sample.txt",
        "location": test_folder_path,
        "content": "Hello from ARIA System File API"
    })
    print(resp.status_code, resp.json())
    assert resp.status_code == 201
    created_file_path = resp.json()["data"]["path"]

    print("\n--- 4. Testing /api/files/list ---")
    resp = client.get(f"/api/files/list?location={test_folder_path}&extension=txt")
    print(resp.status_code, resp.json())
    assert resp.status_code == 200
    assert resp.json()["total"] >= 1

    print("\n--- 5. Testing /api/files/search ---")
    resp = client.post("/api/files/search", json={
        "query": "aria_sample",
        "location": test_folder_path
    })
    print(resp.status_code, resp.json())
    assert resp.status_code == 200
    assert resp.json()["total"] >= 1

    print("\n--- 6. Testing /api/files/copy ---")
    copy_dest = os.path.join(test_folder_path, "aria_sample_copy.txt")
    resp = client.post("/api/files/copy", json={
        "source": created_file_path,
        "destination": copy_dest
    })
    print(resp.status_code, resp.json())
    assert resp.status_code == 200
    assert os.path.exists(copy_dest)

    print("\n--- 7. Testing /api/files/move ---")
    move_dest = os.path.join(test_folder_path, "aria_sample_moved.txt")
    resp = client.post("/api/files/move", json={
        "source": copy_dest,
        "destination": move_dest
    })
    print(resp.status_code, resp.json())
    assert resp.status_code == 200
    assert os.path.exists(move_dest)
    assert not os.path.exists(copy_dest)

    print("\n--- 8. Testing Safety Check: Attempting to delete protected system file ---")
    resp = client.post("/api/files/delete", json={
        "path": r"C:\Windows\System32\notepad.exe"
    })
    print(resp.status_code, resp.json())
    assert resp.status_code == 403, f"Expected 403 Forbidden, got {resp.status_code}"
    print("Safety Check passed: Protected system file deletion was blocked!")

    print("\n--- 9. Testing /api/files/delete on test files ---")
    resp = client.post("/api/files/delete", json={"path": created_file_path})
    print(resp.status_code, resp.json())
    assert resp.status_code == 200

    resp = client.post("/api/files/delete", json={"path": move_dest})
    print(resp.status_code, resp.json())
    assert resp.status_code == 200

    # Cleanup test folder
    resp = client.post("/api/files/delete", json={"path": test_folder_path})
    print(resp.status_code, resp.json())
    assert resp.status_code == 200

    print("\n--- 10. Verifying data/file_history.json ---")
    assert HISTORY_FILE.exists()
    import json
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        history = json.load(f)
    print(f"Total logged operations in history: {len(history)}")
    assert len(history) >= 8
    print("Sample history record:", history[-1])

    print("\nALL ARIA FILE API TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    run_tests()
