import json
import boto3
import os
import time
import cohere

class LLM:
    def __init__(self):
        self.brt = boto3.client('bedrock-runtime',
                                region_name=os.environ.get('AWS_REGION'),
                                aws_access_key_id=os.environ.get('AWS_ACCESS'),
                                aws_secret_access_key=os.environ.get('AWS_SECRET'))
        self.co  = cohere.BedrockClient(
                                aws_region=os.environ.get('AWS_REGION'),
                                aws_access_key=os.environ.get('AWS_ACCESS'),
                                aws_secret_key=os.environ.get('AWS_SECRET'))

    def prompt(self, model_id, chapter):
        # prompt = ""
        # if model_id.startswith('amazon.titan'):
        prompt = f"""
You are an expert financial analyst with years of experience in economic forecasting.
Classify the following text based on its forecasted impact on United States GDP growth and the S&P 500 Index return.
Use only these scores: -1, -0.5, 0, 0.5, 1

-1: Negative forecasted impact
-0.5: Slightly negative forecasted impact
0: Neutral or uncertain forecasted impact
0.5: Slightly positive forecasted impact
1: Positive forecasted impact

Text to analyse:
{chapter}

Rules:
- Respond with ONLY two scores from the list [-1, -0.5, 0, 0.5, 1], separated by a comma.
- Avoid defaulting to 0.5; use 0.5 only if there is strong evidence for a slightly positive impact.
- Consider both positive and negative aspects in the text.
- Do not hesitate to use -1 when appropraite.
- The text has an inherently positive bias, so consider this when scoring. A 0.5 could actually just be neutral. Use your best judgment from reading the text.
- Do not provide any additional commentary or text.

Acceptable output format:
_,_
"""

        return prompt

    def invoke_model(self, model_id, prompt_input):
        try:
            if model_id.startswith('anthropic'):
                response = self.brt.invoke_model(
                    modelId=model_id,
                    body=json.dumps({
                        "messages": [{"role": "user", "content": prompt_input}],
                        "max_tokens": 10,
                        "temperature": 0.3,
                        "top_p": 0.95,
                        "top_k": 5,
                        "anthropic_version": "bedrock-2023-05-31"
                    }),
                    contentType='application/json',
                    accept='application/json'
                )
            elif model_id.startswith('amazon.titan'):
                response = self.brt.invoke_model(
                    modelId=model_id,
                    body=json.dumps({
                        "inputText": prompt_input,
                        "textGenerationConfig": {
                            "maxTokenCount": 10,
                            "temperature": 0.3,
                            "topP": 0.95,
                        }
                    }),
                    contentType='application/json',
                    accept='application/json'
                )
            elif model_id.startswith('cohere'):
                response = self.co.chat(
                    message=prompt_input,
                    model=model_id,
                    max_tokens=10,
                    temperature=0.3,
                    p=0.95,
                    k=5
                )
            elif model_id.startswith('meta'):
                response = self.brt.invoke_model(
                    modelId=model_id,
                    body=json.dumps({
                        "prompt": prompt_input,
                        "max_gen_len": 10,
                        "temperature": 0.3,
                        "top_p": 0.95,
                        "top_k": 5
                    }),
                    contentType='application/json',
                    accept='application/json'
                )
            elif model_id.startswith('mistral'):
                response = self.brt.invoke_model(
                    modelId=model_id,
                    body=json.dumps({
                        "prompt": prompt_input,
                        "max_tokens": 512,
                        "temperature": 0.3,
                        "top_p": 0.95,
                        "top_k": 5
                    }),
                    contentType='application/json',
                    accept='application/json'
                )
            else:
                raise ValueError(f"Unsupported model: {model_id}")
        
            # print(f"Response received: {response}")  # Debug print
            return response
        except Exception as e:
            print(f"Error invoking model {model_id}: {str(e)}")
            return None

    def parse_response(self, model_id, prompt_input, wait_time):
        max_retries = 3
        backoff_factor = 5
        valid_scores = [-1, -0.5, 0, 0.5, 1]

        for attempt in range(max_retries):
            try:
                time.sleep(wait_time)
                response = self.invoke_model(model_id, prompt_input)
                completion = self.extract_completion(model_id, response)
                print(f"Completion: {completion}")

                # Extract the first two valid scores from the response
                scores = []
                parts = completion.replace(",", " ").split()
                for part in parts:
                    try:
                        score = float(part)
                        if score in valid_scores:
                            scores.append(score)
                            if len(scores) == 2:
                                break
                    except ValueError:
                        continue

                # Assign scores or default to empty string
                score1 = scores[0] if len(scores) > 0 else ""
                score2 = scores[1] if len(scores) > 1 else ""
                print(f"Score 1: {score1}, Score 2: {score2}")  # Debugging
                return score1, score2

            except Exception as e:
                wait_time = backoff_factor ** attempt
                print(f"Exception: {e}. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)

        raise ValueError(f"The model did not return a valid response after {max_retries} attempts.")

    def extract_completion(self, model_id, response):
        if model_id.startswith('anthropic'):
            response_body = json.loads(response['body'].read())
            return response_body['content'][0].get('text', '').strip()
        elif model_id.startswith('amazon.titan'):
            response_body = json.loads(response['body'].read())
            return response_body.get('results', [{}])[0].get('outputText', '').strip()
        elif model_id.startswith('cohere'):
            return response.text.strip()
        elif model_id.startswith('meta'):
            response_body = json.loads(response['body'].read())
            return response_body.get('generation', '').strip()
        elif model_id.startswith('mistral'):
            response_body = json.loads(response['body'].read())
            return response_body['outputs'][0]['text'].strip()
        else:
            raise ValueError(f"Unsupported model: {model_id}")

    def Claude35Sonnet(self, chapter):
        model_id = 'anthropic.claude-3-5-sonnet-20240620-v1:0'
        prompt_input = self.prompt(model_id, chapter)
        wait_time = 10
        return self.parse_response(model_id, prompt_input, wait_time)
    
    def TitanTextPremier(self, chapter):
        model_id = 'amazon.titan-text-premier-v1:0'
        prompt_input = self.prompt(model_id, chapter)
        wait_time = 0
        return self.parse_response(model_id, prompt_input, wait_time)
    
    def CohereCommandRPlus(self, chapter):
        model_id = 'cohere.command-r-plus-v1:0'
        prompt_input = self.prompt(model_id, chapter)
        wait_time = 2.5
        return self.parse_response(model_id, prompt_input, wait_time)
    
    def MetaLlama370B(self, chapter):
        model_id = 'meta.llama3-70b-instruct-v1:0'
        prompt_input = self.prompt(model_id, chapter)
        wait_time = 1
        return self.parse_response(model_id, prompt_input, wait_time)

    def MistralLarge2402(self, chapter):
        model_id = 'mistral.mistral-large-2402-v1:0'
        prompt_input = self.prompt(model_id, chapter)
        wait_time = 1
        return self.parse_response(model_id, prompt_input, wait_time)