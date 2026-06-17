import pytest
from httpx import AsyncClient
from app.core.config import settings

@pytest.mark.asyncio
async def test_auth_flow(client: AsyncClient):
    test_email = "user@example.com"
    test_password = "secure_password_123"
    api_prefix = settings.API_V1_STR

    # 1. Test registration
    register_payload = {"email": test_email, "password": test_password}
    reg_response = await client.post(f"{api_prefix}/auth/register", json=register_payload)
    assert reg_response.status_code == 201
    reg_data = reg_response.json()
    assert reg_data["email"] == test_email
    assert "id" in reg_data

    # 2. Test registration duplicates
    dup_response = await client.post(f"{api_prefix}/auth/register", json=register_payload)
    assert dup_response.status_code == 400

    # 3. Test successful authentication
    login_payload = {"email": test_email, "password": test_password}
    login_response = await client.post(f"{api_prefix}/auth/login", json=login_payload)
    assert login_response.status_code == 200
    token_data = login_response.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"
    access_token = token_data["access_token"]

    # 4. Fetch private credentials resource using the token
    headers = {"Authorization": f"Bearer {access_token}"}
    me_response = await client.get(f"{api_prefix}/auth/me", headers=headers)
    assert me_response.status_code == 200
    me_data = me_response.json()
    assert me_data["email"] == test_email
    assert me_data["is_active"] is True

    # 5. Fail retrieval with bad token credentials
    bad_headers = {"Authorization": "Bearer invalid_token_value"}
    unauthorized_response = await client.get(f"{api_prefix}/auth/me", headers=bad_headers)
    assert unauthorized_response.status_code == 401