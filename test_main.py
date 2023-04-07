import pytest
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)

# définir un fixture pour authentifier les requêtes
@pytest.fixture
def authorized_client():
    response = client.post("/login", data={"username": "admin", "password": "admin"})
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    return TestClient(app, headers=headers)

# tester la création d'une entreprise
def test_create_company(authorized_client):
    response = authorized_client.post("/companies", json={
        "name": "MyCompany",
        "address": "123 Main Street",
        "capital": 100000.0,
        "status": "active",
        "contact_person_name": "John Doe",
        "contact_person_email": "john.doe@example.com",
        "contact_person_phone": "555-1234"
    })
    assert response.status_code == 200
    assert response.json()["message"] == "Company créée"

# tester la récupération d'une entreprise par ID
def test_get_company(authorized_client):
    response = authorized_client.get("/companies/1")
    assert response.status_code == 200
    assert response.json()["name"] == "MyCompany"

# tester la mise à jour d'une entreprise par ID
def test_update_company(authorized_client):
    response = authorized_client.put("/companies/1", json={
        "name": "MyUpdatedCompany",
        "address": "456 Main Street",
        "capital": 200000.0,
        "status": "inactive",
        "contact_person_name": "Jane Doe",
        "contact_person_email": "jane.doe@example.com",
        "contact_person_phone": "555-5678"
    })
    assert response.status_code == 200
    assert response.json()["message"] == "Company modifiée"

# tester la suppression d'une entreprise par ID
def test_delete_company(authorized_client):
    response = authorized_client.delete("/companies/1")
    assert response.status_code == 200
    assert response.json()["message"] == "Entreprise avec l'ID 1 a été supprimé avec succès"

# tester la récupération de toutes les entreprises avec pagination
def test_get_companies(authorized_client):
    response = authorized_client.get("/companies?page=1&per_page=10")
    assert response.status_code == 200
    assert response.json()["page"] == 1
    assert response.json()["per_page"] == 10
    assert len(response.json()["companies"]) == 1
