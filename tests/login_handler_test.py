import pytest
from unittest.mock import patch, MagicMock
from src.main import login_handler, client
import botocore.exceptions
import json
import boto3

valid_body = {
	"email": "temp@h4i.com",
	"password": "H4i12345$"
}

no_email_body = {
	"email": "",
	"password": "H4i12345$"
}

no_password_body = {
	"email": "temp@h4i.com",
	"password": ""
}

invalid_user = {
    "email": "temp_mahi@h4i.com",
	"password": "H4i12345$"
}

def test_login_success():
    mock_response = {
        "AuthenticationResult": {
            "IdToken": "mock-id-token",
            "AccessToken": "mock-access-token",
            "RefreshToken": "mock-refresh-token"
        }
    }

    with patch("src.main.client.initiate_auth", return_value=mock_response):
        result = login_handler(valid_body)

        assert result["status"] == 200
        body = json.loads(result["body"])  # Deserialize JSON string
        assert body["message"] == "Login successful."
        assert body["id_token"] == "mock-id-token"
        assert body["access_token"] == "mock-access-token"
        assert body["refresh_token"] == "mock-refresh-token"
        
def test_no_email_provided():
    with patch("src.main.client.initiate_auth"):
        result = login_handler(no_email_body)
        assert result["status"] == 400
        assert result["body"] == "No email provided."
        
def test_no_password_provided():
    with patch("src.main.client.initiate_auth"):
        result = login_handler(no_password_body)
        assert result["status"] == 400
        assert result["body"] == "No password provided."
        
def test_login_not_authorized():
    not_auth_exception = boto3.client("cognito-idp", region_name="us-east-1").exceptions.NotAuthorizedException(
        {
            "Error": {
                "Code": "NotAuthorizedException",
                "Message": "Incorrect username or password."
            }
        },
        operation_name="InitiateAuth"
    )

    with patch("src.main.client.initiate_auth", side_effect=not_auth_exception):
        result = login_handler(valid_body)

        assert result["status"] == 401
        assert result["body"] == "Incorrect username or password."
        
def test_login_user_not_confirmed():
    exception = boto3.client("cognito-idp", region_name="us-east-1").exceptions.UserNotConfirmedException(
        {
            "Error": {
                "Code": "UserNotConfirmedException",
                "Message": "User is not confirmed."
            }
        },
        operation_name="InitiateAuth"
    )

    with patch("src.main.client.initiate_auth", side_effect=exception):
        result = login_handler(valid_body)

        assert result["status"] == 403
        assert result["body"] == "User not confirmed. Please confirm your email."
        
def test_login_client_error():
    exception = botocore.exceptions.ClientError(
        error_response={
            "Error": {
                "Code": "SomeOtherClientError",
                "Message": "Something went wrong"
            }
        },
        operation_name="InitiateAuth"
    )

    with patch("src.main.client.initiate_auth", side_effect=exception):
        result = login_handler(valid_body)

        assert result["status"] == 500
        assert "ClientError" in result["body"]
        assert "Something went wrong" in result["body"]
        
def test_login_generic_exception():
    with patch("src.main.client.initiate_auth", side_effect=Exception("Unexpected failure")):
        result = login_handler(valid_body)

        assert result["status"] == 500
        assert "Internal Server Error" in result["body"]
        assert "Unexpected failure" in result["body"]