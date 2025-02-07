import os
import pickle
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# ...

SCOPES = ['https://www.googleapis.com/auth/gmail.send']
creds = None

# ...

def send_email(subject, body):
    sender_email = 'online-scanning@online-scanning-test.iam.gserviceaccount.com'
    receiver_email = 'monicabcho@gmail.com'
    cc_email = 'jmmabatas@gmail.com'

    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = receiver_email
    message['Cc'] = cc_email
    message['Subject'] = subject

    message.attach(MIMEText(body, 'plain'))
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

    try:
        service = build('gmail', 'v1', credentials=creds)
        message = service.users().messages().send(userId='me', body={'raw': raw_message}).execute()
        print("Email notification sent successfully!")
    except Exception as e:
        print("Failed to send email notification:", str(e))

# ...

if __name__ == "__main__":
    # Authenticate with Gmail API
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    try:
        # Your existing code here

    except Exception as e:
        # Handle exceptions and send email notification
        error_message = f"Error occurred: {str(e)}"
        print(error_message)
        send_email("Code Exception Notification", error_message)
