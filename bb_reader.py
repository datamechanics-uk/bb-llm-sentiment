import os

def read_national_summary(year, month):
    file_path = os.path.join('beige_books', str(year), f'{month:02d}', 'national_summary.txt')

    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    return content

# Test the function
content = read_national_summary(2010, 9)
if content:
    print(f"Content length: {len(content)} characters")
    print("First 100 characters:", content[:100])
else:
    print("No content retrieved")