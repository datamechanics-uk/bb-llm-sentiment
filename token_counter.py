import os
import csv
import json
from tokencost import calculate_all_costs_and_tokens

model = "claude-3-5-sonnet-20240620"
prompt = [{"role": "user", "content": "Hello!"}]
completion = "How may I assist you today?"

print(f"{calculate_all_costs_and_tokens(model=model, prompt=prompt, completion=completion)}")