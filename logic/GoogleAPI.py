import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from dotenv import load_dotenv
load_dotenv()

# Google sheet credentials
TOKEN_DIRECTORY_PATH = os.getenv('TOKEN_PATH')

# Scopes and credentials
GOOGLE_SHEET_SCOPE = [os.getenv('GOOGLE_SHEET_SCOPE')]
CREDENTIALS_FILE_PATH = os.getenv('CREDENTIALS_FILE_PATH')

# Get credentials from google cloud console
# Checks if user has a token already, if so proceed
# if not prompt user to sign in
# save token
def getCredentials():
    # Iniialize
    creds = None
    # Checks if token already exist
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', GOOGLE_SHEET_SCOPE)
    # Checks if credential are valid
    if not creds or not creds.valid:
        # Check if credential is expired and if have refresh token
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # No tokens exist (or can't be refreshed)
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', GOOGLE_SHEET_SCOPE)
            creds = flow.run_local_server(port=8888)
        
        # Saves credentials to token.json
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    return creds

# Get LOADINGCNTR Sheet from the GS
def getLOADINGCNTR():
    # get the credential from the function above
    creds = getCredentials()
    # This opens a connection to google sheets using creds
    service = build('sheets', 'v4', credentials=creds)
    
    # SGI Workorder sheet id
    spreadsheet_id = '1un4plhTwC_uPaLb2JLt2HCY8ILU7xC1Xd_lNhTo0LL8'
    # LOADINGCNTR is sheet name and column A to H - all rows
    range_name = 'LOADINGCNTR!A:H'
    # Returns a dict of data from GS
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id, 
        range=range_name
    ).execute()
    
    # Returns value key
    values = result.get('values', [])
    return values
