import pytest
from unittest.mock import patch, MagicMock
from src.main import sign_up_handler, client
import botocore.exceptions

valid_body = {
	"email": "mahidhar1287@gmail.com",
	"password": "Yogi6011$"
}

no_email_body = {
    "email": "",
    "password": "Yogi6011$"
}

no_password_body = {
    "email": "mahidhar1287@gmail.com",
    "password": ""
}

def test_signup_success():
    mock_response = {"UserConfirmed": False}
    
    with patch("src.main.client.sign_up", return_value=mock_response):
        result = sign_up_handler(valid_body)
        assert result["status"] == 200
        assert "Sign-up successful" in result["body"]

def test_no_email_fail():
    with patch("src.main.client.sign_up"):
        result = sign_up_handler(no_email_body)
        assert result["status"] == 400
        assert result["body"] == "No email provided."

def test_no_password_fail():
    with patch("src.main.client.sign_up"):
        result = sign_up_handler(no_password_body)
        assert result["status"] == 400
        assert result["body"] == "No password provided."

def test_username_exists_fail():
    with patch("src.main.client.sign_up") as mock_sign_up:
        mock_sign_up.side_effect = client.exceptions.UsernameExistsException(
            {
                "Error": {"Code": "UsernameExistsException", "Message": "User already exists"}
            },
            operation_name="SignUp"
        )
        result = sign_up_handler(valid_body)
        assert result["status"] == 409
        assert "User already exists" in result["body"]

def test_signup_client_error_username_failure():
    with patch("src.main.client.sign_up") as mock_sign_up:
        mock_sign_up.side_effect = botocore.exceptions.ClientError(
            {
                "Error": {"Code": "UsernameExistsException", "Message": "User already exists."}
            },
            operation_name="SignUp"
        )

        result = sign_up_handler(valid_body)
        assert result["status"] == 409
        assert "User already exists" in result["body"]

def test_signup_client_error_generic_failure():
    with patch("src.main.client.sign_up") as mock_sign_up:
        mock_sign_up.side_effect = botocore.exceptions.ClientError(
            {
                "Error": {"Code": "InvalidUser", "Message": ""}
            },
            operation_name="SignUp"
        )

        result = sign_up_handler(valid_body)
        assert result["status"] == 500
        assert "ClientError" in result["body"]

def test_signup_generic_failure():
    with patch("src.main.client.sign_up", side_effect=Exception("Unexpected error")):
        result = sign_up_handler(valid_body)
        assert result["status"] == 500
        assert "Internal Server Error" in result["body"]