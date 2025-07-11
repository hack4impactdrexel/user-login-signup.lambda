from aws_lambda_typing import events, context
from typing import Dict, Any
#import boto3

def handler(event: events.APIGatewayProxyEventV2, context: context.Context) -> Dict[str, Any]:
    print(event)
    print(context)
	
    return {
        'statusCode': 200,
        'body': 'Hello from Lambda!'
    }