import os
os.environ.setdefault("ZIMAGE_API_TOKEN", "test-token-abcdefghijklmnopqrstuvwxyz-123456")

from fastapi.testclient import TestClient
from zimage_server.app import create_app


def test_root_returns_api_metadata_json_not_html():
    app = create_app(start_worker=False)
    with TestClient(app) as client:
        response = client.get("/")
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("application/json")
        assert response.json() == {
            "service": "z-image-turbo-kaggle-t4x2",
            "type": "rest-api",
            "version": "0.1.0",
            "docs": "/docs",
            "health": "/health",
            "ready": "/ready",
            "info": "/v1/info",
        }
