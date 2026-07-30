import importlib.metadata

import pytest
import werkzeug

if not hasattr(werkzeug, "__version__"):
    try:
        werkzeug.__version__ = importlib.metadata.version("werkzeug")
    except importlib.metadata.PackageNotFoundError:
        werkzeug.__version__ = "3.1.0"

from examples.flask_app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_index_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.get_json()
    assert data["name"] == "Krama Core Flask Example"
    assert "op_consult" in data["endpoints"]


def test_op_consult_endpoint(client):
    response = client.get("/api/op-consult")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "success"
    assert data["resource_type"] == "Bundle"
    assert data["total_resources"] > 0
    assert "bundle" in data


def test_compliance_endpoint_default(client):
    response = client.get("/api/compliance")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "success"
    assert data["passed"] is True
    assert "DPDP Act" in data["frameworks"]


def test_compliance_endpoint_post_payload(client):
    payload = {
        "country": "US",
        "purpose": "Treatment",
        "patient_identifiers": ["us_mrn"],
        "lawful_basis": "treatment",
        "consent_present": True,
        "encrypted": True,
        "data_residency_region": "us-east-1",
        "requested_fields": ["diagnosis"],
        "necessary_fields": ["diagnosis"],
    }
    response = client.post("/api/compliance", json=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "success"
    assert data["passed"] is True
    assert data["country"] == "USA"
