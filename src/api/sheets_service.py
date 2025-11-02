"""
sheets_service.py
Service layer to handle Google Sheets API interactions.
Reads configuration from environment variables and appends expense data to the specified Google Sheet.
"""

# import necessary libraries
import json
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build

# ---------------------------------------------------------------
# CONFIGURATION (Reads from Environment Variables)
# ---------------------------------------------------------------
# SPREADSHEET_ID is read from the Cloud Run environment
SPREADSHEET_ID = os.environ.get("SPREADSHEET_ID")
WORKSHEET_NAME = "Sheet1"  # For the first worksheet

# ---------------------------------------------------------------
# FUNCTION TO INITIALIZE GOOGLE SHEETS SERVICE
# ---------------------------------------------------------------
def get_sheets_service():
    # Get Google Sheets API service object
    creds_json = os.environ.get("GOOGLE_SHEETS_CREDENTIALS")

    # Critical check if configuration is missing
    if not SPREADSHEET_ID or not creds_json:
        # If either is missing, log an error and return None
        print("ERROR: SPREADSHEET_ID or GOOGLE_SHEETS_CREDENTIALS not set.")
        return None

    try:
        # Load credentials from the JSON string
        info = json.loads(creds_json)
        
        # Create credentials object with the necessary scopes
        creds = service_account.Credentials.from_service_account_info(
            info,
            scopes=['https://www.googleapis.com/auth/spreadsheets']
        )

        # Build the Sheets API service object
        service = build("sheets", "v4", credentials=creds)
        return service
    
    except Exception as e:
        print(f"Error initializing Sheets Service: {e}")
        return None

# ---------------------------------------------------------------
# FUNCTION TO EXECUTE LATEST ROW NO NUMBER
# ---------------------------------------------------------------
def get_latest_row_number():
    # Get the Sheets API service
    service = get_sheets_service()
    if not service:
        raise Exception("Sheets API Service is not available.")

    # No column is column A
    range_name = f'{WORKSHEET_NAME}!A:A'

    try:
        # Retrieve all values in column A
        result = service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=range_name
        ).execute()
        
        values = result.get('values', [])
        # Determine the latest row number
        if len(values) > 1:
            latest_number = int(values[-1][0]) # [0] is used to access the first index of the list
            return latest_number + 1
        else:
            return 1

    except Exception as e:
        raise Exception(f"Failed to retrieve latest row number: {e}")

# ---------------------------------------------------------------
# FUNCTION TO APPEND EXPENSE DATA
# ---------------------------------------------------------------      
def append_expense_row(product_name, amount, month):
    # Get the Sheets API service
    service = get_sheets_service()
    if not service:
        raise Exception("Sheets API Service is not available.")

    # Get the next row number
    next_row_no = get_latest_row_number()
    
    # Data structure for the row
    values = [
        [next_row_no, product_name, amount, month]  # No, Product Name, Amount, Month
    ]
    
    # Define the Sheets API parameters
    range_name = f'{WORKSHEET_NAME}!A:D'  # Columns A to D
    body = {'values': values}
    
    try:
        # Execute the append request
        service.spreadsheets().values().append(
            spreadsheetId=SPREADSHEET_ID,
            range=range_name,
            valueInputOption='USER_ENTERED',
            insertDataOption='INSERT_ROWS',
            body=body
        ).execute()
        
        return True
    
    except Exception as e:
        raise Exception(f"Failed to write data to Google Sheets: {e}")
