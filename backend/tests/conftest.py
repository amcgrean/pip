import os

os.environ['DATABASE_URL'] = 'sqlite:///./test.db'
os.environ['SECRET_KEY'] = 'test-secret-key-12345'
os.environ['CORS_ALLOWED_ORIGINS'] = 'http://localhost:5173'
os.environ['ENVIRONMENT'] = 'test'

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.security import get_password_hash
from app.db.base_class import Base
from app.db.session import get_db
from app.main import app
from app.models.user import User

engine = create_engine('sqlite:///./test.db', connect_args={'check_same_thread': False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope='session', autouse=True)
def cleanup_test_db():
    yield
    if os.path.exists('test.db'):
        os.remove('test.db')


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    db.add(User(email='admin@test.local', full_name='Admin', password_hash=get_password_hash('Password123!'), role='admin', is_active=True))
    db.commit()
    db.close()

    def override_get_db():
        test_db = TestingSessionLocal()
        try:
            yield test_db
        finally:
            test_db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides = {}


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def auth_headers(client):
    res = client.post('/api/v1/auth/login', json={'email': 'admin@test.local', 'password': 'Password123!'})
    token = res.json()['access_token']
    return {'Authorization': f'Bearer {token}'}
