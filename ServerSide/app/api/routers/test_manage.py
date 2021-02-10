from fastapi.testclient import TestClient
from app.api.dependencies.authentication import get_current_user
from app.main import app
from app.db.models import User
import json

client = TestClient(app)

def override_get_current_user():
    return User.select().where(User.email == 'test@yahoo.com')

def test_quiz_creat():
    app.dependency_overrides[get_current_user] = override_get_current_user
    data = {
        'name' : 'secound quiz',
        'start_time' : "2021-01-11T12:14:45.750Z",
        'end_time': "2021-02-11T12:14:45.750Z"
    }
    headers = {
        'Content-Type': 'application/json'
    }
    response = client.post("/manage/quiz/create",headers=headers,data=json.dumps(data))
    print(response.json())
    assert response.status_code == 200
    assert response.json() == {'code': 200, 'msg': 'oook'}
    app.dependency_overrides = {}