import os
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# SSL workaround
os.environ['WDM_SSL_VERIFY'] = '0'

# Load test data
csv_path = r"C:\Users\F6CAF02\Documents\Project\parabank\Test_script\Signup_Test_Data.csv"
df = pd.read_csv(csv_path)

# Start Chrome driver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.maximize_window()

# Define form URL
url = "https://parabank.parasoft.com/parabank/register.htm"  # Change this to your actual sign-up form URL

# Field mapping (CSV column => HTML element ID)
field_ids = {
    "First Name": "customer.firstName",
    "Last Name": "customer.lastName",
    "Address": "customer.address.street",
    "City": "customer.address.city",
    "State": "customer.address.state",
    "Zip": "customer.address.zipCode",
    "Phone #": "customer.phoneNumber",
    "SSN": "customer.ssn",
    "Username": "customer.username",
    "Email / Username": "customer.username",
    "Password": "customer.password",
    "Confirm Password": "repeatedPassword"
}

# Function to clear and fill a form field
def fill_field(field_id, value):
    try:
        element = driver.find_element(By.ID, field_id)
        element.clear()
        if pd.notna(value):
            element.send_keys(str(value).strip())
    except:
        pass

# Store test results
test_results = []

# Iterate through each test case
for index, row in df.iterrows():
    test_name = row.get("Test Case", f"Test #{index+1}")
    expected = row.get("Expected Result", "").strip()

    print(f"\n🔹 Running: {test_name}")
    driver.get(url)
    time.sleep(1)

    # Fill in form fields
    for csv_field, html_id in field_ids.items():
        if csv_field in row:
            fill_field(html_id, row[csv_field])

    # Submit form
    try:
        submit_btn = driver.find_element(By.XPATH, "//input[@type='submit' and @value='Register']")
        submit_btn.click()
        time.sleep(1)
    except Exception as e:
        actual_result = f"Error submitting form: {str(e)}"
        status = "FAIL"
        test_results.append([test_name, expected, actual_result, status])
        continue

    # Collect error messages
    error_elements = driver.find_elements(By.CLASS_NAME, "error")
    error_texts = [e.text for e in error_elements if e.text.strip()]
    actual_result = "; ".join(error_texts) if error_texts else "Registration success"

    # Compare actual vs expected (basic contains check)
    if expected.lower() in actual_result.lower():
        status = "PASS"
    else:
        status = "FAIL"

    # Log result
    print(f"   ✅ Expected: {expected}")
    print(f"   📝 Actual: {actual_result}")
    print(f"   🧪 Result: {status}")

    test_results.append([test_name, expected, actual_result, status])

# Close browser
driver.quit()

# Save results to CSV
report_df = pd.DataFrame(test_results, columns=["Test Case", "Expected Result", "Actual Result", "Status"])
report_path = os.path.join(os.path.dirname(csv_path), "Signup_Test_Report.csv")
report_df.to_csv(report_path, index=False)

# Display summary
print("\n🧾 Test Summary:")
print(report_df.to_string(index=False))
print(f"\n📁 Detailed report saved to: {report_path}")