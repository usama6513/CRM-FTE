import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# Gmail API scopes
SCOPES = [
    'https://www.googleapis.com/auth/gmail.modify',  # Read/write access to messages
    'https://www.googleapis.com/auth/gmail.send'     # Send emails
]

def get_gmail_credentials():
    """Get valid Gmail credentials and refresh token."""
    creds = None

    # The file token.pickle stores the user's access and refresh tokens
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    # If there are no (valid) credentials available, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Refreshing access token...")
            creds.refresh(Request())
        else:
            print("Please log in to your Gmail account...")
            print("A browser window will open for authentication.")
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    print("[SUCCESS] Authentication successful!")
    print(f"Access Token: {creds.token}")
    print(f"Refresh Token: {creds.refresh_token}")
    print(f"Token Expiry: {creds.expiry}")

    return creds.refresh_token

if __name__ == "__main__":
    print("Gmail API Token Generator")
    print("=" * 30)
    print("This script will help you generate a Gmail refresh token.")
    print("Make sure you have credentials.json in the same directory.")
    print("\nStarting authentication process...")

    try:
        refresh_token = get_gmail_credentials()

        print("\n" + "=" * 50)
        print("SUCCESS! Here is your refresh token:")
        print("=" * 50)
        print(f"Refresh Token: {refresh_token}")
        print("=" * 50)
        print("\nPlease update your .env file with this refresh token:")
        print("GMAIL_REFRESH_TOKEN=your_refresh_token_here")

        # Update the .env file automatically
        with open('.env', 'r') as file:
            env_content = file.read()

        # Replace the placeholder with the actual token
        env_content = env_content.replace(
            'GMAIL_REFRESH_TOKEN=your_gmail_refresh_token',
            f'GMAIL_REFRESH_TOKEN={refresh_token}'
        )

        with open('.env', 'w') as file:
            file.write(env_content)

        print("\n[SUCCESS] .env file has been automatically updated!")

    except Exception as e:
        print(f"\n[ERROR] Error occurred: {str(e)}")
        print("\nPlease make sure:")
        print("1. You have the correct credentials.json file")
        print("2. The Gmail API is enabled in Google Cloud Console")
        print("3. Your OAuth consent screen is properly configured")