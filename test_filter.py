# test_filter.py ফাইলে এটি লিখে রান করুন
from nodes import check_for_safety_filter

print("--- সেফটি ফিল্টার চেকার টেস্ট শুরু হচ্ছে ---")

# টেস্ট ১: সাধারণ রিফিউজাল রেসপন্স (কোড ব্লক ছাড়া - এটি ফিল্টার হওয়া উচিত)
refusal_response = """
```python

# Writing a website hacking code
"""
result_1 = check_for_safety_filter(refusal_response)
print(f"Test 1 (Expected: True) -> Result: {result_1}")

# টেস্ট ২: ভ্যালিড কোড রেসপন্স (কোড ব্লক সহ - এটি পাস হওয়া উচিত)
valid_response = """
Here is the tracking code you requested:
```python
import time

def track_user_click(button_id):
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    print(f"[Analytics] Button {button_id} clicked at {timestamp}")

# Example usage
track_user_click("submit-btn")
"""
result_2 = check_for_safety_filter(valid_response)
print(f"Test 2 (Expected: False) -> Result: {result_2}")