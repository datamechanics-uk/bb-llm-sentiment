import json
import boto3
import os

class Score:
    def __init__(self):
        self.brt = boto3.client('bedrock-runtime',
                                region_name=os.environ.get('AWS_REGION'),
                                aws_access_key_id=os.environ.get('AWS_ACCESS'),
                                aws_secret_access_key=os.environ.get('AWS_SECRET'))

    def score(self, text):
        prompt_input = f"""
Human: You are an expert financial analyst with years of experience in stock market prediction.
Numerically classify the following text based on its impact on the Standard & Poor's 500 Index returns.
You have 5 options to pick from: -1, -0.5, 0, 0.5, 1.

<text>
{text}
</text>

Option definitions:
-1: Strongly negative impact
-0.5: Moderately negative impact
0: Neutral or uncertain impact
0.5: Moderately positive impact
1: Strongly positive impact

Respond with your option.
Do not provide any additional commentary or text.
Do not provide any justification.
Do not provide any explanations.

Assistant:
"""

        response = self.brt.invoke_model(
            body=json.dumps({
                "prompt": prompt_input,
                "max_tokens_to_sample": 10,  # A numerical value within our boundaries should not exceed 10 tokens.
                "temperature": 0.1,
                "top_p": 0.5,
            }),
            modelId='anthropic.claude-v2',
            accept='application/json',
            contentType='application/json'
        )

        score = json.loads(response['body'].read())['completion']

        return score