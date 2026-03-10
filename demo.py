from dotenv import load_dotenv
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
load_dotenv()

from analyzer import analyze_code
from executor import extract_code_block, execute_code

code = """def calculate_average(numbers):
    total = 0
    for num in numbers:
        total += num
    
    return total / len(numbers)

scores = [85, 90, 92, "100"]
print('Average:', calculate_average(scores))

empty_list = []
print('Empty Average:', calculate_average(empty_list))"""


print("--- ANALYZING CODE ---")
result = analyze_code(code, 'Error Correction', 'Python')

print("--- EXTRACTING CORRECTED CODE ---")
extracted = extract_code_block(result, 'Python')
print(extracted)

print("\n--- RUNNING CORRECTED CODE ---")
print(execute_code(extracted, 'Python'))
