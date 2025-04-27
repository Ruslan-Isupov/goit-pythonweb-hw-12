def test_healthchecker_success(client):
    # Call method
    response = client.get("api/healthchecker")
    data = response.json()

    # Assertions
    assert response.status_code == 200, response.text
    assert data["message"] == "Welcome to REST API"


def test_healthchecker_success_fail(client_fail_healthchecker):
    # Call method
    response = client_fail_healthchecker.get("api/healthchecker")
    data = response.json()

    # Assertions
    assert response.status_code == 500, response.text
    assert "detail" in data
