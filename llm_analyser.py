import boto3
import json

class LLMAnalyser:
    def __init__(self):
        self.bedrock = boto3.client(service_name='bedrock-runtime')

    def analyse_text(self, text, model_id):
        prompt = f"""
    
Analyze the provided Beige Book chapter, focusing on five key economic metrics:
1. GDP (Gross Domestic Product)
2. Interest Rates
3. Inflation
4. Employment
5. Stock Market Performance (specifically SPX returns)
For each metric, provide:
1. A forecasting rating: 1 (likely to increase), -1 (likely to decrease), 0 (likely to remain stable)
2. A concise justification for the rating

Format your response as follows for each metric:
{{rating:justification}}

Critical Instructions:
- Your ratings should reflect definitive FORECASTS based on the information in the text, not current conditions.
- Provide a clear, unambiguous justification that aligns with the given rating. Avoid phrases like "likely to continue or remain stable" - choose one direction.
- Conduct a holistic analysis using ALL relevant information in the text, even if a specific metric isn't directly mentioned.
- Infer potential impacts on each metric based on related economic factors discussed in the text.
- A neutral (0) rating should only be given when there's a genuine balance of positive and negative factors, not due to lack of direct mention.
- Use economic reasoning to connect different aspects of the economy. For example, strong employment might suggest positive stock market performance.
- Base your analysis SOLELY on the information provided in the given text.
- Do NOT consider any external current, future, or past events, or known data about these metrics.
- Ensure justifications are concise yet informative, suitable for qualitative analysis.
- Maintain consistency in your analytical approach across all five metrics.

Here's the text to analyze:

"{text}"

Provide your analysis based solely on the information in this text.

"""

        body = json.dumps({
            "prompt": prompt,
            "max_tokens_to_sample": 1000,
            "temperature": 0.5,
            "top_p": 0.9,
        })

        response = self.bedrock.invoke_model(body=body, modelId=model_id)
        response_body = json.loads(response.get('body').read())
        
        # Parse the response and extract ratings and justifications
        analysis = {}
        lines = response_body.get('completion').strip().split('\n')
        metrics = ['gdp', 'interest_rate', 'inflation', 'employment', 'stock_market']
        for metric, line in zip(metrics, lines):
            rating, justification = line.split(':', 1)
            analysis[metric] = {'rating': int(rating.strip('{}')), 'justification': justification.strip()}
        
        return analysis

    def get_available_models(self):
        # This is a placeholder. You'll need to implement this based on 
        # how Amazon Bedrock provides model information.
        return ['anthropic.claude-v2', 'ai21.j2-ultra-v1', 'amazon.titan-text-express-v1']