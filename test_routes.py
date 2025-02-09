import pytest
from app import create_app
from models import Application, db
from datetime import datetime, date, timedelta

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    with app.test_client() as client:
        with app.app_context():
            db.create_all()  # Create tables based on SQLAlchemy models
            # Add test data
            test_app = Application(
                id="TEST123",
                fin="S1234567X",
                name="Test User",
                pass_type="EP",
                doa=date.today() - timedelta(days=365),
                doe=date.today() + timedelta(days=30),
                company_uen="123456789A",
                status="ACTIVE"
            )
            db.session.add(test_app)
            db.session.commit()
        yield client

        # Clean up
        with app.app_context():
            db.session.remove()
            db.drop_all()

def test_valid_search(client):
    # Test the endpoint
    response = client.get('/api/applications/search?fin=S1234567X',
                         headers={'X-API-Key': 'default_key'})
    print(response.json)  # Debugging output
    assert response.status_code == 200
    assert len(response.json) > 0

def test_invalid_fin_search(client):
    response = client.get('/api/applications/search?fin=INVALID',
                         headers={'X-API-Key': 'default_key'})
    assert response.status_code == 400
    assert "Invalid FIN format" in response.json['error']

def test_valid_update(client):
    # Get the created application
    with client.application.app_context():
        app = Application.query.first()
        app_id = app.id
        
    data = {'new_doe': (date.today() + timedelta(days=60)).isoformat()}
    response = client.put(f'/api/applications/{app_id}/update-expiry',
                         json=data,
                         headers={'X-API-Key': 'default_key'})
    assert response.status_code == 200
    assert "amendment_id" in response.json

def test_invalid_date_update(client):
    # Get the created application
    with client.application.app_context():
        app = Application.query.first()
        app_id = app.id
        
    response = client.put(f'/api/applications/{app_id}/update-expiry',
                         json={'new_doe': 'invalid-date'},
                         headers={'X-API-Key': 'default_key'})
    assert response.status_code == 400
    assert "Invalid date format" in response.json['error']

# New test case for the root route
def test_root_route(client):
    response = client.get('/')
    assert response.status_code == 200
    assert response.json == {"message": "Welcome to the Work Pass Extension API"}