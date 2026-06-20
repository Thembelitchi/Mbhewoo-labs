from fastapi.testclient import TestClient
from app.main import app

# Initialize the pytest TestClient targeted at our app instance
client = TestClient(app)


def test_health_check_endpoint():
    """
    Assert that hitting the GET /health router endpoint returns 
    a successful 200 OK standard status code and the correct payload envelope.
    """
    response = client.get("/health")
    
    # Assert successful status code
    assert response.status_code == 200
    
    # Assert exact required payload keys and values
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "mbhewoo-labs"
