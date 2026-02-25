import os
import json
import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
GOOGLE_SHEET_ID = os.environ.get('GOOGLE_SHEET_ID')
CREDENTIALS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'google_sheets_creds.json')

def get_google_sheets_client():
    """Create and return Google Sheets API client"""
    try:
        if not os.path.exists(CREDENTIALS_PATH):
            print("❌ Credentials file not found at:", CREDENTIALS_PATH)
            return None
        
        scopes = ['https://www.googleapis.com/auth/spreadsheets']
        creds = Credentials.from_service_account_file(CREDENTIALS_PATH, scopes=scopes)
        client = gspread.authorize(creds)
        return client
    except Exception as e:
        print(f"❌ Error connecting to Google Sheets: {e}")
        return None

def clear_all_sheets():
    """Clear all data from Google Sheets (keep headers)"""
    client = get_google_sheets_client()
    if client is None:
        return
    
    try:
        spreadsheet = client.open_by_key(GOOGLE_SHEET_ID)
        print(f"Clearing data from Google Sheet: {GOOGLE_SHEET_ID}\n")
        
        # Get all worksheets
        worksheets = spreadsheet.worksheets()
        
        for worksheet in worksheets:
            sheet_name = worksheet.title
            print(f"Processing sheet: {sheet_name}")
            
            # Get all rows
            all_rows = worksheet.get_all_values()
            
            if len(all_rows) > 1:  # If there's more than just the header
                # Keep only the header row (first row)
                rows_to_delete = len(all_rows) - 1
                
                # Delete rows starting from row 2 (index 1)
                for i in range(rows_to_delete, 0, -1):
                    worksheet.delete_rows(2, 1)  # Delete row 2
                
                print(f"  ✓ Cleared {rows_to_delete} data rows (kept header)")
            else:
                print(f"  ✓ Already empty (only header)")
        
        print("\n✅ All sheets cleared successfully!")
    
    except Exception as e:
        print(f"❌ Error clearing sheets: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("Google Sheets Data Clearer")
    print("=" * 60)
    clear_all_sheets()
