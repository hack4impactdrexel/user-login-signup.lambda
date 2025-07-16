from aws_lambda_typing import events, context
from typing import Dict, Any
import boto3
import json
import botocore.exceptions

client = boto3.client('cognito-idp', region_name="us-east-1")
COGNITO_USER_POOL_ID = "1hcrufs3e1m66gmes0jisr34ce"
COGNITO_CLIENT_ID = "us-east-1_9TZBS9Yey"

def handler(event: events.APIGatewayProxyEventV2, context: context.Context) -> Dict[str, Any]:
    print(event)
    print(context)
    try:
        raw_body = event.get("body", "{}")
        body = json.loads(raw_body) if isinstance(raw_body, str) else raw_body
        if "login" in event["path"]:
            return login_handler(body)
        elif "sign-up" in event["path"]:
            return sign_up_handler(body)
        elif "forgot-password" in event["path"]:
            return forgot_password_handler(body)
        else:
            return {
                "status": 501,
                "body": "This path is not specified."
            }
    except Exception as e:
        return {
            "status": 500,
            "body": f"Internal Server Error. {e}"
        }


def sign_up_handler(body: Dict[str, Any]) -> Dict[str, Any]:
    email = body.get("email", "")
    password = body.get("password", "")
    phone_number = body.get("phone_number", "")
    full_name = body.get("full_name", "")

    if not email:
        return {
            "status": 400,
            "body": "No email provided."
        }
    if not password:
        return {
            "status": 400,
            "body": "No password provided."
        }
    if not phone_number:
        return {
            "status": 400,
            "body": "No phone number provided."
        }
    if not full_name:
        return {
            "status": 400,
            "body": "No name provided."
        }
    
    try:
        response = client.sign_up(
            ClientId=COGNITO_USER_POOL_ID,
            Username=email,
            Password=password,
            UserAttributes=[
                {"Name": "email", "Value": email},
                {"Name": "phone_number", "Value": phone_number},
                {"Name": "name", "Value": full_name},
                {"Name": "picture", "Value": "s3://ifam-project-user-profile-pictures/user.png"}
            ]
        )

        return {
            "status": 200,
            "body": json.dumps({
                "message": "Sign-up successful. Please confirm your email.",
                "userConfirmed": response.get("UserConfirmed", False),
            })
        }
    except client.exceptions.UsernameExistsException:
        return {
            "status": 409,
            "body": "User already exists."
        }
    except botocore.exceptions.ClientError as e:
        if e.response["Error"]["Code"] == "UsernameExistsException":
            return {
                "status": 409,
                "body": "User already exists."
            }
        return {
            "status": 500,
            "body": f"ClientError: {e}"
        }
    except Exception as e:
        return {
            "status": 500,
            "body": f"Internal Server Error. {e}"
        }

def login_handler(body: Dict[str, Any]) -> Dict[str, Any]:
    email = body.get("email", "")
    password = body.get("password", "")

    if not email:
        return {
            "status": 400,
            "body": "No email provided."
        }
    if not password:
        return {
            "status": 400,
            "body": "No password provided."
        }

    try:
        print("Before: ", email, password)
        response = client.initiate_auth(
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={
                'USERNAME': email,
                'PASSWORD': password
            },
            ClientId=COGNITO_USER_POOL_ID
        )
        print("After: ", response)

        return {
            "status": 200,
            "body": json.dumps({
                "message": "Login successful.",
                "id_token": response['AuthenticationResult']['IdToken'],
                "access_token": response['AuthenticationResult']['AccessToken'],
                "refresh_token": response['AuthenticationResult']['RefreshToken']
            })
        }
    except client.exceptions.NotAuthorizedException:
        return {
            "status": 401,
            "body": "Incorrect username or password."
        }
    except client.exceptions.UserNotConfirmedException:
        return {
            "status": 403,
            "body": "User not confirmed. Please confirm your email."
        }
    except botocore.exceptions.ClientError as e:
        return {
            "status": 500,
            "body": f"ClientError: {e}"
        }
    except Exception as e:
        return {
            "status": 500,
            "body": f"Internal Server Error. {e}"
        }

def forgot_password_handler(body: Dict[str, Any]) -> Dict[str, Any]:
    return {}