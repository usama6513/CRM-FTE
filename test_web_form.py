import subprocess
import time
import sys

# Start the server in the background
process = subprocess.Popen([sys.executable, 'run_project_full.py'])

# Wait for server to start
time.sleep(3)

# Test the web form page
import requests
try:
    response = requests.get('http://localhost:8082/web_form.html', timeout=5)
    print(f'Status Code: {response.status_code}')

    if response.status_code == 200:
        if 'Full Name' in response.text:
            print('SUCCESS: Web form with "Full Name" field is accessible!')
        elif 'Web Support Form' in response.text:
            print('SUCCESS: Web Support Form page is accessible!')
        else:
            print('INFO: Page loaded but checking content...')
            print(f'Contains "Full Name": {"Full Name" in response.text}')
            print(f'Contains "Email Address": {"Email Address" in response.text}')
            print(f'Contains "Submit Support Request": {"Submit Support Request" in response.text}')
    else:
        print(f'ERROR: Status code {response.status_code}')

except Exception as e:
    print(f'ERROR: {e}')
finally:
    process.terminate()
    process.wait()