import boto3
import json
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modules.paths import Paths
from modules.write_csv import WriteCSV
paths = Paths()
csv_writer = WriteCSV()

brt = boto3.client(
    service_name='bedrock-runtime',
    region_name=os.environ.get('AWS_REGION'),
    aws_access_key_id=os.environ.get('AWS_ACCESS'),
    aws_secret_access_key=os.environ.get('AWS_SECRET')
)

def read_beige_book_text(year: str, month: str, district: str):
    base_path = os.path.join(paths.beige_books_raw_scraped(), year, month)
    file_path = os.path.join(base_path, f"{district}.txt")
    
    with open(file_path, 'r') as file:
        return file.read()

def analyse_text(text, district):
    prompt_input = f"""
Human: You are an expert financial analyst with years of experience in stock market prediction. Numerically classify the following text based on its impact on the Standard & Poor's 500 Index returns:

<text>
{text}
</text>

Categories are:
-1
-0.5
0
0.5
1

Where:
-1: Strongly negative impact
-0.5: Moderately negative impact
0: Neutral or uncertain impact
0.5: Moderately positive impact
1: Strongly positive impact

Do not provide any additional commentary or text.
Do not provide any justification.
Do not provide any explanations.

Assistant:
"""

    body = json.dumps({
        "prompt": f"{prompt_input}",
        "max_tokens_to_sample": 100,
        "temperature": 0.1,
        "top_p": 0.5,
    })

    modelId = 'anthropic.claude-v2'
    accept = 'application/json'
    contentType = 'application/json'

    response = brt.invoke_model(body=body, modelId=modelId, accept=accept, contentType=contentType)
    response_body = json.loads(response.get('body').read())
    score = response_body.get('completion')
    return district, score

def main():
    year = '2020'
    month = '01'
    
    base_path = os.path.join(paths.beige_books_raw_scraped(), year, month)
    results = [['District', 'SPX Impact']]  # Header row

    for filename in os.listdir(base_path):
        district = filename.split('.')[0]
        text = read_beige_book_text(year, month, district)
        result = analyse_text(text, district)
        results.append(result)
        print(f"Processed {district}")
                
    # Write results to CSV using WriteCSV
    csv_path = os.path.join(paths.data(), f'beige_book_analysis_{year}_{month}_all_districts.csv')
    csv_writer.write(csv_path, results)

    print(f"Analysis complete. Results saved to {csv_path}")

if __name__ == "__main__":
    main()