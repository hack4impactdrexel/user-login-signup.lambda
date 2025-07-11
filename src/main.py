from aws_lambda_typing import events, context
from typing import Dict, Any
import boto3
import json
import botocore.exceptions

client = boto3.client('cognito-idp', region_name="us-east-1")
COGNITO_USER_POOL_ID = "1hcrufs3e1m66gmes0jisr34ce"

def handler(event: events.APIGatewayProxyEventV2, context: context.Context) -> Dict[str, Any]:
    # print(event)
    # print(context)
    try:
        event = json.loads(event)
        body = json.loads(event.get("body", {}))
        if "login" in event["path"]:
            return login_handler(body)
        elif "sign-up" in event["path"]:
            return sign_up_handler(body)
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
        response = client.sign_up(
            ClientId=COGNITO_USER_POOL_ID,
            Username=email,
            Password=password,
            UserAttributes=[
                {
                    "Name": "email",
                    "Value": email
                }
            ]
        )

        return {
            "status": 200,
            "body": json.dumps({
                "message": "Sign-up successful. Please confirm your email.",
                "userConfirmed": response.get("UserConfirmed", False)
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

def login_handler() -> Dict[str, Any]:
    return {}

if __name__ == "__main__":
    with open("temp.json") as j:
        print(type(j.read()))
        print(handler(j.read(), None))