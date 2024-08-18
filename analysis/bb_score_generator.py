import boto3
import json
import os

# Environment variables debugging
# print(f"AWS_REGION: {os.environ.get('AWS_REGION')}")
# print(f"AWS_ACCESS: {os.environ.get('AWS_ACCESS')}")
# print(f"AWS_SECRET: {os.environ.get('AWS_SECRET')}")

brt = boto3.client(
    service_name='bedrock-runtime',
    region=os.environ.get('AWS_REGION'),
    aws_access=os.environ.get('AWS_ACCESS'),
    aws_secret=os.environ.get('AWS_SECRET')
)

prompt_input = """
Hello

"""

body = json.dumps({
    "prompt": f"\n\nHuman: {prompt_input}.\n\nAssistant:",
    "max_tokens_to_sample": 300,
    "temperature": 0.1,
    "top_p": 0.5,
})

modelId = 'anthropic.claude-v2'
accept = 'application/json'
contentType = 'application/json'

try:
    response = brt.invoke_model(body=body, modelId=modelId, accept=accept, contentType=contentType)
    response_body = json.loads(response.get('body').read())
    print(response_body.get('completion'))
except Exception as e:
    print(f"An error occurred: {str(e)}")
    # Print out the exception details
    import traceback
    traceback.print_exc()