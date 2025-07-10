from aws_lambda_typing import events, context_
from typing import Dict, Any
import boto3

def handler(event: events.APIGatewayProxyEventV2, context: context_.Context) -> Dict[str, Any]:
    print(event)
    print(context)
	
    return {
        'statusCode': 200,
        'body': 'Hello from Lambda!'
    }