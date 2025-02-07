import os
import re

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

API_KEY = 'AIzaSyCgwXarrTCCjOA0PdDYqg4l5xXuC549k2c'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SAMPLE_SPREADSHEET_ID = '1Y8SoXADF2X9cE1d8bU8aKlZ70LyjnKhBbL7I24S1KnA'
SAMPLE_RANGE_NAME = 'Keywords!E2:E'
account_email = 'Dummy Account credentials!A2'
account_pass = 'Dummy Account credentials!B2'
sample_write = 'Sheet8!A1:C4'
def get_keyword():
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    try:
        service = build('sheets', 'v4', developerKey=API_KEY, credentials=creds)

        # Call the Sheets API
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                    range=SAMPLE_RANGE_NAME).execute()
        values = result.get('values', [])
        for value in values:
            keywords.append(re.sub(r"[^a-zA-Z0-9- ]", "", str(value)))

        if not values:
            print('No data found.')
            return

    except HttpError as err:
        print(err)

def get_creds():
    try:
        service = build('sheets', 'v4', developerKey=API_KEY, credentials=creds)

        # Call the Sheets API
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                    range=account_email).execute()
        result2 = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                    range=account_pass).execute()
        values = result.get('values', [])
        values2 = result2.get('values', [])
        for value in values:
            creds.append(re.sub(r"[\[\]'\"']", "", str(value)))

        if not values:
            print('No data found.')
            return

        for value in values2:
            creds.append(re.sub(r"[\[\]'\"']", "", str(value)))

        if not values:
            print('No data found.')
            return

    except HttpError as err:
        print(err)

def write_data():
    try:
        service = build('sheets', 'v4', developerKey=API_KEY, credentials=creds)

        range_name = "OS MAIN"  # Replace this with the sheet name and range you want to write to

        # Retrieve the current values in the sheet
        result = service.spreadsheets().values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range=range_name).execute()
        values = result.get('values', [])

        if not values:
            print('No data found.')
            return

        # Calculate the next row to write to
        next_row = len(values) + 1

        # Prepare the data to write
        data = [
            ["RACS", "RACS", "CXM", "", "May", "29-May-23", "05/31/2023", "Facebook", "Ephe Martinez", "facebook.com", "Mobile Postpaid", "testestest tesetsets"]
        ]
        values_to_write = data

        # Write the data to the sheet
        body = {'values': values_to_write}
        try:
            service.spreadsheets().values().update(
                spreadsheetId=SAMPLE_SPREADSHEET_ID,
                range=f"{range_name}!A{next_row}",
                valueInputOption='RAW',
                body=body
            ).execute()
            print('Data successfully written to the sheet.')
        except HttpError as error:
            print(f'An error occurred: {error}')

    except HttpError as err:
        print(err)


if __name__ == '__main__':
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    keywords = []
    creds_data = []
    get_keyword()
    # get_creds()
    # write_data()
    print(keywords)
    print(creds)