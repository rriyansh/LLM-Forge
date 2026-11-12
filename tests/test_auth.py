from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.utils.auth import get_principal
from src.utils.security import create_access_token


def test_principal_from_jwt():
    app = FastAPI()

    @app.get("/whoami")
    async def whoami(p=__import__("fastapi").Depends(get_principal)):
        return {"user": p.user_id, "role": p.role}

    client = TestClient(app)
    token = create_access_token("u1", role="admin", tenant="t1")
    r = client.get("/whoami", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert r.json()["user"] == "u1"
    assert r.json()["role"] == "admin"
