from fastapi.testclient import TestClient
from app.api.dependencies.authentication import get_current_user
from app.main import app
from app.db.models import User
import json

client = TestClient(app)

def test_register():
    data = {
          "name": "test",
          "password": "1234",
          "email": "test@yahoo.com"
        }
    headers = {
        'Content-Type': 'application/json'
    }
    response = client.post("/auth/register",headers=headers,data=json.dumps(data))
    assert response.status_code == 200
    assert response.json() == {'msg':'Successfully Registerd'} or response.json() == {'msg':'email already taken by another person'}