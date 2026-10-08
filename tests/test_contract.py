import os
os.environ.setdefault('ZIMAGE_API_TOKEN','test-token-abcdefghijklmnopqrstuvwxyz-123456')

from fastapi.testclient import TestClient
from zimage_server.app import create_app


def test_health_is_public_and_minimal():
    app = create_app(start_worker=False)
    with TestClient(app) as client:
        r = client.get('/health')
        assert r.status_code == 200
        assert r.json() == {'status': 'ok'}


def test_ready_requires_bearer_token():
    app = create_app(start_worker=False)
    with TestClient(app) as client:
        assert client.get('/ready').status_code == 401
        assert client.get('/ready', headers={'Authorization':'Bearer wrong'}).status_code == 403


def test_generation_rejects_empty_prompt_and_unknown_profile():
    app = create_app(start_worker=False)
    h={'Authorization':'Bearer test-token-abcdefghijklmnopqrstuvwxyz-123456'}
    with TestClient(app) as client:
        r = client.post('/v1/images/generations', headers=h, json={'prompt':'   ','seed':42,'profile':'safe_512'})
        assert r.status_code == 422
        r = client.post('/v1/images/generations', headers=h, json={'prompt':'hello','seed':42,'profile':'high_1024'})
        assert r.status_code == 422
